import taichi as ti
import numpy as np

ti.init(arch=ti.gpu)

# -------------------- 基本参数 --------------------
W, H = 800, 800
MAX_POINTS = 100
MAX_SAMPLES = 4000
INIT_SAMPLES = 600

BG_COLOR = ti.Vector([0.04, 0.04, 0.06])
CURVE_COLOR = ti.Vector([0.15, 0.90, 0.25])

# -------------------- 显示缓冲区 --------------------
frame_buffer = ti.Vector.field(3, dtype=ti.f32, shape=(W, H))

# 曲线采样点缓冲区（GPU）
curve_buffer = ti.Vector.field(2, dtype=ti.f32, shape=MAX_SAMPLES + 1)

# GUI 控制点与折线缓冲区
control_vis = ti.Vector.field(2, dtype=ti.f32, shape=MAX_POINTS)
line_indices = ti.field(dtype=ti.i32, shape=MAX_POINTS * 2)


# -------------------- GPU Kernel --------------------
@ti.kernel
def clear_canvas():
    for i, j in frame_buffer:
        frame_buffer[i, j] = BG_COLOR


@ti.kernel
def draw_curve(sample_count: ti.i32, brush: ti.i32):
    for i in range(sample_count):
        p = curve_buffer[i]
        px = ti.cast(p[0] * (W - 1), ti.i32)
        py = ti.cast(p[1] * (H - 1), ti.i32)

        for dx, dy in ti.ndrange((-brush, brush + 1), (-brush, brush + 1)):
            x = px + dx
            y = py + dy
            if 0 <= x < W and 0 <= y < H:
                frame_buffer[x, y] = CURVE_COLOR


# -------------------- 曲线计算 --------------------
def bezier_point_iter(points, t):
    """
    迭代版 de Casteljau 算法
    points: [(x1, y1), (x2, y2), ...]
    t: [0, 1]
    """
    work = [np.array(p, dtype=np.float32) for p in points]
    n = len(work)

    while n > 1:
        for i in range(n - 1):
            work[i] = (1.0 - t) * work[i] + t * work[i + 1]
        n -= 1

    return work[0]


def build_curve_samples(ctrl_points, sample_num):
    """
    根据当前控制点生成整条曲线的采样点
    """
    samples = np.zeros((sample_num + 1, 2), dtype=np.float32)
    for k in range(sample_num + 1):
        t = k / sample_num
        samples[k] = bezier_point_iter(ctrl_points, t)
    return samples


def update_control_visual(points):
    """
    更新用于 GUI 绘制的控制点和控制折线数据
    """
    count = len(points)

    # 控制点
    point_np = np.full((MAX_POINTS, 2), -1.0, dtype=np.float32)
    if count > 0:
        point_np[:count] = np.array(points, dtype=np.float32)
    control_vis.from_numpy(point_np)

    # 折线索引
    index_np = np.zeros(MAX_POINTS * 2, dtype=np.int32)
    if count >= 2:
        idx = []
        for i in range(count - 1):
            idx.extend([i, i + 1])
        index_np[:len(idx)] = np.array(idx, dtype=np.int32)
    line_indices.from_numpy(index_np)


def rebuild_curve_if_needed(ctrl_points, sample_num):
    """
    重新生成曲线并绘制到 GPU 像素缓冲区
    """
    clear_canvas()

    if len(ctrl_points) >= 2:
        curve_np = build_curve_samples(ctrl_points, sample_num)
        curve_buffer.from_numpy(curve_np)
        draw_curve(sample_num + 1, 1)   # brush=1，曲线稍粗一点


# -------------------- 主程序 --------------------
def main():
    window = ti.ui.Window("Bezier Curve - Modified Version", (W, H))
    canvas = window.get_canvas()

    control_points = []
    sample_num = INIT_SAMPLES

    # dirty 标记：只有发生变化时才重建曲线
    dirty = True

    print("操作说明：")
    print("左键：添加控制点")
    print("右键：撤销最后一个控制点")
    print("C：清空画布")
    print("↑ / ↓：调整采样点数量")

    while window.running:
        for e in window.get_events(ti.ui.PRESS):
            if e.key == ti.ui.LMB:
                if len(control_points) < MAX_POINTS:
                    pos = window.get_cursor_pos()
                    control_points.append(pos)
                    dirty = True
                    print(f"添加控制点: {pos}")

            elif e.key == ti.ui.RMB:
                if control_points:
                    removed = control_points.pop()
                    dirty = True
                    print(f"撤销控制点: {removed}")

            elif e.key == 'c' or e.key == 'C':
                control_points.clear()
                dirty = True
                print("已清空控制点。")

            elif e.key == ti.ui.UP:
                sample_num = min(MAX_SAMPLES, sample_num + 100)
                dirty = True
                print(f"当前采样数: {sample_num}")

            elif e.key == ti.ui.DOWN:
                sample_num = max(100, sample_num - 100)
                dirty = True
                print(f"当前采样数: {sample_num}")

        if dirty:
            rebuild_curve_if_needed(control_points, sample_num)
            update_control_visual(control_points)
            dirty = False

        canvas.set_image(frame_buffer)

        # 画控制点
        if len(control_points) > 0:
            canvas.circles(control_vis, radius=0.007, color=(1.0, 0.25, 0.25))

        # 画控制折线
        if len(control_points) >= 2:
            canvas.lines(
                control_vis,
                width=0.002,
                indices=line_indices,
                color=(0.75, 0.75, 0.75)
            )

        window.show()


if __name__ == "__main__":
    main()