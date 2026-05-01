import taichi as ti

ti.init(arch=ti.gpu)

# debug解决一下效果不明显的问题：640 × 360：锯齿会更明显，AA 前后差异更容易看出来
WIDTH = 640
HEIGHT = 360

INF = 1e10
EPS = 1e-4

MAX_BOUNCES_LIMIT = 5
AA_GRID_LIMIT = 5

pixels = ti.Vector.field(3, dtype=ti.f32, shape=(WIDTH, HEIGHT))


@ti.func
def clamp01(x):
    return ti.min(ti.max(x, 0.0), 1.0)


@ti.func
def clamp_color(c):
    return ti.Vector([
        clamp01(c[0]),
        clamp01(c[1]),
        clamp01(c[2])
    ])


@ti.func
def gamma_correct(c):
    c = clamp_color(c)
    return ti.Vector([
        ti.sqrt(c[0]),
        ti.sqrt(c[1]),
        ti.sqrt(c[2])
    ])


@ti.func
def reflect(direction, normal):
    return direction - 2.0 * direction.dot(normal) * normal


@ti.func
def sky_color(direction):
    t = 0.5 * (direction.y + 1.0)

    bottom = ti.Vector([1.0, 1.0, 1.0])
    top = ti.Vector([0.45, 0.65, 1.0])

    return (1.0 - t) * bottom + t * top


@ti.func
def intersect_sphere(ray_origin, ray_dir, center, radius):
    hit = 0
    nearest_t = INF

    oc = ray_origin - center

    b = oc.dot(ray_dir)
    c = oc.dot(oc) - radius * radius

    discriminant = b * b - c

    if discriminant > 0.0:
        sqrt_d = ti.sqrt(discriminant)

        t1 = -b - sqrt_d
        t2 = -b + sqrt_d

        if t1 > EPS:
            hit = 1
            nearest_t = t1
        elif t2 > EPS:
            hit = 1
            nearest_t = t2

    return hit, nearest_t


@ti.func
def get_checker_color(pos):
    x_id = ti.cast(ti.floor(pos.x), ti.i32)
    z_id = ti.cast(ti.floor(pos.z), ti.i32)

    checker = (x_id + z_id) & 1

    color = ti.Vector([0.9, 0.9, 0.9])

    if checker == 1:
        color = ti.Vector([0.08, 0.08, 0.08])

    return color


@ti.func
def intersect_scene(ray_origin, ray_dir):
    hit_anything = 0
    nearest_t = INF

    hit_normal = ti.Vector([0.0, 1.0, 0.0])
    material_id = 0
    base_color = ti.Vector([0.0, 0.0, 0.0])

    red_center = ti.Vector([-1.5, 0.0, 0.0])
    red_radius = 1.0

    hit_red, t_red = intersect_sphere(ray_origin, ray_dir, red_center, red_radius)

    if hit_red == 1 and t_red < nearest_t:
        hit_anything = 1
        nearest_t = t_red

        hit_pos = ray_origin + ray_dir * nearest_t
        hit_normal = (hit_pos - red_center).normalized()

        material_id = 2
        base_color = ti.Vector([1.0, 0.12, 0.08])

    mirror_center = ti.Vector([1.5, 0.0, 0.0])
    mirror_radius = 1.0

    hit_mirror, t_mirror = intersect_sphere(
        ray_origin,
        ray_dir,
        mirror_center,
        mirror_radius
    )

    if hit_mirror == 1 and t_mirror < nearest_t:
        hit_anything = 1
        nearest_t = t_mirror

        hit_pos = ray_origin + ray_dir * nearest_t
        hit_normal = (hit_pos - mirror_center).normalized()

        material_id = 3
        base_color = ti.Vector([0.82, 0.82, 0.88])

    if ti.abs(ray_dir.y) > EPS:
        t_plane = (-1.0 - ray_origin.y) / ray_dir.y

        if t_plane > EPS and t_plane < nearest_t:
            hit_anything = 1
            nearest_t = t_plane

            hit_pos = ray_origin + ray_dir * nearest_t
            hit_normal = ti.Vector([0.0, 1.0, 0.0])

            material_id = 1
            base_color = get_checker_color(hit_pos)

    return hit_anything, nearest_t, hit_normal, material_id, base_color


@ti.func
def is_in_shadow(hit_pos, normal, light_pos):
    shadow = 0

    shadow_origin = hit_pos + normal * EPS

    to_light = light_pos - shadow_origin
    light_distance = to_light.norm()
    shadow_dir = to_light / light_distance

    hit, t, _, _, _ = intersect_scene(shadow_origin, shadow_dir)

    if hit == 1 and t < light_distance - EPS:
        shadow = 1

    return shadow


@ti.func
def phong_shading(hit_pos, normal, ray_dir, base_color, light_pos):
    ambient_strength = 0.12
    diffuse_strength = 0.95
    specular_strength = 0.35
    shininess = 64.0

    light_color = ti.Vector([1.0, 0.96, 0.86])

    color = ambient_strength * base_color

    shadow = is_in_shadow(hit_pos, normal, light_pos)

    if shadow == 0:
        to_light = light_pos - hit_pos
        distance = to_light.norm()
        light_dir = to_light / distance

        n_dot_l = ti.max(normal.dot(light_dir), 0.0)

        diffuse = diffuse_strength * n_dot_l * base_color * light_color

        view_dir = (-ray_dir).normalized()
        half_dir = (light_dir + view_dir).normalized()

        specular_factor = ti.pow(ti.max(normal.dot(half_dir), 0.0), shininess)
        specular = specular_strength * specular_factor * light_color

        attenuation = 1.0 / (0.35 + 0.08 * distance + 0.015 * distance * distance)

        color += attenuation * (diffuse + specular)

    return color


@ti.func
def trace_ray(ray_origin, ray_dir, light_pos, max_bounces):
    final_color = ti.Vector([0.0, 0.0, 0.0])
    throughput = ti.Vector([1.0, 1.0, 1.0])

    current_origin = ray_origin
    current_dir = ray_dir

    active = 1

    for bounce in range(MAX_BOUNCES_LIMIT):
        if active == 1 and bounce < max_bounces:
            hit, t, normal, material_id, base_color = intersect_scene(
                current_origin,
                current_dir
            )

            if hit == 0:
                final_color += throughput * sky_color(current_dir)
                active = 0
            else:
                hit_pos = current_origin + current_dir * t

                if material_id == 1 or material_id == 2:
                    local_color = phong_shading(
                        hit_pos,
                        normal,
                        current_dir,
                        base_color,
                        light_pos
                    )

                    final_color += throughput * local_color
                    active = 0

                elif material_id == 3:
                    if bounce + 1 >= max_bounces:
                        final_color += throughput * ti.Vector([0.035, 0.035, 0.04])
                        active = 0
                    else:
                        reflected_dir = reflect(current_dir, normal).normalized()

                        current_origin = hit_pos + reflected_dir * EPS
                        current_dir = reflected_dir

                        throughput *= ti.Vector([0.8, 0.8, 0.82])

    return final_color


@ti.func
def generate_camera_ray(i, j, offset_x, offset_y):
    camera_pos = ti.Vector([0.0, 1.0, 5.5])
    camera_target = ti.Vector([0.0, 0.0, 0.0])

    forward = (camera_target - camera_pos).normalized()
    world_up = ti.Vector([0.0, 1.0, 0.0])

    right = forward.cross(world_up).normalized()
    up = right.cross(forward).normalized()

    aspect = ti.cast(WIDTH, ti.f32) / ti.cast(HEIGHT, ti.f32)
    fov = 45.0 * 3.141592653589793 / 180.0
    scale = ti.tan(fov * 0.5)

    x = 2.0 * (ti.cast(i, ti.f32) + offset_x) / ti.cast(WIDTH, ti.f32) - 1.0
    y = 2.0 * (ti.cast(j, ti.f32) + offset_y) / ti.cast(HEIGHT, ti.f32) - 1.0

    x *= aspect * scale
    y *= scale

    ray_dir = (forward + x * right + y * up).normalized()

    return camera_pos, ray_dir


@ti.kernel
def render(
    light_x: ti.f32,
    light_y: ti.f32,
    light_z: ti.f32,
    max_bounces: ti.i32,
    aa_grid: ti.i32
):
    light_pos = ti.Vector([light_x, light_y, light_z])

    for i, j in pixels:
        color_sum = ti.Vector([0.0, 0.0, 0.0])
        sample_count = 0.0

        grid_f = ti.cast(aa_grid, ti.f32)

        for sx in range(AA_GRID_LIMIT):
            for sy in range(AA_GRID_LIMIT):
                if sx < aa_grid and sy < aa_grid:
                    offset_x = (ti.cast(sx, ti.f32) + 0.5) / grid_f
                    offset_y = (ti.cast(sy, ti.f32) + 0.5) / grid_f

                    camera_pos, ray_dir = generate_camera_ray(
                        i,
                        j,
                        offset_x,
                        offset_y
                    )

                    color_sum += trace_ray(
                        camera_pos,
                        ray_dir,
                        light_pos,
                        max_bounces
                    )

                    sample_count += 1.0

        color = color_sum / sample_count

        pixels[i, j] = gamma_correct(color)


def main():
    window = ti.ui.Window(
        "Work5 Optional 2 - MSAA Anti-Aliasing",
        (WIDTH, HEIGHT),
        vsync=True
    )

    canvas = window.get_canvas()
    gui = window.get_gui()

    light_x = -2.5
    light_y = 4.0
    light_z = 3.0

    max_bounces = 3
    aa_grid = 1

    while window.running:
        if window.is_pressed(ti.ui.ESCAPE):
            break

        gui.begin("Controls", 0.02, 0.02, 0.38, 0.56)

        gui.text("Optional 2: MSAA Anti-Aliasing")
        gui.text("AA Grid 1 = 1 sample / pixel")
        gui.text("AA Grid 2 = 4 samples / pixel")
        gui.text("AA Grid 3 = 9 samples / pixel")
        gui.text("AA Grid 4 = 16 samples / pixel")
        gui.text("AA Grid 5 = 25 samples / pixel")
        gui.text(" ")

        light_x = gui.slider_float("Light X", light_x, -6.0, 6.0)
        light_y = gui.slider_float("Light Y", light_y, 0.5, 8.0)
        light_z = gui.slider_float("Light Z", light_z, -6.0, 6.0)

        aa_grid_float = gui.slider_float(
            "AA Grid",
            float(aa_grid),
            1.0,
            float(AA_GRID_LIMIT)
        )

        aa_grid = int(aa_grid_float + 0.5)

        if aa_grid < 1:
            aa_grid = 1
        if aa_grid > AA_GRID_LIMIT:
            aa_grid = AA_GRID_LIMIT

        max_bounces_float = gui.slider_float(
            "Max Bounces",
            float(max_bounces),
            1.0,
            float(MAX_BOUNCES_LIMIT)
        )

        max_bounces = int(max_bounces_float + 0.5)

        if max_bounces < 1:
            max_bounces = 1
        if max_bounces > MAX_BOUNCES_LIMIT:
            max_bounces = MAX_BOUNCES_LIMIT

        sample_count = aa_grid * aa_grid
        gui.text(f"Current AA Grid: {aa_grid}")
        gui.text(f"Samples per pixel: {sample_count}")

        gui.end()

        render(light_x, light_y, light_z, max_bounces, aa_grid)

        canvas.set_image(pixels)
        window.show()


if __name__ == "__main__":
    main()