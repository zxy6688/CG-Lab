import math
import numpy as np
import taichi as ti

ti.init(arch=ti.gpu)

WIDTH, HEIGHT = 1200, 900
ASPECT = WIDTH / HEIGHT

BG_COLOR = 0x0F1220
EDGE_BASE = 0x7CFFCB
EDGE_DARK = 0x2B5C56
VERTEX_COLOR = 0xF9F871
TEXT_COLOR = 0xEAEAF2
X_AXIS_COLOR = 0xFF6B6B
Y_AXIS_COLOR = 0x4ADE80
Z_AXIS_COLOR = 0x60A5FA

FOV_DEG = 55.0
CAMERA_POS = np.array([0.0, 0.0, 5.5], dtype=np.float64)

CUBE_VERTICES = np.array([
    [-1.0, -1.0, -1.0],
    [1.0, -1.0, -1.0],
    [1.0, 1.0, -1.0],
    [-1.0, 1.0, -1.0],
    [-1.0, -1.0, 1.0],
    [1.0, -1.0, 1.0],
    [1.0, 1.0, 1.0],
    [-1.0, 1.0, 1.0],
], dtype=np.float64)

CUBE_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
]

AXIS_POINTS = np.array([
    [0.0, 0.0, 0.0], [2.4, 0.0, 0.0],
    [0.0, 0.0, 0.0], [0.0, 2.4, 0.0],
    [0.0, 0.0, 0.0], [0.0, 0.0, 2.4],
], dtype=np.float64)


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def hex_to_rgb(color):
    return np.array([
        (color >> 16) & 255,
        (color >> 8) & 255,
        color & 255
    ], dtype=np.float64)


def rgb_to_hex(rgb):
    rgb = np.clip(np.round(rgb), 0, 255).astype(np.int32)
    return (int(rgb[0]) << 16) | (int(rgb[1]) << 8) | int(rgb[2])


def mix_color(c1, c2, t):
    return rgb_to_hex(hex_to_rgb(c1) * (1.0 - t) + hex_to_rgb(c2) * t)


def quat_normalize(q):
    n = np.linalg.norm(q)
    if n < 1e-12:
        return np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)
    return q / n


def quat_mul(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2

    return np.array([
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
    ], dtype=np.float64)


def axis_angle_to_quat(axis, deg):
    rad = math.radians(deg)
    axis = np.array(axis, dtype=np.float64)
    axis = axis / np.linalg.norm(axis)

    s = math.sin(rad / 2.0)

    return quat_normalize(np.array([
        math.cos(rad / 2.0),
        axis[0] * s,
        axis[1] * s,
        axis[2] * s
    ], dtype=np.float64))


def quat_from_euler_xyz(rx_deg, ry_deg, rz_deg):
    qx = axis_angle_to_quat([1, 0, 0], rx_deg)
    qy = axis_angle_to_quat([0, 1, 0], ry_deg)
    qz = axis_angle_to_quat([0, 0, 1], rz_deg)
    return quat_normalize(quat_mul(qz, quat_mul(qy, qx)))


def quat_to_matrix(q):
    w, x, y, z = quat_normalize(q)

    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ], dtype=np.float64)


def slerp(q0, q1, t):
    q0 = quat_normalize(q0)
    q1 = quat_normalize(q1)

    dot = float(np.dot(q0, q1))

    if dot < 0.0:
        q1 = -q1
        dot = -dot

    if dot > 0.9995:
        return quat_normalize(q0 + t * (q1 - q0))

    theta_0 = math.acos(clamp(dot, -1.0, 1.0))
    theta = theta_0 * t
    q2 = quat_normalize(q1 - q0 * dot)

    return quat_normalize(q0 * math.cos(theta) + q2 * math.sin(theta))


def transform_points(points, model_rot):
    return points @ model_rot.T


def view_transform(points_world):
    return points_world - CAMERA_POS


def project_points(points_view):
    focal = 1.0 / math.tan(math.radians(FOV_DEG) / 2.0)

    projected = []
    depths = []

    for p in points_view:
        z_cam = -p[2]

        if z_cam < 1e-4:
            projected.append(np.array([-10.0, -10.0]))
            depths.append(-1e9)
            continue

        x_ndc = (p[0] * focal / ASPECT) / z_cam
        y_ndc = (p[1] * focal) / z_cam

        x_screen = 0.5 + 0.5 * x_ndc
        y_screen = 0.5 + 0.5 * y_ndc

        projected.append(np.array([x_screen, y_screen]))
        depths.append(z_cam)

    return np.array(projected), np.array(depths)


def draw_axes(gui, rot):
    pts_world = transform_points(AXIS_POINTS, rot)
    pts_view = view_transform(pts_world)
    pts_2d, _ = project_points(pts_view)

    axis_colors = [X_AXIS_COLOR, Y_AXIS_COLOR, Z_AXIS_COLOR]
    labels = ["X", "Y", "Z"]

    for i in range(3):
        p0 = pts_2d[2 * i]
        p1 = pts_2d[2 * i + 1]

        gui.line(tuple(p0), tuple(p1), radius=2.5, color=axis_colors[i])
        gui.circle(tuple(p1), radius=4, color=axis_colors[i])
        gui.text(labels[i], pos=(p1[0] + 0.01, p1[1] + 0.005), color=axis_colors[i])


def draw_cube(gui, vertices_world):
    vertices_view = view_transform(vertices_world)
    verts_2d, depths = project_points(vertices_view)

    edge_order = []

    for a, b in CUBE_EDGES:
        avg_depth = (depths[a] + depths[b]) * 0.5
        edge_order.append((avg_depth, a, b))

    edge_order.sort(reverse=True)

    for avg_depth, a, b in edge_order:
        p0 = verts_2d[a]
        p1 = verts_2d[b]

        if not ((-0.2 <= p0[0] <= 1.2 and -0.2 <= p0[1] <= 1.2) or
                (-0.2 <= p1[0] <= 1.2 and -0.2 <= p1[1] <= 1.2)):
            continue

        depth_t = clamp((avg_depth - 3.2) / 4.0, 0.0, 1.0)
        main_color = mix_color(EDGE_DARK, EDGE_BASE, depth_t)

        gui.line(tuple(p0), tuple(p1), radius=4.5, color=0x16202A)
        gui.line(tuple(p0), tuple(p1), radius=2.2, color=main_color)

    vertex_order = sorted(
        [(depths[i], i) for i in range(len(depths))],
        reverse=True
    )

    for depth, i in vertex_order:
        p = verts_2d[i]
        depth_t = clamp((depth - 3.2) / 4.0, 0.0, 1.0)
        r = 2.2 + 2.4 * depth_t

        gui.circle(tuple(p), radius=r + 2.0, color=0x16202A)
        gui.circle(tuple(p), radius=r, color=VERTEX_COLOR)


def main():
    gui = ti.GUI(
        "Work2 Option 2 - 3D Cube Rotation Interpolation",
        res=(WIDTH, HEIGHT),
        background_color=BG_COLOR
    )

    q0 = quat_from_euler_xyz(0.0, 0.0, 0.0)
    q1 = quat_from_euler_xyz(75.0, 215.0, 38.0)

    paused = False
    manual_mode = False
    t_manual = 0.0
    time_acc = 0.0
    speed = 1.1

    while gui.running:
        dt = 1.0 / 60.0

        for e in gui.get_events(ti.GUI.PRESS):
            if e.key == ti.GUI.ESCAPE:
                gui.running = False
            elif e.key == ti.GUI.SPACE:
                paused = not paused
            elif e.key == 'm':
                manual_mode = not manual_mode
            elif e.key == 'r':
                t_manual = 0.0
                time_acc = 0.0
            elif e.key == 'a':
                manual_mode = True
                t_manual = clamp(t_manual - 0.03, 0.0, 1.0)
            elif e.key == 'd':
                manual_mode = True
                t_manual = clamp(t_manual + 0.03, 0.0, 1.0)
            elif e.key == 'w':
                speed = min(speed + 0.1, 3.0)
            elif e.key == 's':
                speed = max(speed - 0.1, 0.2)

        if not paused and not manual_mode:
            time_acc += dt * speed

        t = t_manual if manual_mode else 0.5 + 0.5 * math.sin(time_acc)
        q_t = slerp(q0, q1, t)

        rot_interp = quat_to_matrix(q_t)
        rot_extra = quat_to_matrix(
            quat_from_euler_xyz(
                12.0 * math.sin(time_acc * 0.7),
                18.0 * math.cos(time_acc * 0.45),
                0.0
            )
        )

        model_rot = rot_extra @ rot_interp
        vertices_world = transform_points(CUBE_VERTICES, model_rot)

        gui.clear(BG_COLOR)
        draw_axes(gui, model_rot)
        draw_cube(gui, vertices_world)

        gui.text("3D Cube + Rotation Interpolation (SLERP)", pos=(0.03, 0.95), color=TEXT_COLOR)
        gui.text(f"t = {t:.3f}", pos=(0.03, 0.91), color=TEXT_COLOR)
        gui.text(f"mode = {'manual' if manual_mode else 'auto'}", pos=(0.03, 0.88), color=TEXT_COLOR)
        gui.text(f"speed = {speed:.1f}", pos=(0.03, 0.85), color=TEXT_COLOR)
        gui.text("pose A = (0, 0, 0)", pos=(0.03, 0.80), color=0xB8C0FF)
        gui.text("pose B = (75, 215, 38)", pos=(0.03, 0.77), color=0xB8C0FF)

        gui.text("[Space] pause/resume", pos=(0.72, 0.93), color=TEXT_COLOR)
        gui.text("[M] auto/manual", pos=(0.72, 0.90), color=TEXT_COLOR)
        gui.text("[A/D] adjust t", pos=(0.72, 0.87), color=TEXT_COLOR)
        gui.text("[W/S] speed +/-", pos=(0.72, 0.84), color=TEXT_COLOR)
        gui.text("[R] reset  [Esc] quit", pos=(0.72, 0.81), color=TEXT_COLOR)

        gui.show()


if __name__ == "__main__":
    main()