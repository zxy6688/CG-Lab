import taichi as ti
import numpy as np
import math

# 选做 1: Anti-Aliased Bezier Curve
#
# 功能：
# 1. 鼠标左键添加控制点
# 2. 鼠标右键撤销最后一个控制点
# 3. C 键清空控制点
# 4. A 键切换：普通单像素渲染 / 反走样渲染
# 5. 显示控制点、控制折线、贝塞尔曲线
#
# 说明：
# 曲线点仍然在 CPU 端用 De Casteljau 算法计算
# 再在 CPU 端将曲线样本光栅化到一张 RGB 图像上
# 最后一次性传给 GPU 显示
# 反走样的核心是：一个浮点曲线点不只影响一个像素，而是对周围 3x3 像素
# 按距离分配不同权重，从而获得更平滑的边缘

ti.init(arch=ti.gpu)

WIDTH = 800
HEIGHT = 800
NUM_SEGMENTS = 1400
MAX_CONTROL_POINTS = 100

BG_COLOR = np.array([0.05, 0.06, 0.09], dtype=np.float32)
CURVE_COLOR = np.array([0.20, 0.90, 0.85], dtype=np.float32)

pixels = ti.Vector.field(3, dtype=ti.f32, shape=(WIDTH, HEIGHT))
gui_points = ti.Vector.field(2, dtype=ti.f32, shape=MAX_CONTROL_POINTS)
gui_indices = ti.field(dtype=ti.i32, shape=MAX_CONTROL_POINTS * 2)


def de_casteljau(points, t):
    """
    递归版 De Casteljau 算法
    points: [[x, y], ...]
    t: [0, 1]
    return: np.array([x, y], dtype=np.float32)
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


def sample_bezier(control_points, num_segments):
    """
    在 [0,1] 上均匀采样贝塞尔曲线
    """
    if len(control_points) < 2:
        return np.zeros((0, 2), dtype=np.float32)

    curve = np.zeros((num_segments + 1, 2), dtype=np.float32)
    for i in range(num_segments + 1):
        t = i / num_segments
        curve[i] = de_casteljau(control_points, t)
    return curve


def rasterize_curve_basic(image, curve_points):
    """
    基础渲染：每个曲线点只点亮一个像素
    """
    for pt in curve_points:
        x = int(pt[0] * (WIDTH - 1))
        y = int(pt[1] * (HEIGHT - 1))
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            image[x, y] = CURVE_COLOR


def rasterize_curve_antialias(image, curve_points, sigma=0.75):
    """
    反走样渲染：
    对每个浮点曲线点，考察其周围 3x3 像素邻域，
    根据像素中心到曲线点的距离分配权重，使用高斯衰减实现平滑边缘。
    """
    for pt in curve_points:
        x_real = pt[0] * (WIDTH - 1)
        y_real = pt[1] * (HEIGHT - 1)

        cx = int(math.floor(x_real))
        cy = int(math.floor(y_real))

        for ix in range(cx - 1, cx + 2):
            for iy in range(cy - 1, cy + 2):
                if 0 <= ix < WIDTH and 0 <= iy < HEIGHT:
                    px = ix + 0.5
                    py = iy + 0.5

                    dx = px - x_real
                    dy = py - y_real
                    dist2 = dx * dx + dy * dy

                    # 高斯衰减权重
                    w = math.exp(-dist2 / (2.0 * sigma * sigma))

                    # 从背景色平滑过渡到曲线色
                    target = BG_COLOR * (1.0 - w) + CURVE_COLOR * w

                    # 取逐通道最大值，避免多次采样使颜色变暗
                    image[ix, iy] = np.maximum(image[ix, iy], target)


def build_frame(control_points, aa_enabled):
    """
    根据当前控制点和抗锯齿开关，生成整张图像
    """
    image = np.zeros((WIDTH, HEIGHT, 3), dtype=np.float32)
    image[:] = BG_COLOR

    if len(control_points) >= 2:
        curve_points = sample_bezier(control_points, NUM_SEGMENTS)
        if aa_enabled:
            rasterize_curve_antialias(image, curve_points)
        else:
            rasterize_curve_basic(image, curve_points)

    return image


def update_gui_buffers(control_points):
    """
    使用固定大小对象池更新控制点和控制折线索引
    """
    count = len(control_points)

    # 控制点对象池：先全部放到屏幕外
    points_np = np.full((MAX_CONTROL_POINTS, 2), -10.0, dtype=np.float32)
    if count > 0:
        points_np[:count] = np.array(control_points, dtype=np.float32)
    gui_points.from_numpy(points_np)

    # 控制折线索引对象池
    indices_np = np.zeros(MAX_CONTROL_POINTS * 2, dtype=np.int32)
    idx_list = []
    for i in range(count - 1):
        idx_list.extend([i, i + 1])

    if len(idx_list) > 0:
        indices_np[:len(idx_list)] = np.array(idx_list, dtype=np.int32)

    gui_indices.from_numpy(indices_np)


def main():
    window = ti.ui.Window("Bezier Curve - Anti Aliasing", (WIDTH, HEIGHT))
    canvas = window.get_canvas()

    control_points = []
    aa_enabled = True
    dirty = True

    print("===== Anti-Aliased Bezier Curve =====")
    print("左键：添加控制点")
    print("右键：撤销最后一个控制点")
    print("C 键：清空")
    print("A 键：切换 普通渲染 / 反走样渲染")
    print("当前模式：Anti-Aliasing ON")

    frame_np = np.zeros((WIDTH, HEIGHT, 3), dtype=np.float32)
    frame_np[:] = BG_COLOR
    pixels.from_numpy(frame_np)

    while window.running:
        for e in window.get_events(ti.ui.PRESS):
            if e.key == ti.ui.LMB:
                if len(control_points) < MAX_CONTROL_POINTS:
                    pos = window.get_cursor_pos()
                    control_points.append([pos[0], pos[1]])
                    dirty = True
                    print(f"Added control point: {pos}")

            elif e.key == ti.ui.RMB:
                if control_points:
                    removed = control_points.pop()
                    dirty = True
                    print(f"Removed control point: {removed}")

            elif e.key == 'c' or e.key == 'C':
                control_points = []
                dirty = True
                print("Canvas cleared.")

            elif e.key == 'a' or e.key == 'A':
                aa_enabled = not aa_enabled
                dirty = True
                print(f"Anti-Aliasing: {'ON' if aa_enabled else 'OFF'}")

        if dirty:
            frame_np = build_frame(control_points, aa_enabled)
            pixels.from_numpy(frame_np)
            update_gui_buffers(control_points)
            dirty = False

        canvas.set_image(pixels)

        count = len(control_points)
        if count >= 2:
            canvas.lines(
                gui_points,
                width=0.002,
                indices=gui_indices,
                color=(0.65, 0.65, 0.65)
            )

        if count > 0:
            canvas.circles(
                gui_points,
                radius=0.008,
                color=(1.0, 0.35, 0.25)
            )

        window.show()


if __name__ == "__main__":
    main()