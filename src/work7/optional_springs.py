import taichi as ti

ti.init(arch=ti.gpu)

N = 20
num_particles = N * N

spacing = 0.040
mass = 1.0
dt = 5e-4

k_s = 10000.0
k_d = ti.field(dtype=ti.f32, shape=())

gravity = ti.Vector([0.0, -9.8, 0.0])
max_velocity = 50.0

num_structural_springs = 2 * N * (N - 1)
num_shear_springs = 2 * (N - 1) * (N - 1)
num_bending_springs = 2 * N * (N - 2)

num_base_springs = num_structural_springs
num_full_springs = num_structural_springs + num_shear_springs + num_bending_springs

base_x = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)
base_v = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)
base_f = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)
base_x_next = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)
base_v_next = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)
base_f_next = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)

full_x = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)
full_v = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)
full_f = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)
full_x_next = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)
full_v_next = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)
full_f_next = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)

is_fixed = ti.field(dtype=ti.i32, shape=num_particles)

base_a = ti.field(dtype=ti.i32, shape=num_base_springs)
base_b = ti.field(dtype=ti.i32, shape=num_base_springs)
base_rest = ti.field(dtype=ti.f32, shape=num_base_springs)

full_a = ti.field(dtype=ti.i32, shape=num_full_springs)
full_b = ti.field(dtype=ti.i32, shape=num_full_springs)
full_rest = ti.field(dtype=ti.f32, shape=num_full_springs)

base_indices = ti.field(dtype=ti.i32, shape=num_base_springs * 2)
full_structural_indices = ti.field(dtype=ti.i32, shape=num_structural_springs * 2)
full_shear_indices = ti.field(dtype=ti.i32, shape=num_shear_springs * 2)
full_bending_indices = ti.field(dtype=ti.i32, shape=num_bending_springs * 2)


@ti.func
def get_id(i, j):
    return i * N + j


@ti.func
def clamp_velocity(vel):
    result = vel
    length = vel.norm()

    if length > max_velocity:
        result = vel / length * max_velocity

    return result


@ti.func
def add_spring_force(pos, force, spring_a, spring_b, spring_rest, sid):
    a = spring_a[sid]
    b = spring_b[sid]

    delta = pos[a] - pos[b]
    length = delta.norm()

    if length > 1e-6:
        direction = delta / length
        spring_force = -k_s * (length - spring_rest[sid]) * direction

        ti.atomic_add(force[a], spring_force)
        ti.atomic_add(force[b], -spring_force)


@ti.kernel
def set_damping(value: ti.f32):
    k_d[None] = value


@ti.kernel
def init_particles():
    for i, j in ti.ndrange(N, N):
        idx = get_id(i, j)

        local_x = (j - (N - 1) * 0.5) * spacing
        y = 0.58 - i * spacing
        z = 0.0

        base_x[idx] = ti.Vector([local_x - 0.45, y, z])
        full_x[idx] = ti.Vector([local_x + 0.45, y, z])

        base_v[idx] = ti.Vector([0.0, 0.0, 0.0])
        full_v[idx] = ti.Vector([0.0, 0.0, 0.0])

        base_f[idx] = ti.Vector([0.0, 0.0, 0.0])
        full_f[idx] = ti.Vector([0.0, 0.0, 0.0])

        base_x_next[idx] = base_x[idx]
        full_x_next[idx] = full_x[idx]

        base_v_next[idx] = base_v[idx]
        full_v_next[idx] = full_v[idx]

        fixed = 0
        if i == 0 and (j == 0 or j == N - 1):
            fixed = 1

        is_fixed[idx] = fixed


@ti.kernel
def init_base_springs():
    for i, j in ti.ndrange(N, N - 1):
        sid = i * (N - 1) + j

        base_a[sid] = get_id(i, j)
        base_b[sid] = get_id(i, j + 1)
        base_rest[sid] = spacing

    offset = N * (N - 1)

    for i, j in ti.ndrange(N - 1, N):
        sid = offset + i * N + j

        base_a[sid] = get_id(i, j)
        base_b[sid] = get_id(i + 1, j)
        base_rest[sid] = spacing


@ti.kernel
def init_full_springs():
    for i, j in ti.ndrange(N, N - 1):
        sid = i * (N - 1) + j

        full_a[sid] = get_id(i, j)
        full_b[sid] = get_id(i, j + 1)
        full_rest[sid] = spacing

    vertical_offset = N * (N - 1)

    for i, j in ti.ndrange(N - 1, N):
        sid = vertical_offset + i * N + j

        full_a[sid] = get_id(i, j)
        full_b[sid] = get_id(i + 1, j)
        full_rest[sid] = spacing

    shear_offset = num_structural_springs

    for i, j in ti.ndrange(N - 1, N - 1):
        sid = shear_offset + i * (N - 1) + j

        full_a[sid] = get_id(i, j)
        full_b[sid] = get_id(i + 1, j + 1)
        full_rest[sid] = spacing * ti.sqrt(2.0)

    shear_offset_2 = shear_offset + (N - 1) * (N - 1)

    for i, j in ti.ndrange(N - 1, N - 1):
        sid = shear_offset_2 + i * (N - 1) + j

        full_a[sid] = get_id(i, j + 1)
        full_b[sid] = get_id(i + 1, j)
        full_rest[sid] = spacing * ti.sqrt(2.0)

    bending_offset = num_structural_springs + num_shear_springs

    for i, j in ti.ndrange(N, N - 2):
        sid = bending_offset + i * (N - 2) + j

        full_a[sid] = get_id(i, j)
        full_b[sid] = get_id(i, j + 2)
        full_rest[sid] = spacing * 2.0

    bending_offset_2 = bending_offset + N * (N - 2)

    for i, j in ti.ndrange(N - 2, N):
        sid = bending_offset_2 + i * N + j

        full_a[sid] = get_id(i, j)
        full_b[sid] = get_id(i + 2, j)
        full_rest[sid] = spacing * 2.0


@ti.kernel
def init_render_indices():
    for sid in range(num_base_springs):
        base_indices[sid * 2] = base_a[sid]
        base_indices[sid * 2 + 1] = base_b[sid]

    for sid in range(num_structural_springs):
        full_structural_indices[sid * 2] = full_a[sid]
        full_structural_indices[sid * 2 + 1] = full_b[sid]

    for local_id in range(num_shear_springs):
        sid = num_structural_springs + local_id

        full_shear_indices[local_id * 2] = full_a[sid]
        full_shear_indices[local_id * 2 + 1] = full_b[sid]

    for local_id in range(num_bending_springs):
        sid = num_structural_springs + num_shear_springs + local_id

        full_bending_indices[local_id * 2] = full_a[sid]
        full_bending_indices[local_id * 2 + 1] = full_b[sid]


@ti.kernel
def add_disturbance():
    for i, j in ti.ndrange(N, N):
        idx = get_id(i, j)

        if is_fixed[idx] == 0 and i > N // 3:
            wave = ti.sin(j * 0.65) + 0.5 * ti.cos(i * 0.45)

            base_v[idx] += ti.Vector([1.4 + 0.6 * wave, 0.0, 0.30 * wave])
            full_v[idx] += ti.Vector([1.4 + 0.6 * wave, 0.0, 0.30 * wave])


@ti.kernel
def step_explicit():
    for i in range(num_particles):
        base_f[i] = mass * gravity - k_d[None] * base_v[i]
        full_f[i] = mass * gravity - k_d[None] * full_v[i]

    for sid in range(num_base_springs):
        add_spring_force(base_x, base_f, base_a, base_b, base_rest, sid)

    for sid in range(num_full_springs):
        add_spring_force(full_x, full_f, full_a, full_b, full_rest, sid)

    for i in range(num_particles):
        if is_fixed[i] == 0:
            old_base_v = base_v[i]
            old_full_v = full_v[i]

            base_x[i] += old_base_v * dt
            full_x[i] += old_full_v * dt

            base_v[i] += base_f[i] / mass * dt
            full_v[i] += full_f[i] / mass * dt

            base_v[i] = clamp_velocity(base_v[i])
            full_v[i] = clamp_velocity(full_v[i])
        else:
            base_v[i] = ti.Vector([0.0, 0.0, 0.0])
            full_v[i] = ti.Vector([0.0, 0.0, 0.0])


@ti.kernel
def step_semi_implicit():
    for i in range(num_particles):
        base_f[i] = mass * gravity - k_d[None] * base_v[i]
        full_f[i] = mass * gravity - k_d[None] * full_v[i]

    for sid in range(num_base_springs):
        add_spring_force(base_x, base_f, base_a, base_b, base_rest, sid)

    for sid in range(num_full_springs):
        add_spring_force(full_x, full_f, full_a, full_b, full_rest, sid)

    for i in range(num_particles):
        if is_fixed[i] == 0:
            base_v[i] += base_f[i] / mass * dt
            full_v[i] += full_f[i] / mass * dt

            base_v[i] = clamp_velocity(base_v[i])
            full_v[i] = clamp_velocity(full_v[i])

            base_x[i] += base_v[i] * dt
            full_x[i] += full_v[i] * dt
        else:
            base_v[i] = ti.Vector([0.0, 0.0, 0.0])
            full_v[i] = ti.Vector([0.0, 0.0, 0.0])


@ti.kernel
def step_implicit():
    for i in range(num_particles):
        base_x_next[i] = base_x[i]
        base_v_next[i] = base_v[i]

        full_x_next[i] = full_x[i]
        full_v_next[i] = full_v[i]

    for _ in ti.static(range(8)):
        for i in range(num_particles):
            base_f_next[i] = mass * gravity - k_d[None] * base_v_next[i]
            full_f_next[i] = mass * gravity - k_d[None] * full_v_next[i]

        for sid in range(num_base_springs):
            add_spring_force(base_x_next, base_f_next, base_a, base_b, base_rest, sid)

        for sid in range(num_full_springs):
            add_spring_force(full_x_next, full_f_next, full_a, full_b, full_rest, sid)

        for i in range(num_particles):
            if is_fixed[i] == 0:
                base_v_next[i] = base_v[i] + base_f_next[i] / mass * dt
                full_v_next[i] = full_v[i] + full_f_next[i] / mass * dt

                base_v_next[i] = clamp_velocity(base_v_next[i])
                full_v_next[i] = clamp_velocity(full_v_next[i])

                base_x_next[i] = base_x[i] + base_v_next[i] * dt
                full_x_next[i] = full_x[i] + full_v_next[i] * dt
            else:
                base_v_next[i] = ti.Vector([0.0, 0.0, 0.0])
                full_v_next[i] = ti.Vector([0.0, 0.0, 0.0])

                base_x_next[i] = base_x[i]
                full_x_next[i] = full_x[i]

    for i in range(num_particles):
        if is_fixed[i] == 0:
            base_x[i] = base_x_next[i]
            base_v[i] = base_v_next[i]

            full_x[i] = full_x_next[i]
            full_v[i] = full_v_next[i]
        else:
            base_v[i] = ti.Vector([0.0, 0.0, 0.0])
            full_v[i] = ti.Vector([0.0, 0.0, 0.0])


def reset_cloth():
    init_particles()
    init_base_springs()
    init_full_springs()
    init_render_indices()
    add_disturbance()


def simulate_one_step(method):
    if method == 0:
        step_explicit()
    elif method == 1:
        step_semi_implicit()
    else:
        step_implicit()


def main():
    current_damping = 1.0
    set_damping(current_damping)
    reset_cloth()

    window = ti.ui.Window(
        "Games101 - Optional Springs Comparison",
        res=(900, 900),
        vsync=True
    )

    canvas = window.get_canvas()
    scene = ti.ui.Scene()
    camera = ti.ui.Camera()

    camera.position(0.0, 0.03, 2.55)
    camera.lookat(0.0, 0.04, 0.0)
    camera.up(0.0, 1.0, 0.0)
    camera.fov(50)

    method = 1
    paused = False
    show_extra_springs = True

    while window.running:
        if window.get_event(ti.ui.PRESS):
            if window.event.key == ti.ui.ESCAPE:
                break
            elif window.event.key == "1":
                method = 0
            elif window.event.key == "2":
                method = 1
            elif window.event.key == "3":
                method = 2
            elif window.event.key == "r":
                reset_cloth()
            elif window.event.key == " ":
                paused = not paused
            elif window.event.key == "d":
                add_disturbance()

        gui = window.get_gui()

        with gui.sub_window("Control Panel", 0.02, 0.02, 0.39, 0.42):
            gui.text("Optional 1: Spring Topology")
            gui.text("Left: Structural only")
            gui.text("Right: Structural + Shear + Bending")
            gui.text("")

            gui.text("Integration Method:")

            if gui.button(("[*] " if method == 0 else "[ ] ") + "Explicit Euler"):
                method = 0

            if gui.button(("[*] " if method == 1 else "[ ] ") + "Semi-Implicit Euler"):
                method = 1

            if gui.button(("[*] " if method == 2 else "[ ] ") + "Implicit Euler"):
                method = 2

            gui.text("")
            gui.text("Damping:")

            if gui.button(("[*] " if current_damping == 1.0 else "[ ] ") + "k_d = 1.0"):
                current_damping = 1.0
                set_damping(current_damping)
                reset_cloth()

            if gui.button(("[*] " if current_damping == 5.0 else "[ ] ") + "k_d = 5.0"):
                current_damping = 5.0
                set_damping(current_damping)
                reset_cloth()

            gui.text("")

            if gui.button("Hide Extra Springs" if show_extra_springs else "Show Extra Springs"):
                show_extra_springs = not show_extra_springs

            if gui.button("Disturb Cloth"):
                add_disturbance()

            if gui.button("Pause Simulation" if not paused else "Resume Simulation"):
                paused = not paused

            if gui.button("Reset Cloth"):
                reset_cloth()

            gui.text("")
            gui.text("1/2/3: switch method")
            gui.text("D: disturb, Space: pause, R: reset")

        camera.track_user_inputs(
            window,
            movement_speed=0.03,
            hold_key=ti.ui.RMB
        )

        if not paused:
            for _ in range(8):
                simulate_one_step(method)

        scene.set_camera(camera)
        scene.ambient_light((0.45, 0.45, 0.45))
        scene.point_light(pos=(0.5, 1.5, 1.5), color=(1.0, 1.0, 1.0))

        scene.lines(
            base_x,
            indices=base_indices,
            color=(0.75, 0.75, 0.75),
            width=1.0
        )

        scene.particles(
            base_x,
            radius=0.0085,
            color=(0.0, 0.60, 1.0)
        )

        scene.lines(
            full_x,
            indices=full_structural_indices,
            color=(0.90, 0.90, 0.90),
            width=1.0
        )

        if show_extra_springs:
            scene.lines(
                full_x,
                indices=full_shear_indices,
                color=(1.0, 0.76, 0.20),
                width=0.75
            )

            scene.lines(
                full_x,
                indices=full_bending_indices,
                color=(0.75, 0.35, 1.0),
                width=0.65
            )

        scene.particles(
            full_x,
            radius=0.0085,
            color=(0.0, 0.95, 1.0)
        )

        canvas.scene(scene)
        window.show()


if __name__ == "__main__":
    main()