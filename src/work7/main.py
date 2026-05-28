import taichi as ti

ti.init(arch=ti.gpu)

# =========================
# Basic parameters
# =========================

N = 20
num_particles = N * N

spacing = 0.048
mass = 1.0
dt = 5e-4

k_s = 10000.0
k_d = ti.field(dtype=ti.f32, shape=())

gravity = ti.Vector([0.0, -9.8, 0.0])
max_velocity = 50.0

# Structural springs only
num_springs = 2 * N * (N - 1)

# =========================
# Taichi fields
# =========================

x = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)
v = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)
f = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)

x_next = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)
v_next = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)
f_next = ti.Vector.field(3, dtype=ti.f32, shape=num_particles)

is_fixed = ti.field(dtype=ti.i32, shape=num_particles)

spring_a = ti.field(dtype=ti.i32, shape=num_springs)
spring_b = ti.field(dtype=ti.i32, shape=num_springs)
spring_rest = ti.field(dtype=ti.f32, shape=num_springs)

line_indices = ti.field(dtype=ti.i32, shape=num_springs * 2)


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
def add_spring_force(pos, force, sid):
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

        px = (j - (N - 1) * 0.5) * spacing + 0.10
        py = 0.62 - i * spacing
        pz = 0.0

        x[idx] = ti.Vector([px, py, pz])
        v[idx] = ti.Vector([0.0, 0.0, 0.0])
        f[idx] = ti.Vector([0.0, 0.0, 0.0])

        x_next[idx] = x[idx]
        v_next[idx] = v[idx]
        f_next[idx] = f[idx]

        fixed = 0

        # Fix two upper corners
        if i == 0 and (j == 0 or j == N - 1):
            fixed = 1

        is_fixed[idx] = fixed


@ti.kernel
def init_springs():
    # Horizontal structural springs
    for i, j in ti.ndrange(N, N - 1):
        sid = i * (N - 1) + j

        a = get_id(i, j)
        b = get_id(i, j + 1)

        spring_a[sid] = a
        spring_b[sid] = b
        spring_rest[sid] = spacing

    # Vertical structural springs
    offset = N * (N - 1)

    for i, j in ti.ndrange(N - 1, N):
        sid = offset + i * N + j

        a = get_id(i, j)
        b = get_id(i + 1, j)

        spring_a[sid] = a
        spring_b[sid] = b
        spring_rest[sid] = spacing


@ti.kernel
def init_render_indices():
    for sid in range(num_springs):
        line_indices[sid * 2] = spring_a[sid]
        line_indices[sid * 2 + 1] = spring_b[sid]


@ti.kernel
def step_explicit():
    # Gravity + damping
    for i in range(num_particles):
        f[i] = mass * gravity - k_d[None] * v[i]

    # Spring forces
    for sid in range(num_springs):
        add_spring_force(x, f, sid)

    # Explicit Euler
    for i in range(num_particles):
        if is_fixed[i] == 0:
            old_v = v[i]

            x[i] = x[i] + old_v * dt

            acc = f[i] / mass
            v[i] = v[i] + acc * dt
            v[i] = clamp_velocity(v[i])
        else:
            v[i] = ti.Vector([0.0, 0.0, 0.0])


@ti.kernel
def step_semi_implicit():
    # Gravity + damping
    for i in range(num_particles):
        f[i] = mass * gravity - k_d[None] * v[i]

    # Spring forces
    for sid in range(num_springs):
        add_spring_force(x, f, sid)

    # Semi-implicit Euler
    for i in range(num_particles):
        if is_fixed[i] == 0:
            acc = f[i] / mass

            v[i] = v[i] + acc * dt
            v[i] = clamp_velocity(v[i])

            x[i] = x[i] + v[i] * dt
        else:
            v[i] = ti.Vector([0.0, 0.0, 0.0])


@ti.kernel
def step_implicit():
    # Prepare predicted state
    for i in range(num_particles):
        x_next[i] = x[i]
        v_next[i] = v[i]

    # Fixed-point iterations
    for _ in ti.static(range(8)):
        for i in range(num_particles):
            f_next[i] = mass * gravity - k_d[None] * v_next[i]

        for sid in range(num_springs):
            add_spring_force(x_next, f_next, sid)

        for i in range(num_particles):
            if is_fixed[i] == 0:
                acc = f_next[i] / mass

                v_next[i] = v[i] + acc * dt
                v_next[i] = clamp_velocity(v_next[i])

                x_next[i] = x[i] + v_next[i] * dt
            else:
                v_next[i] = ti.Vector([0.0, 0.0, 0.0])
                x_next[i] = x[i]

    # Apply predicted state
    for i in range(num_particles):
        if is_fixed[i] == 0:
            x[i] = x_next[i]
            v[i] = v_next[i]
        else:
            v[i] = ti.Vector([0.0, 0.0, 0.0])


def reset_cloth():
    init_particles()
    init_springs()
    init_render_indices()


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
        "Games101 - Mass Spring System",
        res=(900, 900),
        vsync=True
    )

    canvas = window.get_canvas()
    scene = ti.ui.Scene()
    camera = ti.ui.Camera()

    camera.position(0.10, 0.02, 2.30)
    camera.lookat(0.10, 0.02, 0.0)
    camera.up(0.0, 1.0, 0.0)
    camera.fov(48)

    method = 1
    paused = False

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

        gui = window.get_gui()

        with gui.sub_window("Control Panel", 0.02, 0.02, 0.36, 0.36):
            gui.text("Integration Method:")

            if gui.button(("[*] " if method == 0 else "[ ] ") + "Explicit Euler (Explosive)"):
                method = 0

            if gui.button(("[*] " if method == 1 else "[ ] ") + "Semi-Implicit Euler (Stable)"):
                method = 1

            if gui.button(("[*] " if method == 2 else "[ ] ") + "Implicit Euler (Damped)"):
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
            if gui.button("Pause Simulation" if not paused else "Resume Simulation"):
                paused = not paused

            if gui.button("Reset Cloth"):
                reset_cloth()

            gui.text("")
            gui.text("Shortcuts: 1 / 2 / 3 switch methods")
            gui.text("Space: pause, R: reset")
            gui.text("Right mouse drag: rotate view")

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
            x,
            indices=line_indices,
            color=(0.85, 0.85, 0.85),
            width=1.2
        )

        scene.particles(
            x,
            radius=0.0105,
            color=(0.0, 0.65, 1.0)
        )

        canvas.scene(scene)
        window.show()


if __name__ == "__main__":
    main()