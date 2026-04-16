import taichi as ti
import taichi.math as tm

ti.init(arch=ti.gpu)

# ================================================================
# CompareShadow.py
#   左半：基础 Phong
#   右半：Phong + Hard Shadow
# ================================================================

W, H    = 1400, 800
HALF_W  = W // 2
HA      = HALF_W / H          # half-aspect ≈ 0.875

pixels = ti.Vector.field(3, dtype=ti.f32, shape=(W, H))

EPS         = 1e-4
INF         = 1e9
SHADOW_BIAS = 2e-3

# ── 相机 ───────────────────────────────────────────────────────
# 相机在 z=6，看向 z=0 平面；y=1.6 稍微俯视
CAM_X, CAM_Y, CAM_Z = 0.0, 1.6, 6.0
VIEW_SCALE = 2.4          # 控制视野大小，px ∈ [-HA*VS, +HA*VS]
                           # 实际 px_max = 0.875*2.4 ≈ ±2.1

# ── 默认光源 ───────────────────────────────────────────────────
# 左上前方照过来，影子往右后方投，在地面很容易看到
DEF_LX, DEF_LY, DEF_LZ = -3.2, 5.5, 3.0

# ── 地面 ───────────────────────────────────────────────────────
GROUND_Y = -1.0

# ── 球（左侧）─────────────────────────────────────────────────
# x=-1.2，确保在视野内（px_max≈2.1，投影≈-1.2 ✓）
SPH_X, SPH_Y, SPH_Z = -1.2, -0.1, 0.0
SPH_R                = 0.9

# ── 圆锥（右侧）───────────────────────────────────────────────
# 顶点在上方，底面圆刚好落在地面 y=GROUND_Y
# x=+1.4，同样在视野内（投影≈1.4 ✓）
CONE_AX, CONE_AY, CONE_AZ = 1.4, 1.8, 0.0    # 顶点坐标
CONE_BASE_Y                = GROUND_Y          # 底面 y
CONE_R                     = 0.8               # 底面半径
CONE_H  = CONE_AY - CONE_BASE_Y              # = 2.8
CONE_K  = CONE_R  / CONE_H
CONE_K2 = CONE_K  * CONE_K

# ── 颜色 ───────────────────────────────────────────────────────
BG_R,   BG_G,   BG_B   = 0.04, 0.06, 0.10
SPH_CR, SPH_CG, SPH_CB = 0.90, 0.15, 0.12
CON_CR, CON_CG, CON_CB = 0.58, 0.18, 0.90


# ================================================================
# 求交函数
# ================================================================

@ti.func
def isect_sphere(ro: tm.vec3, rd: tm.vec3) -> ti.f32:
    c  = tm.vec3(SPH_X, SPH_Y, SPH_Z)
    oc = ro - c
    b  = 2.0 * oc.dot(rd)
    cc = oc.dot(oc) - SPH_R * SPH_R
    d  = b * b - 4.0 * cc
    t  = INF
    if d >= 0.0:
        sq = ti.sqrt(d)
        t1 = (-b - sq) * 0.5
        t2 = (-b + sq) * 0.5
        if t1 > EPS:
            t = t1
        elif t2 > EPS:
            t = t2
    return t


@ti.func
def normal_sphere(p: tm.vec3) -> tm.vec3:
    return (p - tm.vec3(SPH_X, SPH_Y, SPH_Z)).normalized()


@ti.func
def isect_cone(ro: tm.vec3, rd: tm.vec3):
    """返回 (t, hit_part)，hit_part: 0=未命中, 1=侧面, 2=底面"""
    apex = tm.vec3(CONE_AX, CONE_AY, CONE_AZ)
    rel  = ro - apex

    # 隐式方程：(x-ax)^2 + (z-az)^2 - K2*(y-ay)^2 = 0
    a = rd.x*rd.x + rd.z*rd.z - CONE_K2*rd.y*rd.y
    b = 2.0*(rel.x*rd.x + rel.z*rd.z - CONE_K2*rel.y*rd.y)
    c = rel.x*rel.x + rel.z*rel.z - CONE_K2*rel.y*rel.y

    t_best   = INF
    hit_part = 0

    if ti.abs(a) > 1e-8:
        d = b*b - 4.0*a*c
        if d >= 0.0:
            sq = ti.sqrt(d)
            t1 = (-b - sq) / (2.0*a)
            t2 = (-b + sq) / (2.0*a)

            if t1 > EPS:
                hp  = ro + t1*rd
                wy  = hp.y - CONE_AY       # 相对顶点 y，范围 [-CONE_H, 0]
                if -CONE_H <= wy <= 0.0:
                    t_best   = t1
                    hit_part = 1

            if t2 > EPS and t2 < t_best:
                hp  = ro + t2*rd
                wy  = hp.y - CONE_AY
                if -CONE_H <= wy <= 0.0:
                    t_best   = t2
                    hit_part = 1

    elif ti.abs(b) > 1e-8:
        tl = -c / b
        if tl > EPS:
            hp  = ro + tl*rd
            wy  = hp.y - CONE_AY
            if -CONE_H <= wy <= 0.0:
                t_best   = tl
                hit_part = 1

    # 底面圆盘
    if ti.abs(rd.y) > 1e-8:
        tb = (CONE_BASE_Y - ro.y) / rd.y
        if tb > EPS and tb < t_best:
            pb = ro + tb*rd
            dx = pb.x - CONE_AX
            dz = pb.z - CONE_AZ
            if dx*dx + dz*dz <= CONE_R*CONE_R:
                t_best   = tb
                hit_part = 2

    return t_best, hit_part


@ti.func
def normal_cone(p: tm.vec3, hit_part: ti.i32) -> tm.vec3:
    n = tm.vec3(0.0, 0.0, 0.0)
    if hit_part == 2:
        n = tm.vec3(0.0, -1.0, 0.0)
    else:
        local = p - tm.vec3(CONE_AX, CONE_AY, CONE_AZ)
        n = tm.vec3(local.x, -CONE_K2*local.y, local.z).normalized()
    return n


@ti.func
def isect_ground(ro: tm.vec3, rd: tm.vec3) -> ti.f32:
    t = INF
    if ti.abs(rd.y) > 1e-8:
        tp = (GROUND_Y - ro.y) / rd.y
        if tp > EPS:
            t = tp
    return t


@ti.func
def ground_color(p: tm.vec3) -> tm.vec3:
    sc = 0.5
    ix = ti.cast(ti.floor((p.x + 20.0)*sc), ti.i32)
    iz = ti.cast(ti.floor((p.z + 20.0)*sc), ti.i32)
    c  = tm.vec3(0.0, 0.0, 0.0)
    if (ix + iz) % 2 == 0:
        c = tm.vec3(0.78, 0.78, 0.78)
    else:
        c = tm.vec3(0.55, 0.55, 0.55)
    return c


# ================================================================
# 场景求交（返回最近命中）
# ================================================================

@ti.func
def scene_hit(ro: tm.vec3, rd: tm.vec3):
    """返回 (t, obj_id, cone_part)
       obj_id: 0=无  1=球  2=圆锥  3=地面
    """
    t    = INF
    obj  = 0
    part = 0

    ts = isect_sphere(ro, rd)
    if ts < t:
        t = ts; obj = 1

    tc, cp = isect_cone(ro, rd)
    if tc < t:
        t = tc; obj = 2; part = cp

    tg = isect_ground(ro, rd)
    if tg < t:
        t = tg; obj = 3; part = 0

    return t, obj, part


# ================================================================
# 阴影检测
# ================================================================

@ti.func
def in_shadow(pos: tm.vec3, nrm: tm.vec3, lpos: tm.vec3) -> ti.i32:
    to_l  = lpos - pos
    ldist = to_l.norm()
    ldir  = to_l / ldist
    dot   = nrm.dot(ldir)
    bias  = tm.vec3(0.0, 0.0, 0.0)
    if dot >= 0.0:
        bias = nrm * SHADOW_BIAS
    else:
        bias = nrm * (-SHADOW_BIAS)
    ro = pos + bias
    t, obj, _ = scene_hit(ro, ldir)
    result = 0
    if obj != 0 and t > EPS and t < ldist - SHADOW_BIAS:
        result = 1
    return result


# ================================================================
# Phong 着色
# ================================================================

@ti.func
def phong(pos: tm.vec3, nrm: tm.vec3, col: tm.vec3,
          lpos: tm.vec3,
          ka: ti.f32, kd: ti.f32, ks: ti.f32, sh: ti.f32,
          use_shadow: ti.i32) -> tm.vec3:
    cam    = tm.vec3(CAM_X, CAM_Y, CAM_Z)
    N      = nrm.normalized()
    L      = (lpos - pos).normalized()
    V      = (cam  - pos).normalized()

    ambient = ka * col
    result  = ambient

    blocked = 0
    if use_shadow == 1:
        blocked = in_shadow(pos, N, lpos)

    if blocked == 0:
        ndl = ti.max(N.dot(L), 0.0)
        dif = kd * ndl * col
        R   = (2.0 * N.dot(L) * N - L).normalized()
        rv  = ti.max(R.dot(V), 0.0)
        spc = tm.vec3(ks * ti.pow(rv, sh),
                      ks * ti.pow(rv, sh),
                      ks * ti.pow(rv, sh))
        result = ambient + dif + spc

    return tm.clamp(result, 0.0, 1.0)


# ================================================================
# 单像素追踪
# ================================================================

@ti.func
def trace(local_i: ti.i32, j: ti.i32,
          lpos: tm.vec3,
          ka: ti.f32, kd: ti.f32, ks: ti.f32, sh: ti.f32,
          use_shadow: ti.i32) -> tm.vec3:

    bg = tm.vec3(BG_R, BG_G, BG_B)

    # 生成射线
    # j=0 在 Taichi 画布底部 → py 应为负（场景下方），j=H 时为正（场景上方）
    px  = (2.0 * (local_i + 0.5) / HALF_W - 1.0) * HA         * VIEW_SCALE
    py  = (2.0 * (j         + 0.5) / H     - 1.0) * VIEW_SCALE
    cam = tm.vec3(CAM_X, CAM_Y, CAM_Z)
    rd  = (tm.vec3(px, py, 0.0) - cam).normalized()

    t, obj, part = scene_hit(cam, rd)

    color = bg
    if obj != 0:
        p = cam + t * rd

        if obj == 1:
            n     = normal_sphere(p)
            color = phong(p, n,
                          tm.vec3(SPH_CR, SPH_CG, SPH_CB),
                          lpos, ka, kd, ks, sh, use_shadow)

        elif obj == 2:
            n     = normal_cone(p, part)
            color = phong(p, n,
                          tm.vec3(CON_CR, CON_CG, CON_CB),
                          lpos, ka, kd, ks, sh, use_shadow)

        elif obj == 3:
            n     = tm.vec3(0.0, 1.0, 0.0)
            gc    = ground_color(p)
            # 地面：高漫反射、低镜面，便于看清阴影
            color = phong(p, n, gc,
                          lpos, 0.10, 0.90, 0.05, 8.0, use_shadow)

    return color


# ================================================================
# 渲染核心（一次画完整张图）
# ================================================================

@ti.kernel
def render(lx: ti.f32, ly: ti.f32, lz: ti.f32,
           ka: ti.f32, kd: ti.f32, ks: ti.f32, sh: ti.f32):
    lpos = tm.vec3(lx, ly, lz)
    sep  = tm.vec3(0.95, 0.95, 0.95)

    for i, j in pixels:
        # 中间分割线（2px 宽）
        if i == HALF_W or i == HALF_W - 1:
            pixels[i, j] = sep
        elif i < HALF_W:
            # 左：基础 Phong（无阴影）
            pixels[i, j] = trace(i,          j, lpos, ka, kd, ks, sh, 0)
        else:
            # 右：Phong + Hard Shadow
            pixels[i, j] = trace(i - HALF_W, j, lpos, ka, kd, ks, sh, 1)


# ================================================================
# 主循环
# ================================================================

def main():
    win    = ti.ui.Window(
        "Left: Phong  |  Right: Phong + Hard Shadow",
        (W, H), vsync=True
    )
    canvas = win.get_canvas()

    lx, ly, lz         = DEF_LX, DEF_LY, DEF_LZ
    ka, kd, ks, sh      = 0.15, 0.75, 0.40, 32.0

    while win.running:
        gui = win.get_gui()
        with gui.sub_window("Controls", 0.02, 0.02, 0.30, 0.32) as g:
            g.text("Left: Phong  |  Right: + Shadow")
            lx = g.slider_float("Light X", lx, -7.0, 3.0)
            ly = g.slider_float("Light Y", ly,  1.5, 9.0)
            lz = g.slider_float("Light Z", lz, -1.0, 7.0)
            ka = g.slider_float("Ka",      ka,  0.0, 0.5)
            kd = g.slider_float("Kd",      kd,  0.0, 1.0)
            ks = g.slider_float("Ks",      ks,  0.0, 1.0)
            sh = g.slider_float("Shininess", sh, 1.0, 128.0)

        render(lx, ly, lz, ka, kd, ks, sh)
        canvas.set_image(pixels)
        win.show()


if __name__ == "__main__":
    main()