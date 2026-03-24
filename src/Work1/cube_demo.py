import taichi as ti
import math

ti.init(arch=ti.cpu)

# =========================
# 1. 基本配置
# =========================
WIDTH, HEIGHT = 800, 800
ASPECT_RATIO = WIDTH / HEIGHT

# 立方体 8 个顶点
vertices = ti.Vector.field(3, dtype=ti.f32, shape=8)

# 投影到屏幕后的二维坐标
screen_coords = ti.Vector.field(2, dtype=ti.f32, shape=8)


# =========================
# 2. 模型矩阵：绕 X / Y / Z 轴旋转
# =========================
@ti.func
def get_rotation_x(angle: ti.f32):
    rad = angle * math.pi / 180.0
    c = ti.cos(rad)
    s = ti.sin(rad)
    return ti.Matrix([
        [1.0, 0.0, 0.0, 0.0],
        [0.0,  c, -s, 0.0],
        [0.0,  s,  c, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])


@ti.func
def get_rotation_y(angle: ti.f32):
    rad = angle * math.pi / 180.0
    c = ti.cos(rad)
    s = ti.sin(rad)
    return ti.Matrix([
        [ c, 0.0,  s, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s, 0.0,  c, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])


@ti.func
def get_rotation_z(angle: ti.f32):
    rad = angle * math.pi / 180.0
    c = ti.cos(rad)
    s = ti.sin(rad)
    return ti.Matrix([
        [c, -s, 0.0, 0.0],
        [s,  c, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])


@ti.func
def get_model_matrix(angle: ti.f32, axis: ti.i32):
    model = ti.Matrix.identity(ti.f32, 4)

    # Taichi 中不要在动态 if 里直接 return
    if axis == 0:
        model = get_rotation_x(angle)
    elif axis == 1:
        model = get_rotation_y(angle)
    else:
        model = get_rotation_z(angle)

    return model


# =========================
# 3. 视图矩阵
# =========================
@ti.func
def get_view_matrix(eye_pos):
    return ti.Matrix([
        [1.0, 0.0, 0.0, -eye_pos[0]],
        [0.0, 1.0, 0.0, -eye_pos[1]],
        [0.0, 0.0, 1.0, -eye_pos[2]],
        [0.0, 0.0, 0.0, 1.0]
    ])


# =========================
# 4. 投影矩阵
# =========================
@ti.func
def get_projection_matrix(eye_fov: ti.f32, aspect_ratio: ti.f32, zNear: ti.f32, zFar: ti.f32):
    n = -zNear
    f = -zFar

    fov_rad = eye_fov * math.pi / 180.0
    t = ti.tan(fov_rad / 2.0) * ti.abs(n)
    b = -t
    r = aspect_ratio * t
    l = -r

    M_p2o = ti.Matrix([
        [n,   0.0,   0.0,    0.0],
        [0.0, n,     0.0,    0.0],
        [0.0, 0.0, n + f, -n * f],
        [0.0, 0.0,   1.0,    0.0]
    ])

    M_ortho_scale = ti.Matrix([
        [2.0 / (r - l), 0.0, 0.0, 0.0],
        [0.0, 2.0 / (t - b), 0.0, 0.0],
        [0.0, 0.0, 2.0 / (n - f), 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

    M_ortho_trans = ti.Matrix([
        [1.0, 0.0, 0.0, -(r + l) / 2.0],
        [0.0, 1.0, 0.0, -(t + b) / 2.0],
        [0.0, 0.0, 1.0, -(n + f) / 2.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

    M_ortho = M_ortho_scale @ M_ortho_trans
    return M_ortho @ M_p2o


# =========================
# 5. MVP 变换
# =========================
@ti.kernel
def compute_transform(angle: ti.f32, axis: ti.i32):
    eye_pos = ti.Vector([0.0, 0.0, 5.0])

    model = get_model_matrix(angle, axis)
    view = get_view_matrix(eye_pos)
    proj = get_projection_matrix(50.0, ASPECT_RATIO, 0.1, 50.0)

    mvp = proj @ view @ model

    for i in range(8):
        v = vertices[i]
        v4 = ti.Vector([v[0], v[1], v[2], 1.0])
        v_clip = mvp @ v4
        v_ndc = v_clip / v_clip[3]

        screen_coords[i][0] = (v_ndc[0] + 1.0) / 2.0
        screen_coords[i][1] = (v_ndc[1] + 1.0) / 2.0


def axis_name(axis):
    return ["X", "Y", "Z"][axis]


def init_cube():
    # 中心在原点，边长为 2
    cube_points = [
        [-1.0, -1.0, -1.0],
        [ 1.0, -1.0, -1.0],
        [ 1.0,  1.0, -1.0],
        [-1.0,  1.0, -1.0],
        [-1.0, -1.0,  1.0],
        [ 1.0, -1.0,  1.0],
        [ 1.0,  1.0,  1.0],
        [-1.0,  1.0,  1.0],
    ]
    for i in range(8):
        vertices[i] = cube_points[i]


def main():
    init_cube()

    # 12 条边
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),   # 后面
        (4, 5), (5, 6), (6, 7), (7, 4),   # 前面
        (0, 4), (1, 5), (2, 6), (3, 7)    # 连接前后
    ]

    gui = ti.GUI("3D Cube MVP Demo", res=(WIDTH, HEIGHT))

    angle = 0.0
    axis = 1           # 默认绕 Y 轴转，立体感更明显
    auto_rotate = True

    while gui.running:
        if gui.get_event(ti.GUI.PRESS):
            if gui.event.key == 'a':
                angle += 8.0
            elif gui.event.key == 'd':
                angle -= 8.0
            elif gui.event.key == 'r':
                angle = 0.0
            elif gui.event.key == 'x':
                axis = 0
            elif gui.event.key == 'y':
                axis = 1
            elif gui.event.key == 'z':
                axis = 2
            elif gui.event.key == ti.GUI.SPACE:
                auto_rotate = not auto_rotate
            elif gui.event.key == ti.GUI.ESCAPE:
                gui.running = False

        if auto_rotate:
            angle += 0.8

        compute_transform(angle, axis)

        gui.clear(0x112F41)

        # 画立方体边框
        for i, j in edges:
            p1 = screen_coords[i]
            p2 = screen_coords[j]
            gui.line(p1, p2, radius=2, color=0x7DD3FC)

        # 画顶点
        for i in range(8):
            gui.circle(screen_coords[i], radius=4, color=0xF8FAFC)

        gui.text("3D Cube Perspective Rotation", pos=(0.03, 0.96), color=0xFFFFFF)
        gui.text(f"Angle: {angle:.1f}", pos=(0.03, 0.92), color=0xFFFFFF)
        gui.text(f"Axis: {axis_name(axis)}", pos=(0.03, 0.88), color=0xFFFFFF)
        gui.text(f"Auto Rotate: {'ON' if auto_rotate else 'OFF'}", pos=(0.03, 0.84), color=0xFFFFFF)
        gui.text("A/D rotate | X/Y/Z axis | R reset | SPACE auto | ESC quit",
                 pos=(0.03, 0.03), color=0xFFFFFF)

        gui.show()


if __name__ == '__main__':
    main()