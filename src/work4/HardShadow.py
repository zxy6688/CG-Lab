import taichi as ti
import taichi.math as tm

ti.init(arch=ti.gpu)

W, H = 960, 640
ASPECT = W / H
VIEW_SCALE = 1.8
EPS = 1e-4
INF = 1e8
SHADOW_BIAS = 2e-3

pixels = ti.Vector.field(3, dtype=ti.f32, shape=(W, H))

# ----------------------------
# 场景常量
# ----------------------------

# Camera
CAM_X, CAM_Y, CAM_Z = 0.0, 0.0, 5.0

# Light
LIGHT_X, LIGHT_Y, LIGHT_Z = 2.0, 3.0, 4.0

# Sphere
SPHERE_CX, SPHERE_CY, SPHERE_CZ = -1.2, -0.2, 0.0
SPHERE_R = 1.2

# Cone
APEX_X, APEX_Y, APEX_Z = 1.2, 1.2, 0.0
BASE_Y = -1.4
CONE_R = 1.2
CONE_H = APEX_Y - BASE_Y
K = CONE_R / CONE_H
K2 = K * K

# Colors
BG_R, BG_G, BG_B = 0.03, 0.18, 0.18
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
    c = sphere_center()
    oc = ro - c

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
    apex = cone_apex()
    rel = ro - apex

    best_t = INF
    hit_part = 0  # 0=none, 1=side, 2=base

    # 圆锥侧面
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
        t_lin = -c / b
        if t_lin > EPS:
            p = ro + t_lin * rd
            y_local = p.y - APEX_Y
            if y_local >= -CONE_H and y_local <= 0.0:
                best_t = t_lin
                hit_part = 1

    # 圆锥底面圆盘
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
    n = tm.vec3(0.0, 0.0, 0.0)

    if hit_part == 2:
        n = tm.vec3(0.0, -1.0, 0.0)
    else:
        local = p - cone_apex()
        n = tm.vec3(local.x, -K2 * local.y, local.z).normalized()

    return n


@ti.func
def offset_ray_origin(pos, normal, dir_vec):
    new_pos = pos
    if normal.dot(dir_vec) >= 0.0:
        new_pos = pos + normal * SHADOW_BIAS
    else:
        new_pos = pos - normal * SHADOW_BIAS
    return new_pos


@ti.func
def is_in_shadow(pos, normal):
    lp = light_pos()
    to_light = lp - pos
    light_dist = to_light.norm()
    light_dir = to_light.normalized()

    shadow_ro = offset_ray_origin(pos, normal, light_dir)
    shadow_rd = light_dir

    t_s = intersect_sphere(shadow_ro, shadow_rd)
    t_c, _ = intersect_cone(shadow_ro, shadow_rd)

    blocked = 0
    if t_s > EPS and t_s < light_dist - SHADOW_BIAS:
        blocked = 1
    if t_c > EPS and t_c < light_dist - SHADOW_BIAS:
        blocked = 1

    return blocked


@ti.func
def phong_shade_with_shadow(pos, normal, obj_color, ka, kd, ks, shininess):
    light_color = tm.vec3(1.0, 1.0, 1.0)

    N = normal.normalized()
    L = (light_pos() - pos).normalized()
    V = (cam_pos() - pos).normalized()

    ambient = ka * light_color * obj_color
    color = ambient

    shadow_flag = is_in_shadow(pos, N)

    if shadow_flag == 0:
        ndotl = ti.max(N.dot(L), 0.0)
        diffuse = kd * ndotl * light_color * obj_color

        specular = tm.vec3(0.0, 0.0, 0.0)
        if ndotl > 0.0:
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
        px = (2.0 * ((i + 0.5) / W) - 1.0) * ASPECT * VIEW_SCALE
        py = (1.0 - 2.0 * ((j + 0.5) / H)) * VIEW_SCALE
        image_point = tm.vec3(px, py, 0.0)

        ro = camera
        rd = (image_point - ro).normalized()

        best_t = INF
        best_obj = 0
        cone_part = 0

        t_s = intersect_sphere(ro, rd)
        if t_s < best_t:
            best_t = t_s
            best_obj = 1

        t_c, hit_part = intersect_cone(ro, rd)
        if t_c < best_t:
            best_t = t_c
            best_obj = 2
            cone_part = hit_part

        color = bg

        if best_obj != 0:
            hit_pos = ro + best_t * rd

            if best_obj == 1:
                N = sphere_normal(hit_pos)
                color = phong_shade_with_shadow(hit_pos, N, sphere_color, ka, kd, ks, shininess)
            else:
                N = cone_normal(hit_pos, cone_part)
                color = phong_shade_with_shadow(hit_pos, N, cone_color, ka, kd, ks, shininess)

        pixels[i, j] = color


def main():
    window = ti.ui.Window("Work4 Optional 2 - Hard Shadow", (W, H), vsync=True)
    canvas = window.get_canvas()

    ka = 0.2
    kd = 0.7
    ks = 0.5
    shininess = 32.0

    while window.running:
        gui = window.get_gui()
        with gui.sub_window("Phong + Hard Shadow", 0.02, 0.02, 0.32, 0.24):
            gui.text("Shadowed points keep ambient term only")
            ka = gui.slider_float("Ka", ka, 0.0, 1.0)
            kd = gui.slider_float("Kd", kd, 0.0, 1.0)
            ks = gui.slider_float("Ks", ks, 0.0, 1.0)
            shininess = gui.slider_float("Shininess", shininess, 1.0, 128.0)
            gui.text(f"Ka = {ka:.2f}")
            gui.text(f"Kd = {kd:.2f}")
            gui.text(f"Ks = {ks:.2f}")
            gui.text(f"Shininess = {shininess:.1f}")

        render(ka, kd, ks, shininess)
        canvas.set_image(pixels)
        window.show()


if __name__ == "__main__":
    main()