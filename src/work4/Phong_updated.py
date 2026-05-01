import taichi as ti
import taichi.math as tm

# 如果你的机器 GPU / Vulkan 后端有问题，
# 把 ti.gpu 改成 ti.cpu 先跑通再说。
ti.init(arch=ti.gpu)

W, H = 960, 640
ASPECT = W / H
VIEW_SCALE = 1.8
EPS = 1e-4
INF = 1e8

pixels = ti.Vector.field(3, dtype=ti.f32, shape=(W, H))

# ----------------------------
# 场景常量
# ----------------------------

# Camera
CAM_X, CAM_Y, CAM_Z = 0.0, 0.0, 5.0

# Light
LIGHT_X, LIGHT_Y, LIGHT_Z = 2.0, 3.0, 4.0

# Sphere: center (-1.2, -0.2, 0), radius 1.2
SPHERE_CX, SPHERE_CY, SPHERE_CZ = -1.2, -0.2, 0.0
SPHERE_R = 1.2

# Cone:
# apex (1.2, 1.2, 0)
# base plane y = -1.4
# base radius = 1.2
APEX_X, APEX_Y, APEX_Z = 1.2, 1.2, 0.0
BASE_Y = -1.4
CONE_R = 1.2
CONE_H = APEX_Y - BASE_Y  # 2.6
K = CONE_R / CONE_H
K2 = K * K

# Colors
BG_R, BG_G, BG_B = 0.03, 0.18, 0.18          # 深青色背景
SPHERE_CR, SPHERE_CG, SPHERE_CB = 0.8, 0.1, 0.1
CONE_CR, CONE_CG, CONE_CB = 0.6, 0.2, 0.8


@ti.func
def sphere_center():
    return tm.vec3(SPHERE_CX, SPHERE_CY, SPHERE_CZ)


@ti.func
def cone_apex():
    return tm.vec3(APEX_X, APEX_Y, APEX_Z)


@ti.func
def cam_pos():
    return tm.vec3(CAM_X, CAM_Y, CAM_Z)


@ti.func
def light_pos():
    return tm.vec3(LIGHT_X, LIGHT_Y, LIGHT_Z)


@ti.func
def intersect_sphere(ro, rd):
    """
    返回射线与球的最近正交点距离 t
    若未命中，则返回 INF
    """
    c = sphere_center()
    oc = ro - c

    # rd 已归一化，因此 a = 1
    b = 2.0 * oc.dot(rd)
    cc = oc.dot(oc) - SPHERE_R * SPHERE_R
    disc = b * b - 4.0 * cc

    best_t = INF
    if disc >= 0.0:
        sqrt_disc = ti.sqrt(disc)
        t1 = (-b - sqrt_disc) * 0.5
        t2 = (-b + sqrt_disc) * 0.5

        if t1 > EPS:
            best_t = t1
        if t2 > EPS and t2 < best_t:
            best_t = t2

    return best_t


@ti.func
def sphere_normal(p):
    return (p - sphere_center()).normalized()


@ti.func
def intersect_cone(ro, rd):
    """
    有限圆锥（含底面）求交
    返回:
      best_t   : 最近正交点距离
      hit_part : 0 = 未击中, 1 = 锥侧面, 2 = 锥底面
    """
    apex = cone_apex()
    rel = ro - apex

    best_t = INF
    hit_part = 0

    # ---------------------------------
    # 1) 与圆锥侧面求交
    #
    # 局部坐标下，圆锥侧面满足：
    # x^2 + z^2 - k^2 y^2 = 0
    # 其中 y ∈ [-h, 0]
    # apex 在局部原点，向下为负 y
    # ---------------------------------
    a = rd.x * rd.x + rd.z * rd.z - K2 * rd.y * rd.y
    b = 2.0 * (rel.x * rd.x + rel.z * rd.z - K2 * rel.y * rd.y)
    c = rel.x * rel.x + rel.z * rel.z - K2 * rel.y * rel.y

    if ti.abs(a) > 1e-6:
        disc = b * b - 4.0 * a * c
        if disc >= 0.0:
            sqrt_disc = ti.sqrt(disc)
            t1 = (-b - sqrt_disc) / (2.0 * a)
            t2 = (-b + sqrt_disc) / (2.0 * a)

            if t1 > EPS:
                p1 = ro + t1 * rd
                y1 = p1.y - APEX_Y
                if y1 >= -CONE_H and y1 <= 0.0:
                    best_t = t1
                    hit_part = 1

            if t2 > EPS and t2 < best_t:
                p2 = ro + t2 * rd
                y2 = p2.y - APEX_Y
                if y2 >= -CONE_H and y2 <= 0.0:
                    best_t = t2
                    hit_part = 1

    elif ti.abs(b) > 1e-6:
        # 退化成线性情况，做个兜底
        t_lin = -c / b
        if t_lin > EPS:
            p = ro + t_lin * rd
            y_local = p.y - APEX_Y
            if y_local >= -CONE_H and y_local <= 0.0:
                best_t = t_lin
                hit_part = 1

    # ---------------------------------
    # 2) 与圆锥底面圆盘求交
    # base plane: y = BASE_Y
    # ---------------------------------
    if ti.abs(rd.y) > 1e-6:
        tb = (BASE_Y - ro.y) / rd.y
        if tb > EPS and tb < best_t:
            pb = ro + tb * rd
            dx = pb.x - APEX_X
            dz = pb.z - APEX_Z
            if dx * dx + dz * dz <= CONE_R * CONE_R:
                best_t = tb
                hit_part = 2

    return best_t, hit_part


@ti.func
def cone_normal(p, hit_part):
    # debug:Taichi 不支持在非静态 if 内直接 return
    # 所以先计算结果，最后统一返回
    n = tm.vec3(0.0, 0.0, 0.0)

    if hit_part == 2:
        # 底面外法向量（向下）
        n = tm.vec3(0.0, -1.0, 0.0)
    else:
        # 侧面法向量来自隐式函数梯度
        # F(x, y, z) = x^2 + z^2 - k^2 y^2
        # ∇F = (2x, -2k^2 y, 2z)
        local = p - cone_apex()
        n = tm.vec3(local.x, -K2 * local.y, local.z).normalized()

    return n


@ti.func
def phong_shade(pos, normal, obj_color, ka, kd, ks, shininess):
    light_color = tm.vec3(1.0, 1.0, 1.0)

    N = normal.normalized()
    L = (light_pos() - pos).normalized()
    V = (cam_pos() - pos).normalized()

    ambient = ka * light_color * obj_color

    ndotl = ti.max(N.dot(L), 0.0)
    diffuse = kd * ndotl * light_color * obj_color

    specular = tm.vec3(0.0, 0.0, 0.0)
    if ndotl > 0.0:
        # R = 2(N·L)N - L
        R = (2.0 * N.dot(L) * N - L).normalized()
        spec = ti.pow(ti.max(R.dot(V), 0.0), shininess)
        specular = ks * spec * light_color

    color = ambient + diffuse + specular
    return tm.clamp(color, 0.0, 1.0)


@ti.kernel
def render(ka: ti.f32, kd: ti.f32, ks: ti.f32, shininess: ti.f32):
    bg = tm.vec3(BG_R, BG_G, BG_B)
    sphere_color = tm.vec3(SPHERE_CR, SPHERE_CG, SPHERE_CB)
    cone_color = tm.vec3(CONE_CR, CONE_CG, CONE_CB)
    camera = cam_pos()

    for i, j in pixels:
        # 屏幕像素 -> 视平面 z = 0
        px = (2.0 * ((i + 0.5) / W) - 1.0) * ASPECT * VIEW_SCALE
        py = (1.0 - 2.0 * ((j + 0.5) / H)) * VIEW_SCALE
        image_point = tm.vec3(px, py, 0.0)

        ro = camera
        rd = (image_point - ro).normalized()

        best_t = INF
        best_obj = 0      # 0=none, 1=sphere, 2=cone
        cone_part = 0

        # 与球求交
        t_s = intersect_sphere(ro, rd)
        if t_s < best_t:
            best_t = t_s
            best_obj = 1

        # 与圆锥求交
        t_c, hit_part = intersect_cone(ro, rd)
        if t_c < best_t:
            best_t = t_c
            best_obj = 2
            cone_part = hit_part

        if best_obj == 0:
            pixels[i, j] = bg
        else:
            hit_pos = ro + best_t * rd

            if best_obj == 1:
                N = sphere_normal(hit_pos)
                color = phong_shade(hit_pos, N, sphere_color, ka, kd, ks, shininess)
                pixels[i, j] = color
            else:
                N = cone_normal(hit_pos, cone_part)
                color = phong_shade(hit_pos, N, cone_color, ka, kd, ks, shininess)
                pixels[i, j] = color


def main():
    window = ti.ui.Window("Experiment 4 - Phong Lighting", (W, H), vsync=True)
    canvas = window.get_canvas()

    ka = 0.2
    kd = 0.7
    ks = 0.5
    shininess = 32.0

    while window.running:
        gui = window.get_gui()
        with gui.sub_window("Phong Parameters", 0.02, 0.02, 0.30, 0.24) as g:
            g.text("Local illumination: Ambient + Diffuse + Specular")
            ka = g.slider_float("Ka", ka, 0.0, 1.0)
            kd = g.slider_float("Kd", kd, 0.0, 1.0)
            ks = g.slider_float("Ks", ks, 0.0, 1.0)
            shininess = g.slider_float("Shininess", shininess, 1.0, 128.0)
            g.text(f"Ka = {ka:.2f}")
            g.text(f"Kd = {kd:.2f}")
            g.text(f"Ks = {ks:.2f}")
            g.text(f"Shininess = {shininess:.1f}")

        render(ka, kd, ks, shininess)
        canvas.set_image(pixels)
        window.show()


if __name__ == "__main__":
    main()