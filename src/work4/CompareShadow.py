import taichi as ti
import taichi.math as tm

ti.init(arch=ti.gpu)

W, H = 1200, 600
HALF_W = W // 2
pixels = ti.Vector.field(3, dtype=ti.f32, shape=(W, H))

EPS = 1e-4
INF = 1e9
SHADOW_BIAS = 2e-3

# ----------------------------
# 场景参数
# ----------------------------
CAMERA = tm.vec3(0.0, 0.0, 5.0)

SPHERE_CENTER = tm.vec3(-1.2, -0.2, 0.0)
SPHERE_RADIUS = 1.2
SPHERE_COLOR = tm.vec3(0.8, 0.1, 0.1)

CONE_APEX = tm.vec3(1.2, 1.2, 0.0)
CONE_BASE_Y = -1.4
CONE_RADIUS = 1.2
CONE_HEIGHT = CONE_APEX.y - CONE_BASE_Y
CONE_K = CONE_RADIUS / CONE_HEIGHT
CONE_K2 = CONE_K * CONE_K
CONE_COLOR = tm.vec3(0.6, 0.2, 0.8)

GROUND_Y = -1.55
BACKGROUND = tm.vec3(0.05, 0.15, 0.15)


@ti.func
def normalize(v):
    return v / v.norm(1e-6)


@ti.func
def reflect_dir(I, N):
    return I - 2.0 * I.dot(N) * N


# ----------------------------
# 几何求交
# ----------------------------
@ti.func
def intersect_sphere(ro, rd):
    t = INF
    oc = ro - SPHERE_CENTER
    b = 2.0 * oc.dot(rd)
    c = oc.dot(oc) - SPHERE_RADIUS * SPHERE_RADIUS
    delta = b * b - 4.0 * c

    if delta >= 0.0:
        sqrt_delta = ti.sqrt(delta)
        t1 = (-b - sqrt_delta) * 0.5
        t2 = (-b + sqrt_delta) * 0.5

        if t1 > EPS:
            t = t1
        elif t2 > EPS:
            t = t2

    return t


@ti.func
def sphere_normal(p):
    return normalize(p - SPHERE_CENTER)


@ti.func
def intersect_cone(ro, rd):
    t_best = INF
    hit_part = 0
    rel = ro - CONE_APEX

    a = rd.x * rd.x + rd.z * rd.z - CONE_K2 * rd.y * rd.y
    b = 2.0 * (rel.x * rd.x + rel.z * rd.z - CONE_K2 * rel.y * rd.y)
    c = rel.x * rel.x + rel.z * rel.z - CONE_K2 * rel.y * rel.y

    if ti.abs(a) > 1e-6:
        delta = b * b - 4.0 * a * c
        if delta >= 0.0:
            sqrt_delta = ti.sqrt(delta)
            t1 = (-b - sqrt_delta) / (2.0 * a)
            t2 = (-b + sqrt_delta) / (2.0 * a)

            if t1 > EPS:
                p1 = ro + t1 * rd
                y1 = p1.y - CONE_APEX.y
                if -CONE_HEIGHT <= y1 <= 0.0:
                    t_best = t1
                    hit_part = 1

            if t2 > EPS and t2 < t_best:
                p2 = ro + t2 * rd
                y2 = p2.y - CONE_APEX.y
                if -CONE_HEIGHT <= y2 <= 0.0:
                    t_best = t2
                    hit_part = 1

    if ti.abs(rd.y) > 1e-6:
        tb = (CONE_BASE_Y - ro.y) / rd.y
        if tb > EPS and tb < t_best:
            pb = ro + tb * rd
            dx = pb.x - CONE_APEX.x
            dz = pb.z - CONE_APEX.z
            if dx * dx + dz * dz <= CONE_RADIUS * CONE_RADIUS:
                t_best = tb
                hit_part = 2

    return t_best, hit_part


@ti.func
def cone_normal(p, hit_part):
    n = tm.vec3(0.0, 0.0, 0.0)

    if hit_part == 2:
        n = tm.vec3(0.0, -1.0, 0.0)
    else:
        local = p - CONE_APEX
        n = normalize(tm.vec3(local.x, -CONE_K2 * local.y, local.z))

    return n


@ti.func
def intersect_ground(ro, rd):
    t = INF

    if ti.abs(rd.y) > 1e-6:
        tg = (GROUND_Y - ro.y) / rd.y
        if tg > EPS:
            t = tg

    return t


@ti.func
def ground_color(p):
    ix = ti.cast(ti.floor((p.x + 20.0) * 0.6), ti.i32)
    iz = ti.cast(ti.floor((p.z + 20.0) * 0.6), ti.i32)

    c = tm.vec3(0.0, 0.0, 0.0)
    if (ix + iz) % 2 == 0:
        c = tm.vec3(0.78, 0.78, 0.78)
    else:
        c = tm.vec3(0.55, 0.55, 0.55)

    return c


@ti.func
def scene_hit(ro, rd):
    t_min = INF
    obj_id = 0
    cone_part = 0

    t_s = intersect_sphere(ro, rd)
    if t_s < t_min:
        t_min = t_s
        obj_id = 1

    t_c, part = intersect_cone(ro, rd)
    if t_c < t_min:
        t_min = t_c
        obj_id = 2
        cone_part = part

    t_g = intersect_ground(ro, rd)
    if t_g < t_min:
        t_min = t_g
        obj_id = 3
        cone_part = 0

    return t_min, obj_id, cone_part


# ----------------------------
# 阴影逻辑
# ----------------------------
@ti.func
def offset_ray_origin(pos, normal, direction):
    out = pos
    if normal.dot(direction) >= 0.0:
        out = pos + normal * SHADOW_BIAS
    else:
        out = pos - normal * SHADOW_BIAS
    return out


@ti.func
def in_shadow(pos, normal, light_pos):
    to_light = light_pos - pos
    dist = to_light.norm()
    Ldir = normalize(to_light)

    shadow_ro = offset_ray_origin(pos, normal, Ldir)
    t_hit, obj_id, _ = scene_hit(shadow_ro, Ldir)

    blocked = 0
    if obj_id != 0 and t_hit > EPS and t_hit < dist - SHADOW_BIAS:
        blocked = 1

    return blocked


# ----------------------------
# 左右半屏射线
# ----------------------------
@ti.func
def half_ray(local_i, j):
    u = (ti.cast(local_i, ti.f32) - HALF_W * 0.5) / H * 2.0
    v = (ti.cast(j, ti.f32) - H * 0.5) / H * 2.0

    ro = CAMERA
    rd = normalize(tm.vec3(u, v, -1.0))
    return ro, rd


# ----------------------------
# 着色
# ----------------------------
@ti.func
def phong_compare(pos, normal, obj_color, light_pos, ka, kd, ks, shininess, use_shadow):
    N = normalize(normal)
    L = normalize(light_pos - pos)
    V = normalize(CAMERA - pos)

    ambient = ka * obj_color
    color = ambient

    blocked = 0
    if use_shadow == 1:
        blocked = in_shadow(pos, N, light_pos)

    if blocked == 0:
        ndotl = ti.max(N.dot(L), 0.0)
        diffuse = kd * ndotl * obj_color

        specular = tm.vec3(0.0, 0.0, 0.0)
        if ndotl > 0.0:
            R = normalize(reflect_dir(-L, N))
            spec = ti.pow(ti.max(R.dot(V), 0.0), shininess)
            specular = ks * spec * tm.vec3(1.0, 1.0, 1.0)

        color = ambient + diffuse + specular

    return tm.clamp(color, 0.0, 1.0)


@ti.func
def trace_half(local_i, j, light_pos, ka, kd, ks, shininess, use_shadow):
    ro, rd = half_ray(local_i, j)
    t_hit, obj_id, cone_part = scene_hit(ro, rd)

    color = BACKGROUND
    if obj_id != 0:
        p = ro + rd * t_hit
        if obj_id == 1:
            color = phong_compare(
                p, sphere_normal(p), SPHERE_COLOR, light_pos, ka, kd, ks, shininess, use_shadow
            )
        elif obj_id == 2:
            color = phong_compare(
                p, cone_normal(p, cone_part), CONE_COLOR, light_pos, ka, kd, ks, shininess, use_shadow
            )
        else:
            color = phong_compare(
                p, tm.vec3(0.0, 1.0, 0.0), ground_color(p), light_pos, 0.08, 0.94, 0.03, 8.0, use_shadow
            )

    return color


@ti.kernel
def render_compare(lx: ti.f32, ly: ti.f32, lz: ti.f32,
                   ka: ti.f32, kd: ti.f32, ks: ti.f32, shininess: ti.f32):
    sep = tm.vec3(0.95, 0.95, 0.95)
    light_pos = tm.vec3(lx, ly, lz)

    for i, j in pixels:
        if i == HALF_W or i == HALF_W - 1:
            pixels[i, j] = sep
        elif i < HALF_W:
            pixels[i, j] = trace_half(i, j, light_pos, ka, kd, ks, shininess, 0)
        else:
            pixels[i, j] = trace_half(i - HALF_W, j, light_pos, ka, kd, ks, shininess, 1)


def main():
    window = ti.ui.Window("Left: Phong | Right: Phong + Hard Shadow", (W, H), vsync=True)
    canvas = window.get_canvas()
    gui = window.get_gui()

    lx, ly, lz = -3.2, 4.8, 3.0
    ka = 0.18
    kd = 0.78
    ks = 0.36
    shininess = 32.0

    while window.running:
        render_compare(lx, ly, lz, ka, kd, ks, shininess)
        canvas.set_image(pixels)

        with gui.sub_window("Shadow Compare Parameters", 0.58, 0.06, 0.38, 0.30):
            gui.text("Left = Phong, Right = Hard Shadow")
            lx = gui.slider_float("Light X", lx, -6.0, 2.0)
            ly = gui.slider_float("Light Y", ly, 1.5, 8.0)
            lz = gui.slider_float("Light Z", lz, -1.0, 6.0)
            ka = gui.slider_float("Ka", ka, 0.0, 1.0)
            kd = gui.slider_float("Kd", kd, 0.0, 1.0)
            ks = gui.slider_float("Ks", ks, 0.0, 1.0)
            shininess = gui.slider_float("Shininess", shininess, 1.0, 128.0)

        window.show()


if __name__ == "__main__":
    main()