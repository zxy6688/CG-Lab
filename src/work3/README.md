# 计算机图形学实验三：贝塞尔曲线 Bezier Curve

<br>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Taichi-1.7.4-orange?style=for-the-badge" alt="Taichi">
  <img src="https://img.shields.io/badge/Backend-Vulkan-green?style=for-the-badge" alt="Backend">
  <img src="https://img.shields.io/badge/Work3-Bezier%20Curve-purple?style=for-the-badge" alt="Work3">
  <img src="https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge" alt="Status">
</p>

<br>

<a id="toc"></a>

## 目录

<details open>
<summary><strong>一、本次实验任务与收获</strong></summary>

- [一、本次实验任务与收获](#section-1)

</details>

<details open>
<summary><strong>二、文件结构</strong></summary>

- [二、文件结构](#section-2)

</details>

<details open>
<summary><strong>三、运行方式</strong></summary>

- [三、运行方式](#section-3)
  - [3.1 老师参考代码测试版](#section-3-1)
  - [3.2 必做版：基础贝塞尔曲线](#section-3-2)
  - [3.3 选做一：反走样贝塞尔曲线](#section-3-3)
  - [3.4 选做二：Bezier 与 B-Spline 对比](#section-3-4)
  - [3.5 使用 uv 运行](#section-3-5)

</details>

<details open>
<summary><strong>四、实验目标</strong></summary>

- [四、实验目标](#section-4)
  - [4.1 理解贝塞尔曲线的几何意义](#section-4-1)
  - [4.2 实现 De Casteljau 算法](#section-4-2)
  - [4.3 掌握像素缓冲区与光栅化思想](#section-4-3)
  - [4.4 理解图形界面交互与 CPU/GPU 分工](#section-4-4)

</details>

<details open>
<summary><strong>五、实验原理</strong></summary>

- [五、实验原理](#section-5)
  - [5.1 贝塞尔曲线表示](#section-5-1)
  - [5.2 De Casteljau 算法](#section-5-2)
  - [5.3 光栅化与像素映射](#section-5-3)
  - [5.4 CPU/GPU 批量数据传输](#section-5-4)
  - [5.5 反走样基本思想](#section-5-5)
  - [5.6 均匀三次 B 样条曲线](#section-5-6)

</details>

<details open>
<summary><strong>六、基础任务实现</strong></summary>

- [六、基础任务实现](#section-6)
  - [任务 1：初始化与显存预分配](#section-6-1)
    - [任务要求](#section-6-1-1)
    - [实现方式](#section-6-1-2)
  - [任务 2：实现 De Casteljau 算法](#section-6-2)
    - [任务要求](#section-6-2-1)
    - [实现方式](#section-6-2-2)
  - [任务 3：编写 GPU 绘制内核](#section-6-3)
    - [任务要求](#section-6-3-1)
    - [实现方式](#section-6-3-2)
  - [任务 4：主循环、曲线逻辑与交互响应](#section-6-4)
    - [任务要求](#section-6-4-1)
    - [实现方式](#section-6-4-2)
  - [任务 5：绘制交互控制点](#section-6-5)
    - [任务要求](#section-6-5-1)
    - [实现方式](#section-6-5-2)
  - [基础任务可视化结果](#section-6-6)

</details>

<details open>
<summary><strong>七、选做内容</strong></summary>

- [七、选做内容](#section-7)
  - [7.1 选做一：反走样贝塞尔曲线](#section-7-1)
    - [7.1.1 任务要求](#section-7-1-1)
    - [7.1.2 数学原理](#section-7-1-2)
    - [7.1.3 实现思路](#section-7-1-3)
    - [7.1.4 可视化结果](#section-7-1-4)
    - [7.1.5 本部分小结](#section-7-1-5)
  - [7.2 选做二：Bezier 与 B-Spline 对比](#section-7-2)
    - [7.2.1 任务要求](#section-7-2-1)
    - [7.2.2 数学原理](#section-7-2-2)
    - [7.2.3 实现思路](#section-7-2-3)
    - [7.2.4 可视化结果](#section-7-2-4)
    - [7.2.5 本部分小结](#section-7-2-5)

</details>

<details open>
<summary><strong>八、实验总结</strong></summary>

- [八、实验总结](#section-8)

</details>

## 效果图目录

| 展示内容 | 动态演示 | 终端输出说明图 |
| --- | --- | --- |
| 基础贝塞尔曲线 | [查看动态演示](#section-6-6) | [查看终端输出说明图](#section-6-6) |
| 反走样贝塞尔曲线 | [查看动态演示](#section-7-1-4) | [查看终端输出说明图](#section-7-1-4) |
| Bezier 与 B-Spline 对比 | [查看动态演示](#section-7-2-4) | [查看终端输出说明图](#section-7-2-4) |

<a id="section-1"></a>

## 一、本次实验任务与收获

本次实验围绕 **贝塞尔曲线绘制与交互式光栅化** 展开，主要完成了三个层次的内容。

**第一项任务是完成基础贝塞尔曲线绘制系统，对应 `bezier_curve.py`。** 程序基于 Python + Taichi 实现了鼠标添加控制点、灰色控制折线显示、绿色贝塞尔曲线绘制以及按 `C` 清空画布等功能。曲线上的采样点由 CPU 端通过 De Casteljau 算法计算，再批量传输到 GPU Field 中进行像素绘制。

**第二项任务是完成反走样贝塞尔曲线，对应 `bezier_curve_antialias.py`。** 基础版本只会把曲线采样点映射到单个像素上，容易产生明显锯齿。反走样版本在光栅化阶段加入局部像素邻域的距离加权，让曲线边缘从硬跳变变成更平滑的过渡。

**第三项任务是完成 Bezier 与 B-Spline 曲线对比，对应 `bspline_curve_compare.py`。** 该版本在同一组控制点下同时绘制贝塞尔曲线和均匀三次 B 样条曲线，用不同颜色区分两类曲线，便于观察贝塞尔曲线的全局控制特性和 B 样条曲线的局部控制特性。

此外，`test.py` 用于运行老师参考代码或测试版本，方便对比课程示例与本实验实现之间在交互方式、画面组织和曲线绘制效果上的差异。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-2"></a>

## 二、文件结构

```text
CG-Lab/
├── assets/
│   └── work3/
│       ├── demo_basic.gif              # 必做版动态演示：添加控制点、绘制控制折线与贝塞尔曲线、按 C 清空
│       ├── demo_basic.png              # 必做版终端输出说明图
│       ├── demo_antialias.gif          # 选做一动态演示：普通渲染与反走样渲染效果对比
│       ├── demo_antialias.png          # 选做一终端输出说明图
│       ├── demo_bspline_compare.gif    # 选做二动态演示：Bezier 与 B-Spline 曲线对比
│       └── demo_bspline_compare.png    # 选做二终端输出说明图
│
├── src/
│   └── work3/
│       ├── bezier_curve.py             # 必做版：标准贝塞尔曲线绘制、控制点交互、GPU 光栅化
│       ├── bezier_curve_antialias.py   # 选做一：局部像素邻域距离加权，实现反走样曲线
│       ├── bspline_curve_compare.py    # 选做二：同屏绘制 Bezier 与均匀三次 B-Spline 曲线
│       ├── test.py                     # 老师参考代码测试版，用于与本实验实现进行对比
│       └── README.md                   # 实验说明文档
```

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-3"></a>

## 三、运行方式

在项目根目录下运行。

<a id="section-3-1"></a>

### 3.1 老师参考代码测试版

```bash
python -u "src/work3/test.py"
```

该文件用于运行老师参考代码或测试版本，方便观察课程示例中的基础交互方式，并与自己的实现进行对比。

<a id="section-3-2"></a>

### 3.2 必做版：基础贝塞尔曲线

```bash
python -u "src/work3/bezier_curve.py"
```

该版本完成实验三基础任务，包括鼠标添加控制点、控制折线显示、De Casteljau 曲线采样、GPU 光栅化以及按 `C` 清空画布。

<p align="center">
  <img src="../../assets/work3/demo_basic.gif" alt="Basic Bezier Demo" width="720">
</p>

<a id="section-3-3"></a>

### 3.3 选做一：反走样贝塞尔曲线

```bash
python -u "src/work3/bezier_curve_antialias.py"
```

该版本在基础贝塞尔曲线绘制流程上改进像素渲染方式，通过局部邻域距离加权减弱曲线边缘锯齿。

<p align="center">
  <img src="../../assets/work3/demo_antialias.gif" alt="Anti-Aliasing Bezier Demo" width="720">
</p>

<a id="section-3-4"></a>

### 3.4 选做二：Bezier 与 B-Spline 对比

```bash
python -u "src/work3/bspline_curve_compare.py"
```

该版本在同一组控制点下同时绘制贝塞尔曲线和均匀三次 B 样条曲线，适合观察两类曲线在几何控制方式上的差异。

<p align="center">
  <img src="../../assets/work3/demo_bspline_compare.gif" alt="Bezier vs B-Spline Demo" width="720">
</p>

<a id="section-3-5"></a>

### 3.5 使用 uv 运行

如果使用 `uv` 管理环境，也可以在项目根目录运行：

```bash
uv run python src/work3/bezier_curve.py
```

```bash
uv run python src/work3/bezier_curve_antialias.py
```

```bash
uv run python src/work3/bspline_curve_compare.py
```

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-4"></a>

## 四、实验目标

<a id="section-4-1"></a>

### 4.1 理解贝塞尔曲线的几何意义

贝塞尔曲线由一组控制点决定。控制点本身通常不全部落在曲线上，但它们共同决定曲线的起点、终点、弯曲趋势和整体形状。通过交互式添加控制点，可以直观观察控制多边形对曲线形态的影响。

<a id="section-4-2"></a>

### 4.2 实现 De Casteljau 算法

本实验使用 De Casteljau 算法计算贝塞尔曲线上的采样点。该算法通过逐层线性插值求得参数 `t` 对应的曲线点，几何意义直观，数值稳定，适合用于课程实验中的曲线生成。

<a id="section-4-3"></a>

### 4.3 掌握像素缓冲区与光栅化思想

屏幕可以看作一个二维像素网格。曲线算法计算得到的是连续浮点坐标，而最终显示必须落到离散像素上。本实验通过 `pixels` 缓冲区直接操作像素颜色，从而理解从几何点到屏幕像素的光栅化过程。

<a id="section-4-4"></a>

### 4.4 理解图形界面交互与 CPU/GPU 分工

程序通过 `ti.ui.Window` 创建交互窗口，在 CPU 端处理鼠标和键盘输入，在 GPU 端批量绘制曲线像素。实验中采用一次性数据传输和固定大小对象池，避免主循环中频繁动态申请显存对象，提高交互稳定性。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-5"></a>

## 五、实验原理

<a id="section-5-1"></a>

### 5.1 贝塞尔曲线表示

设有 `n` 个控制点：

$$
\mathbf{P}_0,\mathbf{P}_1,\ldots,\mathbf{P}_{n-1}
$$

引入参数：

$$
t \in [0,1]
$$

当 `t` 从 0 连续变化到 1 时，曲线点的位置随之变化。所有采样点连接起来，就形成一条完整的贝塞尔曲线。

贝塞尔曲线具有明显的全局控制特性：当某个控制点发生变化时，整条曲线的形状通常都会受到影响。因此，在控制点较多时，贝塞尔曲线更适合观察整体形态变化，而不适合只修改局部形状。

<a id="section-5-2"></a>

### 5.2 De Casteljau 算法

De Casteljau 算法的核心是递归线性插值。首先定义第 0 层控制点为：

$$
\mathbf{P}_i^{(0)}=\mathbf{P}_i
$$

对于给定参数 `t`，第 `r` 层插值点由上一层相邻两点线性插值得到：

$$
\mathbf{P}_i^{(r)}(t)=(1-t)\mathbf{P}_i^{(r-1)}(t)+t\mathbf{P}_{i+1}^{(r-1)}(t)
$$

不断重复该过程，直到只剩下一个点：

$$
\mathbf{B}(t)=\mathbf{P}_0^{(n-1)}(t)
$$

这个点就是贝塞尔曲线在参数 `t` 处的精确位置。程序在 CPU 端对 `t` 进行多次采样，得到一系列曲线点，再统一发送给 GPU 绘制。

<a id="section-5-3"></a>

### 5.3 光栅化与像素映射

曲线点通常是 `[0,1]` 范围内的归一化浮点坐标。设屏幕宽度为 `W`，高度为 `H`，曲线点为：

$$
\mathbf{P}=(x,y)
$$

对应的像素索引可以写成：

$$
x_{pixel}=\lfloor xW \rfloor
$$

$$
y_{pixel}=\lfloor yH \rfloor
$$

当像素索引满足范围检查后，程序将 `pixels[x_pixel, y_pixel]` 处的颜色改为绿色，这就是本实验中的手动光栅化过程。

<a id="section-5-4"></a>

### 5.4 CPU/GPU 批量数据传输

现代图形程序中，CPU 和 GPU 是分离的。如果每计算一个曲线点就从 Python 端写入 GPU Field，会产生大量跨设备通信，导致程序卡顿。

本实验采用批量传输方式：CPU 先计算所有曲线采样点，将结果存入 NumPy 数组，再通过 `from_numpy(...)` 一次性传输到 Taichi Field。随后 GPU Kernel 并行访问这些点并点亮对应像素，从而减少 CPU/GPU 频繁通信带来的开销。

<a id="section-5-5"></a>

### 5.5 反走样基本思想

基础光栅化会把浮点曲线点直接截断到某个整数像素上，因此曲线边缘容易出现台阶状锯齿。反走样的目标是让曲线点对周围像素产生不同程度的颜色贡献，而不是只点亮一个像素。

设精确曲线点为：

$$
\mathbf{Q}=(x_f,y_f)
$$

某个邻域像素中心为：

$$
\mathbf{S}_{u,v}=(u+0.5,v+0.5)
$$

二者距离为：

$$
d_{u,v}=\left\|\mathbf{Q}-\mathbf{S}_{u,v}\right\|
$$

可以根据距离设计权重：

$$
w_{u,v}=\max\left(0,1-\frac{d_{u,v}}{r}\right)
$$

距离越近，像素颜色贡献越大；距离越远，颜色贡献越小。这样可以在曲线边缘形成更自然的过渡。

<a id="section-5-6"></a>

### 5.6 均匀三次 B 样条曲线

B 样条曲线通过分段多项式实现局部控制。对于均匀三次 B 样条，每 4 个相邻控制点决定一段曲线。设一段曲线由控制点：

$$
\mathbf{P}_i,\mathbf{P}_{i+1},\mathbf{P}_{i+2},\mathbf{P}_{i+3}
$$

决定，则局部参数 `t` 满足：

$$
t \in [0,1]
$$

均匀三次 B 样条可写成基函数形式：

$$
\mathbf{C}_i(t)=
b_0(t)\mathbf{P}_i+
b_1(t)\mathbf{P}_{i+1}+
b_2(t)\mathbf{P}_{i+2}+
b_3(t)\mathbf{P}_{i+3}
$$

其中四个基函数为：

$$
b_0(t)=\frac{(1-t)^3}{6}
$$

$$
b_1(t)=\frac{3t^3-6t^2+4}{6}
$$

$$
b_2(t)=\frac{-3t^3+3t^2+3t+1}{6}
$$

$$
b_3(t)=\frac{t^3}{6}
$$

当控制点数量大于等于 4 时，程序依次遍历所有相邻的 4 个控制点生成局部曲线段，并将这些分段曲线拼接成完整的 B 样条曲线。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-6"></a>

## 六、基础任务实现

<a id="section-6-1"></a>

## 任务 1：初始化与显存预分配

<a id="section-6-1-1"></a>

### 任务要求

实验要求初始化 Taichi GPU 后端，设置屏幕尺寸、曲线采样数和最大控制点数量，并提前分配像素缓冲区、曲线点缓冲区和控制点对象池。

<a id="section-6-1-2"></a>

### 实现方式

本实验在 `bezier_curve.py` 中完成初始化。程序使用 `ti.init(arch=ti.gpu)` 启动 GPU 后端，设置 `800 × 800` 的显示窗口，并预先创建 `pixels`、`curve_points_field` 和 `gui_points` 三类核心缓冲区。控制折线也使用固定大小的索引池进行管理，避免主循环中反复创建动态对象。

对应代码位置：

```python
ti.init(arch=ti.gpu)
pixels
curve_points_field
gui_points
gui_indices
```

<a id="section-6-2"></a>

## 任务 2：实现 De Casteljau 算法

<a id="section-6-2-1"></a>

### 任务要求

实验要求编写纯 Python 函数 `de_casteljau(points, t)`，根据输入控制点和参数 `t` 返回贝塞尔曲线上的二维坐标。

<a id="section-6-2-2"></a>

### 实现方式

程序在 CPU 端实现 `de_casteljau(points, t)`。函数首先复制当前控制点列表，然后不断对相邻点进行线性插值，直到最后只剩一个点。该点即为当前参数 `t` 对应的贝塞尔曲线点。

对应代码位置：

```python
de_casteljau(points, t)
```

<a id="section-6-3"></a>

## 任务 3：编写 GPU 绘制内核

<a id="section-6-3-1"></a>

### 任务要求

实验要求编写 GPU Kernel，从 `curve_points_field` 中读取曲线采样点，将归一化坐标映射为像素索引，并在越界检查后点亮对应像素。

<a id="section-6-3-2"></a>

### 实现方式

本实验通过 `draw_curve_kernel(n: ti.i32)` 完成 GPU 光栅化。Kernel 内部读取曲线点坐标，将其乘以屏幕宽高并转换为整数像素位置，再将合法范围内的像素设置为绿色。该过程在 GPU 端并行执行，避免 Python 逐像素写入 GPU Field 造成卡顿。

对应代码位置：

```python
draw_curve_kernel(n: ti.i32)
```

<a id="section-6-4"></a>

## 任务 4：主循环、曲线逻辑与交互响应

<a id="section-6-4-1"></a>

### 任务要求

实验要求创建 GGUI 窗口，在主循环中监听鼠标点击和键盘事件。鼠标左键添加控制点，按 `C` 键清空控制点。当控制点数量不少于 2 时，程序需要计算曲线采样点并绘制到屏幕上。

<a id="section-6-4-2"></a>

### 实现方式

程序在 `while window.running:` 主循环中处理交互事件。鼠标左键点击时，当前鼠标坐标会被加入控制点列表；按下 `C` 键时，控制点列表被清空。当控制点数量大于等于 2 时，CPU 端循环采样 `1001` 个曲线点，将结果打包为 NumPy 数组并通过 `from_numpy(...)` 一次性传输给 GPU，再调用 Kernel 绘制曲线。

对应代码位置：

```python
window.get_event()
window.get_cursor_pos()
curve_points_field.from_numpy(...)
canvas.set_image(pixels)
```

<a id="section-6-5"></a>

## 任务 5：绘制交互控制点

<a id="section-6-5-1"></a>

### 任务要求

实验要求使用固定大小的 Taichi Field 绘制控制点。当真实控制点数量小于对象池容量时，需要将无效位置放到屏幕外，保证只有真实控制点显示出来。

<a id="section-6-5-2"></a>

### 实现方式

本实验创建固定长度的 `gui_points` 作为控制点对象池。每一帧先将 NumPy 数组填充为 `-10.0`，使无效点位于屏幕外，再把真实控制点覆盖到数组前部。上传到 `gui_points` 后，调用 `canvas.circles(...)` 绘制红色控制点。控制折线也使用固定大小索引池实现，从而稳定显示控制多边形。

对应代码位置：

```python
gui_points.from_numpy(...)
canvas.circles(...)
canvas.lines(...)
```

<a id="section-6-6"></a>

## 基础任务可视化结果

<table align="center">
  <tr>
    <td align="center"><strong>动态交互演示</strong></td>
    <td align="center"><strong>终端输出说明图</strong></td>
  </tr>
  <tr>
    <td align="center">
      <img src="../../assets/work3/demo_basic.gif" alt="Basic Bezier Demo" width="360">
    </td>
    <td align="center">
      <img src="../../assets/work3/demo_basic.png" alt="Basic Bezier Terminal Output" width="360">
    </td>
  </tr>
</table>

上图展示了基础贝塞尔曲线程序的交互与运行效果。动态演示中，用户可以通过鼠标左键连续添加若干控制点，程序会实时显示红色控制点、灰色控制折线和绿色贝塞尔曲线；按下 `C` 键后，画布会被清空并恢复初始状态。终端输出说明图用于记录程序启动后的运行环境、交互提示和基础功能说明，便于说明该版本已经完成控制点输入、曲线采样、GPU 绘制和清空画布等核心任务。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-7"></a>

## 七、选做内容

<a id="section-7-1"></a>

## 7.1 选做一：反走样贝塞尔曲线

<a id="section-7-1-1"></a>

### 7.1.1 任务要求

基础光栅化绘制会将曲线采样点直接映射到单个像素，容易出现阶梯状锯齿。选做一要求改进像素渲染逻辑，使贝塞尔曲线边缘更加平滑。

<a id="section-7-1-2"></a>

### 7.1.2 数学原理

基础版本中，一个浮点曲线点被强制映射到一个整数像素位置：

$$
x_{pixel}=\lfloor x_f \rfloor
$$

$$
y_{pixel}=\lfloor y_f \rfloor
$$

这种做法会损失亚像素信息。反走样版本保留浮点坐标的局部影响，考察曲线点周围的 `3 × 3` 像素邻域，并根据距离分配不同权重：

$$
w_{u,v}=\max\left(0,1-\frac{d_{u,v}}{r}\right)
$$

最终像素颜色由邻域贡献共同决定。距离曲线真实位置越近，颜色越亮；距离越远，颜色越弱，从而让曲线边缘产生平滑过渡。

<a id="section-7-1-3"></a>

### 7.1.3 实现思路

`bezier_curve_antialias.py` 仍然使用 De Casteljau 算法生成曲线采样点，但在光栅化阶段不再只点亮单个像素。程序遍历曲线点周围的局部像素邻域，计算每个邻域像素中心到曲线点的距离，并根据距离权重更新颜色。这样既保持了原有曲线几何定义，又改善了最终显示质量。

对应代码位置：

```python
bezier_curve_antialias.py
draw_curve_antialias_kernel(...)
```

<a id="section-7-1-4"></a>

### 7.1.4 可视化结果

<table align="center">
  <tr>
    <td align="center"><strong>动态交互演示</strong></td>
    <td align="center"><strong>终端输出说明图</strong></td>
  </tr>
  <tr>
    <td align="center">
      <img src="../../assets/work3/demo_antialias.gif" alt="Anti-Aliasing Demo" width="360">
    </td>
    <td align="center">
      <img src="../../assets/work3/demo_antialias.png" alt="Anti-Aliasing Terminal Output" width="360">
    </td>
  </tr>
</table>

上图展示了反走样贝塞尔曲线的运行效果。动态演示中，程序在添加若干控制点后绘制曲线，并展示普通渲染与反走样渲染在视觉上的差异；反走样版本通过局部像素邻域的距离加权，使曲线边缘不再是单像素硬截断，而是呈现更平滑的过渡效果。终端输出说明图用于记录该版本的功能提示和运行状态，说明程序已经完成反走样渲染逻辑，并能够展示曲线边缘更加平滑的视觉效果。

<a id="section-7-1-5"></a>

### 7.1.5 本部分小结

选做一没有改变贝塞尔曲线的数学定义，而是在光栅化阶段进行优化。通过利用亚像素信息和邻域距离加权，程序能够减弱曲线边缘的锯齿现象，使最终显示效果更平滑。

<a id="section-7-2"></a>

## 7.2 选做二：Bezier 与 B-Spline 对比

<a id="section-7-2-1"></a>

### 7.2.1 任务要求

贝塞尔曲线具有全局控制特性，控制点较多时阶数也会升高。选做二要求在现有交互框架中加入 B 样条曲线绘制，并与贝塞尔曲线进行对比，以观察两类曲线在几何行为上的差异。

<a id="section-7-2-2"></a>

### 7.2.2 数学原理

均匀三次 B 样条曲线每一段只依赖 4 个相邻控制点。若当前段由控制点：

$$
\mathbf{P}_i,\mathbf{P}_{i+1},\mathbf{P}_{i+2},\mathbf{P}_{i+3}
$$

决定，则曲线点可以写成：

$$
\mathbf{C}_i(t)=
b_0(t)\mathbf{P}_i+
b_1(t)\mathbf{P}_{i+1}+
b_2(t)\mathbf{P}_{i+2}+
b_3(t)\mathbf{P}_{i+3}
$$

其中：

$$
b_0(t)=\frac{(1-t)^3}{6}
$$

$$
b_1(t)=\frac{3t^3-6t^2+4}{6}
$$

$$
b_2(t)=\frac{-3t^3+3t^2+3t+1}{6}
$$

$$
b_3(t)=\frac{t^3}{6}
$$

当共有 `n` 个控制点时，程序可以生成：

$$
n-3
$$

段三次 B 样条曲线。由于每段只依赖局部的 4 个控制点，B 样条曲线具有明显的局部控制特性。

<a id="section-7-2-3"></a>

### 7.2.3 实现思路

`bspline_curve_compare.py` 在基础交互框架上同时计算贝塞尔曲线和均匀三次 B 样条曲线。贝塞尔曲线仍使用 De Casteljau 算法计算；B 样条曲线则按相邻 4 个控制点逐段采样，并将所有分段曲线点拼接起来。程序使用不同颜色区分两类曲线，从而在同一窗口中直接比较它们的形态差异。

对应代码位置：

```python
bspline_curve_compare.py
de_casteljau(points, t)
bspline_point(...)
generate_bspline_points(...)
```

<a id="section-7-2-4"></a>

### 7.2.4 可视化结果

<table align="center">
  <tr>
    <td align="center"><strong>动态交互演示</strong></td>
    <td align="center"><strong>终端输出说明图</strong></td>
  </tr>
  <tr>
    <td align="center">
      <img src="../../assets/work3/demo_bspline_compare.gif" alt="Bezier vs B-Spline Demo" width="360">
    </td>
    <td align="center">
      <img src="../../assets/work3/demo_bspline_compare.png" alt="Bezier vs B-Spline Terminal Output" width="360">
    </td>
  </tr>
</table>

上图展示了 Bezier 与 B-Spline 曲线的同屏对比效果。动态演示中，用户添加同一组控制点后，程序同时绘制贝塞尔曲线与均匀三次 B 样条曲线，便于观察两类曲线在形状变化上的差异；贝塞尔曲线更容易受到整体控制点变化影响，而 B 样条曲线表现出更明显的局部控制特征。终端输出说明图用于记录该版本的模式说明、颜色含义和操作提示，说明程序已经完成两类曲线的同屏绘制与对比展示。

<a id="section-7-2-5"></a>

### 7.2.5 本部分小结

选做二扩展了曲线建模能力。通过同屏对比可以看到，贝塞尔曲线更适合展示整体控制点对曲线形状的影响，而 B 样条曲线更适合表达局部控制和分段平滑拼接效果。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-8"></a>

## 八、实验总结

本实验完成了老师文档中要求的基础贝塞尔曲线绘制任务，并进一步完成了反走样和 B 样条曲线对比两个选做内容。基础部分实现了控制点交互、控制折线显示、De Casteljau 曲线采样、GPU 光栅化和按键清空等功能，完整覆盖了实验三的核心要求。

在实现方式上，程序将曲线采样和图形显示进行了清晰分工。CPU 端负责处理交互事件和计算曲线采样点，GPU 端负责批量绘制像素。通过 NumPy 数组一次性传输曲线点，并使用固定大小对象池管理控制点和控制折线，程序避免了主循环中的频繁动态分配和跨设备逐点通信。

选做部分中，反走样版本从像素渲染角度改善了曲线边缘质量，使曲线显示更加平滑；B-Spline 对比版本从曲线建模角度扩展了实验内容，使程序能够直观展示 Bezier 曲线与 B 样条曲线在全局控制和局部控制上的差异。整体来看，本实验从曲线数学、交互设计、像素光栅化和 GPU 数据管理多个方面完成了对贝塞尔曲线绘制流程的系统实现。

<p align="right"><a href="#toc">回到目录 ↑</a></p>