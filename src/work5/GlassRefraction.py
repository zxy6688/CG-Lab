import taichi as ti

ti.init(arch=ti.gpu)

WIDTH = 960
HEIGHT = 540

INF = 1e10
EPS = 1e-4

MAX_BOUNCES_LIMIT = 8
GLASS_IOR = 1.5

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
def refract(direction, normal, eta_ratio):
    cos_theta = ti.min((-direction).dot(normal), 1.0)

    r_out_perp = eta_ratio * (direction + cos_theta * normal)

    k = 1.0 - r_out_perp.dot(r_out_perp)

    refracted = ti.Vector([0.0, 0.0, 0.0])
    can_refract = 0

    if k >= 0.0:
        r_out_parallel = -ti.sqrt(k) * normal
        refracted = (r_out_perp + r_out_parallel).normalized()
        can_refract = 1

    return refracted, can_refract


@ti.func
def schlick(cosine, ior):
    r0 = (1.0 - ior) / (1.0 + ior)
    r0 = r0 * r0
    return r0 + (1.0 - r0) * ti.pow(1.0 - cosine, 5.0)


@ti.func
def sky_color(direction):
    t = 0.5 * (direction.y + 1.0)

    bottom = ti.Vector([1.0, 1.0, 1.0])
    top = ti.Vector([0.45, 0.68, 1.0])

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
    scale = 1.0

    x_id = ti.cast(ti.floor(pos.x * scale), ti.i32)
    z_id = ti.cast(ti.floor(pos.z * scale), ti.i32)

    checker = (x_id + z_id) & 1

    color = ti.Vector([0.9, 0.9, 0.9])

    if checker == 1:
        color = ti.Vector([0.07, 0.07, 0.08])

    return color


@ti.func
def intersect_scene(ray_origin, ray_dir):
    hit_anything = 0
    nearest_t = INF

    hit_normal = ti.Vector([0.0, 1.0, 0.0])
    material_id = 0
    base_color = ti.Vector([0.0, 0.0, 0.0])

    # material_id:
    # 0 = none
    # 1 = checker ground diffuse
    # 3 = silver mirror sphere
    # 4 = red glass sphere

    glass_center = ti.Vector([-1.5, 0.0, 0.0])
    glass_radius = 1.0

    hit_glass, t_glass = intersect_sphere(
        ray_origin,
        ray_dir,
        glass_center,
        glass_radius
    )

    if hit_glass == 1 and t_glass < nearest_t:
        hit_anything = 1
        nearest_t = t_glass

        hit_pos = ray_origin + ray_dir * nearest_t
        hit_normal = (hit_pos - glass_center).normalized()

        material_id = 4
        base_color = ti.Vector([1.0, 0.45, 0.35])

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

    # Infinite ground plane: y = -1.0
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
    diffuse_strength = 1.0
    specular_strength = 0.35
    shininess = 72.0

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
def glass_highlight(hit_pos, normal, ray_dir, light_pos):
    color = ti.Vector([0.0, 0.0, 0.0])

    shadow = is_in_shadow(hit_pos, normal, light_pos)

    if shadow == 0:
        to_light = light_pos - hit_pos
        distance = to_light.norm()
        light_dir = to_light / distance

        view_dir = (-ray_dir).normalized()
        half_dir = (light_dir + view_dir).normalized()

        specular_factor = ti.pow(ti.max(normal.dot(half_dir), 0.0), 160.0)

        attenuation = 1.0 / (0.25 + 0.06 * distance + 0.012 * distance * distance)

        color += attenuation * specular_factor * ti.Vector([1.4, 1.25, 1.1])

        rim = ti.pow(1.0 - ti.max(normal.dot(view_dir), 0.0), 2.0)
        color += 0.06 * rim * ti.Vector([1.0, 0.45, 0.35])

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

                # Diffuse ground
                if material_id == 1:
                    local_color = phong_shading(
                        hit_pos,
                        normal,
                        current_dir,
                        base_color,
                        light_pos
                    )

                    final_color += throughput * local_color
                    active = 0

                # Silver mirror sphere
                elif material_id == 3:
                    if bounce + 1 >= max_bounces:
                        final_color += throughput * ti.Vector([0.035, 0.035, 0.04])
                        active = 0
                    else:
                        reflected_dir = reflect(current_dir, normal).normalized()

                        current_origin = hit_pos + reflected_dir * EPS
                        current_dir = reflected_dir

                        throughput *= ti.Vector([0.82, 0.82, 0.86])

                # Red glass sphere
                elif material_id == 4:
                    final_color += throughput * glass_highlight(
                        hit_pos,
                        normal,
                        current_dir,
                        light_pos
                    )

                    if bounce + 1 >= max_bounces:
                        final_color += throughput * ti.Vector([0.08, 0.025, 0.018])
                        active = 0
                    else:
                        front_face = current_dir.dot(normal) < 0.0

                        oriented_normal = normal
                        eta_ratio = 1.0 / GLASS_IOR

                        if not front_face:
                            oriented_normal = -normal
                            eta_ratio = GLASS_IOR

                        cos_theta = ti.min((-current_dir).dot(oriented_normal), 1.0)
                        sin_theta = ti.sqrt(ti.max(0.0, 1.0 - cos_theta * cos_theta))

                        cannot_refract = eta_ratio * sin_theta > 1.0

                        fresnel = schlick(cos_theta, GLASS_IOR)

                        next_dir = ti.Vector([0.0, 0.0, 0.0])

                        if cannot_refract:
                            next_dir = reflect(current_dir, oriented_normal).normalized()
                            throughput *= ti.Vector([0.90, 0.84, 0.80])
                        else:
                            refracted_dir, can_refract = refract(
                                current_dir,
                                oriented_normal,
                                eta_ratio
                            )

                            if can_refract == 1:
                                reflected_dir = reflect(
                                    current_dir,
                                    oriented_normal
                                ).normalized()

                                final_color += throughput * fresnel * 0.35 * sky_color(reflected_dir)

                                next_dir = refracted_dir

                                glass_tint = ti.Vector([1.0, 0.58, 0.48])
                                throughput *= (1.0 - fresnel) * glass_tint
                            else:
                                next_dir = reflect(current_dir, oriented_normal).normalized()
                                throughput *= ti.Vector([0.90, 0.84, 0.80])

                        current_origin = hit_pos + next_dir * EPS
                        current_dir = next_dir

    return final_color


@ti.kernel
def render(light_x: ti.f32, light_y: ti.f32, light_z: ti.f32, max_bounces: ti.i32):
    light_pos = ti.Vector([light_x, light_y, light_z])

    camera_pos = ti.Vector([0.0, 1.0, 5.5])
    camera_target = ti.Vector([0.0, 0.0, 0.0])

    forward = (camera_target - camera_pos).normalized()
    world_up = ti.Vector([0.0, 1.0, 0.0])

    right = forward.cross(world_up).normalized()
    up = right.cross(forward).normalized()

    aspect = ti.cast(WIDTH, ti.f32) / ti.cast(HEIGHT, ti.f32)
    fov = 45.0 * 3.141592653589793 / 180.0
    scale = ti.tan(fov * 0.5)

    for i, j in pixels:
        x = 2.0 * (ti.cast(i, ti.f32) + 0.5) / ti.cast(WIDTH, ti.f32) - 1.0
        y = 2.0 * (ti.cast(j, ti.f32) + 0.5) / ti.cast(HEIGHT, ti.f32) - 1.0

        x *= aspect * scale
        y *= scale

        ray_dir = (forward + x * right + y * up).normalized()

        color = trace_ray(camera_pos, ray_dir, light_pos, max_bounces)

        pixels[i, j] = gamma_correct(color)


def main():
    window = ti.ui.Window(
        "Work5 Optional 1 - Glass Refraction",
        (WIDTH, HEIGHT),
        vsync=True
    )

    canvas = window.get_canvas()
    gui = window.get_gui()

    light_x = -2.8
    light_y = 4.5
    light_z = 3.0

    max_bounces = 6

    while window.running:
        if window.is_pressed(ti.ui.ESCAPE):
            break

        gui.begin("Controls", 0.02, 0.02, 0.33, 0.30)

        gui.text("Optional 1: Glass Refraction")
        gui.text("Red sphere is now red glass.")

        light_x = gui.slider_float("Light X", light_x, -6.0, 6.0)
        light_y = gui.slider_float("Light Y", light_y, 0.5, 8.0)
        light_z = gui.slider_float("Light Z", light_z, -6.0, 6.0)

        max_bounces_float = gui.slider_float(
            "Max Bounces",
            float(max_bounces),
            1.0,
            float(MAX_BOUNCES_LIMIT)
        )

        max_bounces = int(max_bounces_float + 0.5)

        gui.end()

        render(light_x, light_y, light_z, max_bounces)

        canvas.set_image(pixels)
        window.show()


if __name__ == "__main__":
    main()