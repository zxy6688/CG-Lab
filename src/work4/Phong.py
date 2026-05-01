import taichi as ti
import taichi.math as tm

ti.init(arch=ti.gpu)

W, H = 800, 600
pixels = ti.Vector.field(3, dtype=ti.f32, shape=(W, H))

EPS = 1e-4
INF = 1e8

# teacher-like framing
CAM = tm.vec3(0.0, 0.0, 5.0)
LIGHT = tm.vec3(2.2, 3.0, 4.0)

SPHERE_C = tm.vec3(-1.05, -0.05, 0.0)
SPHERE_R = 0.85

CONE_APEX = tm.vec3(1.15, 1.0, 0.0)
CONE_BASE_Y = -1.0
CONE_R = 0.78
CONE_H = CONE_APEX.y - CONE_BASE_Y
K = CONE_R / CONE_H
K2 = K * K

BG = tm.vec3(0.05, 0.15, 0.15)
SPHERE_COL = tm.vec3(0.8, 0.1, 0.1)
CONE_COL = tm.vec3(0.6, 0.2, 0.8)
LIGHT_COL = tm.vec3(1.0, 1.0, 1.0)

@ti.func
def normalize(v):
    return v / v.norm(1e-6)

@ti.func
def intersect_sphere(ro, rd):
    oc = ro - SPHERE_C
    b = 2.0 * oc.dot(rd)
    c = oc.dot(oc) - SPHERE_R * SPHERE_R
    delta = b * b - 4.0 * c
    t = INF
    if delta >= 0.0:
        sq = ti.sqrt(delta)
        t1 = (-b - sq) * 0.5
        t2 = (-b + sq) * 0.5
        if t1 > EPS:
            t = t1
        elif t2 > EPS:
            t = t2
    return t

@ti.func
def sphere_normal(p):
    return normalize(p - SPHERE_C)

@ti.func
def intersect_cone(ro, rd):
    rel = ro - CONE_APEX
    t_best = INF
    hit_part = 0  # 0 none, 1 side, 2 base

    a = rd.x * rd.x + rd.z * rd.z - K2 * rd.y * rd.y
    b = 2.0 * (rel.x * rd.x + rel.z * rd.z - K2 * rel.y * rd.y)
    c = rel.x * rel.x + rel.z * rel.z - K2 * rel.y * rel.y

    if ti.abs(a) > 1e-6:
        delta = b * b - 4.0 * a * c
        if delta >= 0.0:
            sq = ti.sqrt(delta)
            t1 = (-b - sq) / (2.0 * a)
            t2 = (-b + sq) / (2.0 * a)

            if t1 > EPS:
                p1 = ro + t1 * rd
                y1 = p1.y - CONE_APEX.y
                if -CONE_H <= y1 <= 0.0:
                    t_best = t1
                    hit_part = 1

            if t2 > EPS and t2 < t_best:
                p2 = ro + t2 * rd
                y2 = p2.y - CONE_APEX.y
                if -CONE_H <= y2 <= 0.0:
                    t_best = t2
                    hit_part = 1

    if ti.abs(rd.y) > 1e-6:
        tb = (CONE_BASE_Y - ro.y) / rd.y
        if tb > EPS and tb < t_best:
            pb = ro + tb * rd
            dx = pb.x - CONE_APEX.x
            dz = pb.z - CONE_APEX.z
            if dx * dx + dz * dz <= CONE_R * CONE_R:
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
        n = normalize(tm.vec3(local.x, -K2 * local.y, local.z))
    return n

@ti.func
def phong_shade(pos, normal, base_color, ka, kd, ks, sh):
    N = normalize(normal)
    L = normalize(LIGHT - pos)
    V = normalize(CAM - pos)

    ambient = ka * LIGHT_COL * base_color
    ndl = ti.max(N.dot(L), 0.0)
    diffuse = kd * ndl * LIGHT_COL * base_color

    specular = tm.vec3(0.0, 0.0, 0.0)
    if ndl > 0.0:
        R = normalize(2.0 * N.dot(L) * N - L)
        rv = ti.max(R.dot(V), 0.0)
        specular = ks * ti.pow(rv, sh) * LIGHT_COL

    return tm.clamp(ambient + diffuse + specular, 0.0, 1.0)

@ti.kernel
def render(ka: ti.f32, kd: ti.f32, ks: ti.f32, sh: ti.f32):
    for i, j in pixels:
        u = (i - W * 0.5) / H * 2.0
        v = (j - H * 0.5) / H * 2.0
        ro = CAM
        rd = normalize(tm.vec3(u, v, -1.0))

        best_t = INF
        obj = 0
        part = 0

        ts = intersect_sphere(ro, rd)
        if ts < best_t:
            best_t = ts
            obj = 1

        tc, cp = intersect_cone(ro, rd)
        if tc < best_t:
            best_t = tc
            obj = 2
            part = cp

        color = BG
        if obj != 0:
            p = ro + best_t * rd
            if obj == 1:
                color = phong_shade(p, sphere_normal(p), SPHERE_COL, ka, kd, ks, sh)
            else:
                color = phong_shade(p, cone_normal(p, part), CONE_COL, ka, kd, ks, sh)

        pixels[i, j] = color


def main():
    window = ti.ui.Window("Phong Shading Demo", (W, H), vsync=True)
    canvas = window.get_canvas()

    ka = 0.2
    kd = 0.7
    ks = 0.5
    shininess = 32.0

    while window.running:
        render(ka, kd, ks, shininess)
        canvas.set_image(pixels)

        gui = window.get_gui()
        with gui.sub_window("Material Parameters", 0.68, 0.05, 0.28, 0.22):
            ka = gui.slider_float('Ka (Ambient)', ka, 0.0, 1.0)
            kd = gui.slider_float('Kd (Diffuse)', kd, 0.0, 1.0)
            ks = gui.slider_float('Ks (Specular)', ks, 0.0, 1.0)
            shininess = gui.slider_float('N (Shininess)', shininess, 1.0, 128.0)

        window.show()

if __name__ == '__main__':
    main()
