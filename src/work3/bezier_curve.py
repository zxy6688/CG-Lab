import taichi as ti
import numpy as np

# 计算机图形学 - 实验三
# 实验名称：贝塞尔曲线
# 完成内容：
# 1. 使用 Python + Taichi
# 2. 使用 De Casteljau 算法计算曲线点
# 3. 使用像素缓冲区进行光栅化绘制
# 4. 支持鼠标左键添加控制点
# 5. 支持键盘 C 键清空画布
# 6. 绘制控制点、控制折线、贝塞尔曲线

# Taichi 初始化
ti.init(arch=ti.gpu)

# 常量定义
WIDTH = 800
HEIGHT = 800
NUM_SEGMENTS = 1000
MAX_CONTROL_POINTS = 100

# GPU 缓冲区
# 1. 像素缓冲区：存储最终画面
pixels = ti.Vector.field(3, dtype=ti.f32, shape=(WIDTH, HEIGHT))

# 2. 曲线采样点缓冲区：接收 CPU 计算好的曲线坐标
curve_points_field = ti.Vector.field(2, dtype=ti.f32, shape=NUM_SEGMENTS + 1)

# 3. GUI 控制点对象池
gui_points = ti.Vector.field(2, dtype=ti.f32, shape=MAX_CONTROL_POINTS)

# 4. GUI 控制折线索引对象池
gui_indices = ti.field(dtype=ti.i32, shape=MAX_CONTROL_POINTS * 2)


# De Casteljau 算法
def de_casteljau(points, t):
    """
    使用递归线性插值计算贝塞尔曲线在参数 t 处的点坐标
    points: Python 列表，每个元素是一个二维点 [x, y] 或 (x, y)
    t: [0, 1] 之间的浮点数
    返回值: numpy.array([x, y], dtype=np.float32)
    """
    if len(points) == 1:
        return np.array(points[0], dtype=np.float32)

    next_points = []
    for i in range(len(points) - 1):
        p0 = points[i]
        p1 = points[i + 1]
        x = (1.0 - t) * p0[0] + t * p1[0]
        y = (1.0 - t) * p0[1] + t * p1[1]
        next_points.append([x, y])

    return de_casteljau(next_points, t)


# GPU Kernel
@ti.kernel
def clear_pixels():
    """
    清空像素缓冲区，将背景置为黑色
    """
    for i, j in pixels:
        pixels[i, j] = ti.Vector([0.0, 0.0, 0.0])


@ti.kernel
def draw_curve_kernel(n: ti.i32):
    """
    从 curve_points_field 中读取浮点坐标，
    映射到屏幕像素坐标后点亮对应像素为绿色
    """
    for i in range(n):
        pt = curve_points_field[i]

        x_pixel = ti.cast(pt[0] * WIDTH, ti.i32)
        y_pixel = ti.cast(pt[1] * HEIGHT, ti.i32)

        if 0 <= x_pixel < WIDTH and 0 <= y_pixel < HEIGHT:
            pixels[x_pixel, y_pixel] = ti.Vector([0.0, 1.0, 0.0])


# 主程序
def main():
    window = ti.ui.Window("Bezier Curve", (WIDTH, HEIGHT))
    canvas = window.get_canvas()

    # Python 端控制点列表
    control_points = []

    while window.running:
        # 监听输入事件
        for e in window.get_events(ti.ui.PRESS):
            # 鼠标左键添加控制点
            if e.key == ti.ui.LMB:
                if len(control_points) < MAX_CONTROL_POINTS:
                    pos = window.get_cursor_pos()
                    control_points.append([pos[0], pos[1]])
                    print(f"Added control point: {pos}")

            # 按 C 键清空控制点
            elif e.key == 'c' or e.key == 'C':
                control_points = []
                print("Canvas cleared.")

        # 每一帧先清空像素缓冲区
        clear_pixels()

        current_count = len(control_points)

        # 只有控制点数 >= 2 时才生成曲线
        if current_count >= 2:
            # 1. CPU 端批量计算曲线采样点
            curve_points_np = np.zeros((NUM_SEGMENTS + 1, 2), dtype=np.float32)
            for t_int in range(NUM_SEGMENTS + 1):
                t = t_int / NUM_SEGMENTS
                curve_points_np[t_int] = de_casteljau(control_points, t)

            # 2. 一次性拷贝到 GPU
            curve_points_field.from_numpy(curve_points_np)

            # 3. GPU 并行点亮曲线像素
            draw_curve_kernel(NUM_SEGMENTS + 1)

        # 将 pixels 显示到画布
        canvas.set_image(pixels)

        # 绘制控制点
        if current_count > 0:
            # 对象池技巧：先用屏幕外坐标填满
            points_np = np.full((MAX_CONTROL_POINTS, 2), -10.0, dtype=np.float32)

            # 前 current_count 个位置填入真实控制点
            points_np[:current_count] = np.array(control_points, dtype=np.float32)

            # 上传到 GPU
            gui_points.from_numpy(points_np)

            # 绘制红色控制点
            canvas.circles(gui_points, radius=0.006, color=(1.0, 0.0, 0.0))

        # 绘制控制折线
        if current_count >= 2:
            indices_np = np.zeros(MAX_CONTROL_POINTS * 2, dtype=np.int32)

            idx_list = []
            for i in range(current_count - 1):
                idx_list.extend([i, i + 1])

            indices_np[:len(idx_list)] = np.array(idx_list, dtype=np.int32)

            gui_indices.from_numpy(indices_np)

            # 绘制灰色控制折线
            canvas.lines(
                gui_points,
                width=0.002,
                indices=gui_indices,
                color=(0.5, 0.5, 0.5)
            )

        # 刷新窗口
        window.show()


if __name__ == "__main__":
    main()