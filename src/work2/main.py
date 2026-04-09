import taichi as ti
import math

# 1. 基本配置

ti.init(arch=ti.cpu)

# 将窗口宽高抽取出来，避免投影矩阵里的 aspect_ratio 写死
WIDTH, HEIGHT = 700, 700
ASPECT_RATIO = WIDTH / HEIGHT

# 三角形顶点（3个三维点）
vertices = ti.Vector.field(3, dtype=ti.f32, shape=3)

# 投影到屏幕后的二维坐标
screen_coords = ti.Vector.field(2, dtype=ti.f32, shape=3)


# 2. 模型矩阵：分别实现绕 X/Y/Z 轴旋转
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
    """
    模型变换矩阵
    axis = 0 -> 绕 X 轴旋转
    axis = 1 -> 绕 Y 轴旋转
    axis = 2 -> 绕 Z 轴旋转（基础要求）
    """
    # 关键修复：
    # Taichi 不支持在动态 if 中直接 return
    # 所以这里使用“先赋值，后统一 return”的写法
    model = ti.Matrix.identity(ti.f32, 4)

    # 在基础要求“绕 Z 轴旋转”之外，扩展为支持三轴切换
    if axis == 0:
        model = get_rotation_x(angle)
    elif axis == 1:
        model = get_rotation_y(angle)
    else:
        model = get_rotation_z(angle)

    return model


# 3. 视图矩阵
@ti.func
def get_view_matrix(eye_pos):
    """
    视图变换矩阵：将相机平移到原点
    """
    return ti.Matrix([
        [1.0, 0.0, 0.0, -eye_pos[0]],
        [0.0, 1.0, 0.0, -eye_pos[1]],
        [0.0, 0.0, 1.0, -eye_pos[2]],
        [0.0, 0.0, 0.0, 1.0]
    ])


# 4. 投影矩阵
@ti.func
def get_projection_matrix(eye_fov: ti.f32, aspect_ratio: ti.f32, zNear: ti.f32, zFar: ti.f32):
    """
    透视投影矩阵
    过程：
    1. 透视平截头体 -> 正交长方体
    2. 正交长方体 -> 标准立方体 [-1, 1]^3
    """
    # 在右手坐标系中，相机看向 -Z 方向
    # 因此 near / far 在实际坐标里取负值
    n = -zNear
    f = -zFar

    # 由视场角和宽高比计算视锥体边界
    fov_rad = eye_fov * math.pi / 180.0
    t = ti.tan(fov_rad / 2.0) * ti.abs(n)
    b = -t
    r = aspect_ratio * t
    l = -r

    # 第一步：透视到正交
    M_p2o = ti.Matrix([
        [n,   0.0,   0.0,    0.0],
        [0.0, n,     0.0,    0.0],
        [0.0, 0.0, n + f, -n * f],
        [0.0, 0.0,   1.0,    0.0]
    ])

    # 第二步：正交投影（缩放）
    M_ortho_scale = ti.Matrix([
        [2.0 / (r - l), 0.0, 0.0, 0.0],
        [0.0, 2.0 / (t - b), 0.0, 0.0],
        [0.0, 0.0, 2.0 / (n - f), 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

    # 第二步：正交投影（平移）
    M_ortho_trans = ti.Matrix([
        [1.0, 0.0, 0.0, -(r + l) / 2.0],
        [0.0, 1.0, 0.0, -(t + b) / 2.0],
        [0.0, 0.0, 1.0, -(n + f) / 2.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

    M_ortho = M_ortho_scale @ M_ortho_trans
    return M_ortho @ M_p2o


# 5. MVP 变换
@ti.kernel
def compute_transform(angle: ti.f32, axis: ti.i32):
    """
    对三角形三个顶点做 MVP 变换，并映射到屏幕坐标
    """
    eye_pos = ti.Vector([0.0, 0.0, 5.0])

    model = get_model_matrix(angle, axis)
    view = get_view_matrix(eye_pos)

    # 不再把 aspect_ratio 写死为 1.0，而是根据窗口大小动态确定
    proj = get_projection_matrix(45.0, ASPECT_RATIO, 0.1, 50.0)

    # 按列向量右乘原则：MVP = P @ V @ M
    mvp = proj @ view @ model

    for i in range(3):
        v = vertices[i]

        # 补成齐次坐标
        v4 = ti.Vector([v[0], v[1], v[2], 1.0])

        # 裁剪空间坐标
        v_clip = mvp @ v4

        # 透视除法：得到标准设备坐标 NDC
        v_ndc = v_clip / v_clip[3]

        # 视口变换：[-1, 1] -> [0, 1]
        screen_coords[i][0] = (v_ndc[0] + 1.0) / 2.0
        screen_coords[i][1] = (v_ndc[1] + 1.0) / 2.0


def axis_name(axis):
    if axis == 0:
        return "X"
    elif axis == 1:
        return "Y"
    else:
        return "Z"


# 6. 主程序
def main():
    # 初始化三角形顶点
    vertices[0] = [2.0, 0.0, -2.0]
    vertices[1] = [0.0, 2.0, -2.0]
    vertices[2] = [-2.0, 0.0, -2.0]

    gui = ti.GUI("3D MVP Transformation", res=(WIDTH, HEIGHT))

    angle = 0.0
    axis = 2          # 默认绕 Z 轴旋转，符合实验基础要求
    auto_rotate = False

    while gui.running:
        if gui.get_event(ti.GUI.PRESS):
            if gui.event.key == 'a':
                angle += 10.0
            elif gui.event.key == 'd':
                angle -= 10.0
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
            angle += 1.0

        compute_transform(angle, axis)

        a = screen_coords[0]
        b = screen_coords[1]
        c = screen_coords[2]

        # 每帧清屏，避免画面残留
        gui.clear(0x112F41)

        # 绘制彩色线框三角形
        gui.line(a, b, radius=2, color=0xFF0000)
        gui.line(b, c, radius=2, color=0x00FF00)
        gui.line(c, a, radius=2, color=0x0000FF)

        # 状态显示
        gui.text(f"Angle: {angle:.1f}", pos=(0.02, 0.95), color=0xFFFFFF)
        gui.text(f"Axis: {axis_name(axis)}", pos=(0.02, 0.91), color=0xFFFFFF)
        gui.text(f"Auto Rotate: {'ON' if auto_rotate else 'OFF'}",
                 pos=(0.02, 0.87), color=0xFFFFFF)
        gui.text("A/D rotate | X/Y/Z axis | R reset | SPACE auto | ESC quit",
                 pos=(0.02, 0.03), color=0xFFFFFF)

        gui.show()


if __name__ == '__main__':
    main()