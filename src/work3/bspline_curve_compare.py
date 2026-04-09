import taichi as ti
import numpy as np
import math

# 选做2: Bezier vs Uniform Cubic B-Spline
#
# 功能：
# 1. 鼠标左键添加控制点
# 2. 鼠标右键撤销最后一个控制点
# 3. C 键清空
# 4. M 键切换显示模式：compare / bezier / bspline
# 5. 同一套控制点上比较 Bezier 和 B-Spline 的形态差异
#
# 说明：
# Bezier：使用所有控制点，通过 De Casteljau 算法生成一条曲线
# B-Spline：使用均匀三次 B 样条，每 4 个相邻控制点生成一段曲线
# 该程序适合观察“Bezier 全局控制”与“B-Spline 局部控制”的差别


ti.init(arch=ti.gpu)

WIDTH = 800
HEIGHT = 800
NUM_SEGMENTS = 1400
MAX_CONTROL_POINTS = 100

BG_COLOR = np.array([0.05, 0.06, 0.09], dtype=np.float32)
BEZIER_COLOR = np.array([0.10, 0.95, 0.25], dtype=np.float32)
BSPLINE_COLOR = np.array([0.30, 0.65, 1.00], dtype=np.float32)

pixels = ti.Vector.field(3, dtype=ti.f32, shape=(WIDTH, HEIGHT))
gui_points = ti.Vector.field(2, dtype=ti.f32, shape=MAX_CONTROL_POINTS)
gui_indices = ti.field(dtype=ti.i32, shape=MAX_CONTROL_POINTS * 2)


def de_casteljau(points, t):
    """
    递归版 De Casteljau 算法
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
    使用所有控制点采样一条贝塞尔曲线
    """
    if len(control_points) < 2:
        return np.zeros((0, 2), dtype=np.float32)

    curve = np.zeros((num_segments + 1, 2), dtype=np.float32)
    for i in range(num_segments + 1):
        t = i / num_segments
        curve[i] = de_casteljau(control_points, t)
    return curve


def bspline_basis(u):
    """
    均匀三次 B 样条的 4 个基函数
    u in [0, 1]
    """
    b0 = ((1.0 - u) ** 3) / 6.0
    b1 = (3.0 * u**3 - 6.0 * u**2 + 4.0) / 6.0
    b2 = (-3.0 * u**3 + 3.0 * u**2 + 3.0 * u + 1.0) / 6.0
    b3 = (u**3) / 6.0
    return b0, b1, b2, b3


def sample_uniform_cubic_bspline(control_points, total_segments):
    """
    采样均匀三次 B 样条曲线
    n 个控制点可生成 n-3 段局部曲线
    """
    n = len(control_points)
    if n < 4:
        return np.zeros((0, 2), dtype=np.float32)

    segment_count = n - 3
    samples_per_segment = max(10, total_segments // segment_count)

    result = []

    for s in range(segment_count):
        p0 = np.array(control_points[s], dtype=np.float32)
        p1 = np.array(control_points[s + 1], dtype=np.float32)
        p2 = np.array(control_points[s + 2], dtype=np.float32)
        p3 = np.array(control_points[s + 3], dtype=np.float32)

        # 前面各段不包含终点，最后一段包含终点，避免重复拼接点
        step_count = samples_per_segment if s < segment_count - 1 else samples_per_segment + 1

        for j in range(step_count):
            u = j / samples_per_segment
            b0, b1, b2, b3 = bspline_basis(u)
            pt = b0 * p0 + b1 * p1 + b2 * p2 + b3 * p3
            result.append(pt)

    return np.array(result, dtype=np.float32)


def rasterize_curve_antialias(image, curve_points, color, sigma=0.75):
    """
    使用 3x3 邻域 + 高斯衰减的方式光栅化曲线
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

                    w = math.exp(-dist2 / (2.0 * sigma * sigma))
                    target = BG_COLOR * (1.0 - w) + color * w

                    image[ix, iy] = np.maximum(image[ix, iy], target)


def build_frame(control_points, display_mode):
    """
    根据当前控制点和显示模式生成图像
    display_mode:
        - "compare" : 同时显示 Bezier 和 B-Spline
        - "bezier"  : 只显示 Bezier
        - "bspline" : 只显示 B-Spline
    """
    image = np.zeros((WIDTH, HEIGHT, 3), dtype=np.float32)
    image[:] = BG_COLOR

    if len(control_points) >= 2 and display_mode in ("compare", "bezier"):
        bezier_curve = sample_bezier(control_points, NUM_SEGMENTS)
        rasterize_curve_antialias(image, bezier_curve, BEZIER_COLOR)

    if len(control_points) >= 4 and display_mode in ("compare", "bspline"):
        bspline_curve = sample_uniform_cubic_bspline(control_points, NUM_SEGMENTS)
        rasterize_curve_antialias(image, bspline_curve, BSPLINE_COLOR)

    return image


def update_gui_buffers(control_points):
    """
    更新控制点和控制折线对象池
    """
    count = len(control_points)

    points_np = np.full((MAX_CONTROL_POINTS, 2), -10.0, dtype=np.float32)
    if count > 0:
        points_np[:count] = np.array(control_points, dtype=np.float32)
    gui_points.from_numpy(points_np)

    indices_np = np.zeros(MAX_CONTROL_POINTS * 2, dtype=np.int32)
    idx_list = []
    for i in range(count - 1):
        idx_list.extend([i, i + 1])

    if len(idx_list) > 0:
        indices_np[:len(idx_list)] = np.array(idx_list, dtype=np.int32)

    gui_indices.from_numpy(indices_np)


def main():
    window = ti.ui.Window("Bezier vs B-Spline", (WIDTH, HEIGHT))
    canvas = window.get_canvas()

    control_points = []
    display_modes = ["compare", "bezier", "bspline"]
    mode_idx = 0
    dirty = True

    print("===== Bezier vs B-Spline =====")
    print("左键：添加控制点")
    print("右键：撤销最后一个控制点")
    print("C 键：清空")
    print("M 键：切换显示模式 compare / bezier / bspline")
    print("颜色说明：")
    print("  Bezier  = Green")
    print("  B-Spline = Blue")
    print("当前模式：compare")

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

            elif e.key == 'm' or e.key == 'M':
                mode_idx = (mode_idx + 1) % len(display_modes)
                dirty = True
                print(f"Display mode: {display_modes[mode_idx]}")

        if dirty:
            frame_np = build_frame(control_points, display_modes[mode_idx])
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