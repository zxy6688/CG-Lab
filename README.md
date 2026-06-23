# CG-Lab：计算机图形学课程实验仓库

<br>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Taichi-1.7.4-orange?style=for-the-badge" alt="Taichi">
  <img src="https://img.shields.io/badge/Backend-Vulkan-green?style=for-the-badge" alt="Backend">
  <img src="https://img.shields.io/badge/Package-uv-purple?style=for-the-badge" alt="uv">
  <img src="https://img.shields.io/badge/works-1--8-brightgreen?style=for-the-badge" alt="works">
  <img src="https://img.shields.io/badge/Completed-8%2F8-success?style=for-the-badge" alt="Completed">
</p>

<p align="center">
  A computer graphics lab repository covering particle simulation, MVP transformation, Bézier curves, Phong lighting, Whitted-style ray tracing, differentiable rendering, mass-spring cloth simulation, and SMPL-based Linear Blend Skinning.
</p>

<div align="center">

<table>
  <tr>
    <td><strong>姓名</strong></td>
    <td>周欣源</td>
  </tr>
  <tr>
    <td><strong>学号</strong></td>
    <td>202311260012</td>
  </tr>
  <tr>
    <td><strong>专业</strong></td>
    <td>计算机科学与技术</td>
  </tr>
</table>

</div>

<br>

本仓库用于整理 **计算机图形学课程实验** 的代码、实验说明文档与可视化展示资源。项目主要基于 **Python + Taichi** 实现，同时在 `work6` 中使用 **PyTorch3D + CUDA** 完成可微渲染实验，在 `work7` 中使用 **Taichi GGUI** 完成质点弹簧布料仿真，在 `work8` 中使用 **PyTorch + SMPL** 完成 Shape Blend Shapes、Pose Corrective 与 Linear Blend Skinning 实验。仓库采用统一的 `src/workX` 源码结构与 `assets/workX` 资源结构，便于后续维护、展示和提交课程作业。

目前课程一共有 **8 个实验**，其中 **work1–work8 均已完成** 并整理到仓库中。`work8` 基于 SMPL neutral 模型，完整拆解并验证了从模板网格、形状校正、姿态相关校正到最终 LBS 蒙皮的前向过程。

<a id="toc"></a>

## 目录

<details open>
<summary><strong>一、实验总览</strong></summary>

* [一、实验总览](#section-1)

  * [1.1 实验导航表](#section-1-1)
  * [1.2 实验总览卡片](#section-1-2)
  * [1.3 实验完成状态](#section-1-3)

</details>

<details open>
<summary><strong>二、可视化预览</strong></summary>

* [二、可视化预览](#section-2)

</details>

<details open>
<summary><strong>三、项目结构</strong></summary>

* [三、项目结构](#section-3)

</details>

<details open>
<summary><strong>四、环境说明</strong></summary>

* [四、环境说明](#section-4)

  * [4.1 推荐环境](#section-4-1)
  * [4.2 Taichi 后端说明](#section-4-2)
  * [4.3 PyTorch3D 与云端 GPU 说明](#section-4-3)
  * [4.4 work7 Taichi GGUI 说明](#section-4-4)
  * [4.5 work8 SMPL LBS 专用环境](#section-4-5)

</details>

<details open>
<summary><strong>五、快速运行</strong></summary>

* [五、快速运行](#section-5)

  * [5.1 work1 运行命令](#section-5-1)
  * [5.2 work2 运行命令](#section-5-2)
  * [5.3 work3 运行命令](#section-5-3)
  * [5.4 work4 运行命令](#section-5-4)
  * [5.5 work5 运行命令](#section-5-5)
  * [5.6 work6 运行说明](#section-5-6)
  * [5.7 work7 运行命令](#section-5-7)
  * [5.8 work8 LBS 蒙皮运行命令](#section-5-8)

</details>

<details open>
<summary><strong>六、资源与文档规范</strong></summary>

* [六、资源与文档规范](#section-6)

</details>

<details open>
<summary><strong>七、资源组织说明</strong></summary>

* [七、资源组织说明](#section-7)

</details>

<details open>
<summary><strong>八、当前仓库整理说明</strong></summary>

* [八、当前仓库整理说明](#section-8)

</details>

<details open>
<summary><strong>九、Git 提交说明</strong></summary>

* [九、Git 提交说明](#section-9)

</details>

<details open>
<summary><strong>十、SSH 配置记录</strong></summary>

* [十、SSH 配置记录](#section-10)

</details>

<details open>
<summary><strong>十一、后续维护建议</strong></summary>

* [十一、后续维护建议](#section-11)

</details>

<details open>
<summary><strong>十二、仓库用途说明</strong></summary>

* [十二、仓库用途说明](#section-12)

</details>

<details open>
<summary><strong>十三、课程实验完结撒花与致谢</strong></summary>

* [十三、课程实验完结撒花与致谢](#section-13)

</details>

<a id="section-1"></a>

## 一、实验总览

<a id="section-1-1"></a>

### 1.1 实验导航表

当前仓库已经整理完成八个实验。每个实验均配套独立源码目录、展示资源目录和子 README 文档。`work8` 基于 SMPL neutral 模型，完整实现模板网格与蒙皮权重、Shape Blend Shapes、关节回归、Pose Corrective、Forward Kinematics、手写 Linear Blend Skinning 与官方前向一致性验证。

| 实验编号  | 实验名称       | 关键词                                                             | 子 README                           |
| ----- | ---------- | --------------------------------------------------------------- | ---------------------------------- |
| work1 | 图形学开发工具    | `uv`、Taichi、粒子群仿真、项目结构初始化                                       | [进入 work1 文档](src/work1/README.md) |
| work2 | 旋转与变换      | MVP 变换、透视投影、立方体旋转、旋转插值                                          | [进入 work2 文档](src/work2/README.md) |
| work3 | 贝塞尔曲线      | De Casteljau、光栅化、反走样、B-Spline 对比                                | [进入 work3 文档](src/work3/README.md) |
| work4 | Phong 光照模型 | Phong、Blinn-Phong、硬阴影、交互式参数调节                                   | [进入 work4 文档](src/work4/README.md) |
| work5 | 光线追踪       | Ray Tracing、反射、硬阴影、玻璃折射、MSAA                                    | [进入 work5 文档](src/work5/README.md) |
| work6 | 可微渲染       | PyTorch3D、Soft Rasterization、Silhouette、RGB、Texture Fitting     | [进入 work6 文档](src/work6/README.md) |
| work7 | 质点弹簧模型     | Mass-Spring System、Cloth Simulation、Euler Integration、Collision | [进入 work7 文档](src/work7/README.md) |
| work8 | LBS 蒙皮     | SMPL、Linear Blend Skinning、Shape Blend Shapes、Pose Corrective、Skinning Weights | [进入 work8 文档](src/work8/README.md) |

<a id="section-1-2"></a>

### 1.2 实验总览卡片

<table align="center">
  <tr>
    <td align="center">
      <strong>work1</strong><br>
      图形学开发工具<br>
      粒子群仿真<br>
      <a href="src/work1/README.md">查看文档</a>
    </td>
    <td align="center">
      <strong>work2</strong><br>
      旋转与变换<br>
      MVP Transformation<br>
      <a href="src/work2/README.md">查看文档</a>
    </td>
    <td align="center">
      <strong>work3</strong><br>
      贝塞尔曲线<br>
      Bézier Curve<br>
      <a href="src/work3/README.md">查看文档</a>
    </td>
    <td align="center">
      <strong>work4</strong><br>
      Phong 光照模型<br>
      Lighting Model<br>
      <a href="src/work4/README.md">查看文档</a>
    </td>
  </tr>
</table>

<table align="center">
  <tr>
    <td align="center">
      <strong>work5</strong><br>
      光线追踪<br>
      Ray Tracing<br>
      <a href="src/work5/README.md">查看文档</a>
    </td>
    <td align="center">
      <strong>work6</strong><br>
      可微渲染<br>
      Differentiable Rendering<br>
      <a href="src/work6/README.md">查看文档</a>
    </td>
    <td align="center">
      <strong>work7</strong><br>
      质点弹簧模型<br>
      Mass-Spring System<br>
      <a href="src/work7/README.md">查看文档</a>
    </td>
    <td align="center">
      <strong>work8</strong><br>
      LBS 蒙皮<br>
      Linear Blend Skinning<br>
      <a href="src/work8/README.md">查看文档</a>
    </td>
  </tr>
</table>

<a id="section-1-3"></a>

### 1.3 实验完成状态

| 实验    | 基础任务 | 选做内容 | README | 可视化资源 |
| ----- | ---- | ---- | ------ | ----- |
| work1 | ✅    | —    | ✅      | ✅     |
| work2 | ✅    | ✅    | ✅      | ✅     |
| work3 | ✅    | ✅    | ✅      | ✅     |
| work4 | ✅    | ✅    | ✅      | ✅     |
| work5 | ✅    | ✅    | ✅      | ✅     |
| work6 | ✅    | ✅    | ✅      | ✅     |
| work7 | ✅    | ✅    | ✅      | ✅     |
| work8 |  —    | ✅   | ✅      | ✅     |

说明：`work8` 已完成基于 SMPL 的 Linear Blend Skinning 实验，包含模型加载、模板权重可视化、Shape Blend Shapes、关节回归、Pose Corrective、手写 LBS、四阶段总览以及与官方 SMPL 前向结果的一致性验证。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-2"></a>

## 二、可视化预览

下面按照 **3 × 3** 的形式统一展示课程实验预览。前八项为已完成实验的代表性效果图，最后一项为“更多实验说明”导航入口。

<table align="center">
  <tr>
    <td width="33.33%" align="center" valign="top">
      <strong>work1 粒子群仿真</strong><br><br>
      <img src="assets/work1/demo_basic.gif" alt="work1 demo" width="250"><br><br>
    </td>
    <td width="33.33%" align="center" valign="top">
      <strong>work2 MVP 变换</strong><br><br>
      <img src="assets/work2/work2_demo.gif" alt="work2 demo" width="250"><br><br>
    </td>
    <td width="33.33%" align="center" valign="top">
      <strong>work3 贝塞尔曲线</strong><br><br>
      <img src="assets/work3/demo_basic.gif" alt="work3 demo" width="250"><br><br>
    </td>
  </tr>

  <tr>
    <td width="33.33%" align="center" valign="top">
      <strong>work4 Phong 光照</strong><br><br>
      <img src="assets/work4/phong_demo.gif" alt="work4 demo" width="250"><br><br>
    </td>
    <td width="33.33%" align="center" valign="top">
      <strong>work5 光线追踪</strong><br><br>
      <img src="assets/work5/task4_ui.gif" alt="work5 demo" width="250"><br><br>
    </td>
    <td width="33.33%" align="center" valign="top">
      <strong>work6 可微渲染</strong><br><br>
      <img src="assets/work6/texture_fit_optimization.gif" alt="work6 demo" width="250"><br><br>
    </td>
  </tr>

  <tr>
    <td width="33.33%" align="center" valign="top">
      <strong>work7 质点弹簧模型</strong><br><br>
      <img src="assets/work7/work7_overview.gif" alt="work7 demo" width="250"><br><br>
    </td>
    <td width="33.33%" align="center" valign="top">
      <strong>work8 LBS 蒙皮</strong><br><br>
      <a href="src/work8/README.md">
        <img src="assets/work8/comparison_grid.png" alt="work8 SMPL LBS pipeline" width="250">
      </a><br><br>
      <a href="src/work8/README.md">查看文档</a>
    </td>
    <td width="33.33%" align="center" valign="top">
      <strong>更多实验说明</strong><br><br>
      <br>
      <a href="#section-1">查看实验总览</a><br><br>
      <a href="#section-5">查看运行命令</a><br><br>
      <a href="#section-3">查看项目结构</a><br><br><br><br>
    </td>
  </tr>
</table>

<br>

说明：

1. `work1`–`work8` 展示当前仓库中最具代表性的 GIF、PNG 或实验结果图。

2. `work8` 展示 SMPL 模型经过 Shape Blend Shapes、Pose Corrective 和 Linear Blend Skinning 后得到的四阶段流程总览；点击图片或“查看文档”可进入完整实验说明。

3. 如果想进一步查看某个实验的任务说明、数学原理、实现细节与更多可视化结果，请进入各实验子 `README.md`。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-3"></a>

## 三、项目结构

本仓库统一采用 `assets/workX` 存放可视化资源，`src/workX` 存放实验源码与子 README。根目录 README 负责总览所有实验，子 README 负责记录每个实验的任务、原理、运行方式和可视化结果。

```text
CG-Lab/
├── assets/
│   ├── work1/                         # work1 可视化资源：粒子群 GIF、截图、参数图
│   ├── work2/                         # work2 可视化资源：MVP、立方体、旋转插值效果图
│   ├── work3/                         # work3 可视化资源：Bezier、反走样、B-Spline 对比图
│   ├── work4/                         # work4 可视化资源：Phong、Blinn-Phong、硬阴影效果图
│   ├── work5/                         # work5 可视化资源：光线追踪、玻璃折射、MSAA 效果图
│   ├── work6/                         # work6 可视化资源：可微渲染、剪影优化、RGB 优化、纹理拟合
│   ├── work7/                         # work7 可视化资源：质点弹簧、积分对比、弹簧拓扑、球体碰撞
│   ├── work8/                         # work8 可视化资源：SMPL 权重、shape、pose、LBS 与官方验证记录
│   └── ssh_set.png                    # SSH 配置说明截图
│
├── models/
│   └── smpl/
│       ├── README.md                   # SMPL 模型文件获取与放置说明
│       └── SMPL_NEUTRAL.pkl            # 本地模型文件，不提交 Git
│
├── outputs/
│   └── work8/
│       └── summary.txt                 # 模型基础信息与官方前向验证误差
│
├── src/
│   ├── work1/
│   │   ├── __init__.py                # Python 包初始化文件
│   │   ├── config.py                  # 粒子数量、窗口大小、颜色、引力、阻尼等参数配置
│   │   ├── physics.py                 # Taichi Field、粒子初始化 kernel、粒子更新 kernel
│   │   ├── main.py                    # 程序入口：Taichi 初始化、窗口创建、鼠标交互和粒子绘制
│   │   └── README.md                  # work1 实验说明文档
│   │
│   ├── work2/
│   │   ├── __init__.py                # Python 包初始化文件
│   │   ├── main.py                    # 基础版：三角形 MVP 变换、透视除法和屏幕映射
│   │   ├── cube_demo.py               # 选做一：三维线框立方体透视旋转
│   │   ├── cube_interp_demo.py        # 选做二：两个立方体姿态之间的旋转插值动画
│   │   ├── test.py                    # 参考代码测试版
│   │   └── README.md                  # work2 实验说明文档
│   │
│   ├── work3/
│   │   ├── bezier_curve.py            # 基础版：De Casteljau 贝塞尔曲线交互绘制
│   │   ├── bezier_curve_antialias.py  # 选做一：反走样贝塞尔曲线绘制
│   │   ├── bspline_curve_compare.py   # 选做二：Bezier 与 B-Spline 曲线对比
│   │   ├── test.py                    # 参考代码测试版
│   │   └── README.md                  # work3 实验说明文档
│   │
│   ├── work4/
│   │   ├── Phong.py                   # 基础版：Phong 光照模型与 UI 参数调节
│   │   ├── BlinnPhong.py              # 选做一：Blinn-Phong 半程向量高光模型
│   │   ├── HardShadow.py              # 选做二：暗影射线与硬阴影
│   │   ├── ComparePhongBlinn.py       # 对比展示：Phong 与 Blinn-Phong 并排比较
│   │   ├── CompareShadow.py           # 对比展示：无阴影与硬阴影并排比较
│   │   ├── test.py                    # 参考代码测试版
│   │   └── README.md                  # work4 实验说明文档
│   │
│   ├── work5/
│   │   ├── main.py                    # 基础版：Whitted-Style 光线追踪、反射、硬阴影和 UI 控制
│   │   ├── GlassRefraction.py         # 选做一：玻璃折射材质、全反射和 Fresnel 近似
│   │   ├── AntiAliasingMSAA.py        # 选做二：MSAA 多重采样抗锯齿
│   │   ├── test.py                    # 参考代码测试版
│   │   └── README.md                  # work5 实验说明文档
│   │
│   ├── work6/
│   │   ├── cow.obj                                # 低难度剪影优化使用的目标模型
│   │   ├── work6_differentiable_rendering.ipynb   # 主实验 Notebook，包含剪影优化、RGB 优化和消融实验
│   │   ├── work6_low_silhouette.ipynb             # 低难度剪影优化备份版本
│   │   ├── work6_true_textured_fit.ipynb          # 真实纹理牛拟合版本
│   │   ├── data/
│   │   │   └── cow_mesh/                          # 官方 textured cow 数据
│   │   ├── output_meshes/                         # 最终输出的 .obj 模型
│   │   └── README.md                              # work6 实验说明文档
│   │
│   ├── work7/
│   │   ├── README.md                              # work7 实验说明文档
│   │   ├── test.py                                # 老师教程参考实现，用于环境验证与基础效果复现
│   │   ├── main.py                                # 基础任务：三种积分方法与阻尼对比
│   │   ├── optional_springs.py                    # 选做一：剪切弹簧与弯曲弹簧
│   │   └── optional_collision.py                  # 选做二：球体碰撞
│   │
│   └── work8/
│       ├── __init__.py                            # Work8 Python package 标记文件
│       ├── config.py                              # 模型路径、输出路径、关节名称等全局配置
│       ├── smpl_loader.py                         # SMPL neutral 模型加载逻辑
│       ├── smpl_math.py                           # Shape、pose corrective、LBS 核心计算
│       ├── visualization.py                       # 网格、热力图、骨架和总对比图绘制
│       ├── task1_model_info.py                    # Task 1：模型基础信息
│       ├── task2_template_weights.py              # Task 2：模板网格与蒙皮权重
│       ├── task3_shape_joints.py                  # Task 3：形状校正与关节回归
│       ├── task4_pose_correctives.py              # Task 4：姿态相关校正
│       ├── task5_lbs_result.py                    # Task 5：手写 Linear Blend Skinning
│       ├── task6_comparison.py                    # Task 6：四阶段总对比图
│       ├── task7_validation.py                    # Task 7：官方前向一致性验证
│       ├── run_all.py                             # 顺序运行全部任务
│       ├── requirements.txt                       # Work8 专用兼容环境依赖
│       └── README.md                              # work8 实验说明文档
│
├── .gitignore                         # Git 忽略规则，排除 .venv、缓存文件和本地临时文件
├── pyproject.toml                     # uv 项目配置与依赖声明
├── uv.lock                            # uv 依赖锁定文件，保证环境可复现
└── README.md                          # 仓库总说明文档
```

说明：

1. `assets/` 只负责存放图片、GIF 和截图，不放源码。

2. `src/` 只负责存放每个实验的代码和对应 README。

3. 每个实验都采用 `workX` 命名，保证代码目录与资源目录一一对应。

4. `work8` 已完成 SMPL LBS 蒙皮实验，源码位于 `src/work8/`，可视化资源位于 `assets/work8/`，模型基础信息和官方验证误差位于 `outputs/work8/summary.txt`。

5. `.gitignore`、`pyproject.toml` 和 `uv.lock` 均需要保留；`.venv/`、`.venv-work8/`、`__pycache__/`、`.pyc`、`imgui.ini`、`models/smpl/SMPL_NEUTRAL.pkl` 和本地临时运行文件不应提交到仓库。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-4"></a>

## 四、环境说明

<a id="section-4-1"></a>

### 4.1 推荐环境

本仓库推荐使用 `uv` 管理 Python 环境。当前实验主要使用：

| 项目              | 版本 / 说明                         |
| --------------- | ------------------------------- |
| Python          | 3.13                            |
| Taichi          | 1.7.4                           |
| Backend         | Vulkan / GPU compatible backend |
| Package Manager | uv                              |
| Platform        | Windows                         |

安装依赖后，可以在项目根目录运行：

```bash
uv sync
```

如果没有使用 `uv sync`，也可以直接安装核心依赖：

```bash
uv add taichi numpy
```

<a id="section-4-2"></a>

### 4.2 Taichi 后端说明

运行 Taichi 程序时，终端可能出现类似输出：

```text
[W ...] nvcuda.dll lib not found.
[Taichi] Starting on arch=vulkan
```

这通常不是错误。它表示当前设备没有使用 CUDA，但 Taichi 已经自动切换到 Vulkan 后端。只要后面显示 `Starting on arch=vulkan`，并且窗口能够正常打开，就说明程序已经可以运行。

常见后端含义如下：

| 后端       | 含义                          |
| -------- | --------------------------- |
| `cuda`   | 使用 NVIDIA 独立显卡              |
| `metal`  | 使用 macOS Apple Silicon 图形后端 |
| `vulkan` | Windows / Linux 常见现代图形后端    |
| `opengl` | 兼容性图形后端                     |
| `cpu`    | 未调用 GPU，只使用 CPU 执行          |

<a id="section-4-3"></a>

### 4.3 PyTorch3D 与云端 GPU 说明

`work6` 与前几个 Taichi 实验不同，主要依赖 PyTorch3D、PyTorch 和 CUDA 环境。由于 PyTorch3D 涉及底层 C++ / CUDA 扩展编译，本实验使用 ModelScope DSW GPU Notebook 完成运行。

`work6` 实际运行环境如下：

| 项目        | 版本 / 说明                     |
| --------- | --------------------------- |
| Platform  | ModelScope DSW GPU Notebook |
| GPU       | NVIDIA A10                  |
| Python    | 3.11                        |
| PyTorch   | 2.9.1 + CUDA 12.8           |
| PyTorch3D | 0.7.9                       |

在 Notebook 中安装依赖：

```bash
pip install --upgrade pip
pip install fvcore iopath matplotlib ninja imageio trimesh tqdm pandas
pip install "git+https://gitee.com/hongwenzhang/pytorch3d.git" --no-build-isolation
```

该部分主要用于可微渲染实验，和 `work1`–`work5` 的本地 Taichi / Vulkan 运行方式有所区别。

<a id="section-4-4"></a>

### 4.4 work7 Taichi GGUI 说明

`work7` 使用 Taichi GGUI 构建三维布料仿真窗口，主要运行在本地 Windows + Vulkan 后端。实验运行时仍可能出现 `nvcuda.dll lib not found` 警告，只要后续显示 `Starting on arch=vulkan`，并且窗口能够正常打开，即可继续实验。

`work7` 主要依赖：

| 项目              | 说明                   |
| --------------- | -------------------- |
| Taichi GGUI     | 绘制三维布料质点、弹簧线段和控制面板   |
| Vulkan 后端       | 本地 GPU / 图形后端运行      |
| ScreenToGif     | 录制布料动态 GIF           |
| `assets/work7/` | 保存积分对比、弹簧拓扑和球体碰撞演示资源 |

<a id="section-4-5"></a>

### 4.5 work8 SMPL LBS 专用环境

`work8` 基于 SMPL neutral 模型完成模板网格、Shape Blend Shapes、Pose Corrective、Forward Kinematics 与 Linear Blend Skinning 的完整拆解。

由于本实验使用的 `SMPL_NEUTRAL.pkl` 是较早版本的 SMPL pickle 文件，加载时依赖 `chumpy`；而 `chumpy` 与新版 Python、NumPy 的兼容性有限，因此 `work8` 使用独立的 `.venv-work8` 环境，不影响仓库主环境和其他 Taichi 实验。

`work8` 实际运行环境如下：

| 项目 | 版本 / 说明 |
| --- | --- |
| Python | 3.10.20 |
| NumPy | 1.23.5 |
| SciPy | 1.10.1 |
| PyTorch | 2.12.1 + CPU |
| smplx | 0.1.28 |
| chumpy | 0.70 |
| Matplotlib | 3.10.9 |

创建 Work8 专用环境：

```bat
uv venv .venv-work8 --python 3.10 --seed
```

安装依赖：

```bat
uv pip install --python .venv-work8\Scripts\python.exe pip setuptools wheel
uv pip install --python .venv-work8\Scripts\python.exe numpy==1.23.5 scipy==1.10.1 torch smplx==0.1.28 matplotlib imageio pillow
uv pip install --python .venv-work8\Scripts\python.exe chumpy==0.70 --no-build-isolation
```

模型文件需自行放置于：

```text
models/smpl/SMPL_NEUTRAL.pkl
```

该模型文件受原始 SMPL 许可证约束，不会提交到 Git 仓库。具体说明见：

```text
models/smpl/README.md
```

`work8` 主要输出包括：

```text
assets/work8/stage_a_template_weights.png
assets/work8/stage_b_shaped_joints.png
assets/work8/stage_c_pose_offsets.png
assets/work8/stage_d_lbs_result.png
assets/work8/comparison_grid.png
outputs/work8/summary.txt
```

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-5"></a>

## 五、快速运行

所有命令均在项目根目录下运行。

<a id="section-5-1"></a>

### 5.1 work1 运行命令

```bash
python -u "src/work1/main.py"
```

或使用 `uv`：

```bash
uv run python src/work1/main.py
```

该实验会打开粒子群仿真窗口，鼠标移动时粒子会受到吸引并产生聚集、流动、反弹等动态效果。

<a id="section-5-2"></a>

### 5.2 work2 运行命令

基础 MVP 变换：

```bash
python -u "src/work2/main.py"
```

三维立方体透视旋转：

```bash
python -u "src/work2/cube_demo.py"
```

旋转插值动画：

```bash
python -u "src/work2/cube_interp_demo.py"
```

该实验用于观察三维顶点经过 `Model`、`View`、`Projection` 矩阵后如何映射到二维屏幕。

<a id="section-5-3"></a>

### 5.3 work3 运行命令

基础贝塞尔曲线：

```bash
python -u "src/work3/bezier_curve.py"
```

反走样版本：

```bash
python -u "src/work3/bezier_curve_antialias.py"
```

Bezier 与 B-Spline 对比：

```bash
python -u "src/work3/bspline_curve_compare.py"
```

该实验支持鼠标添加控制点，并实时绘制曲线、控制折线和扩展对比效果。

<a id="section-5-4"></a>

### 5.4 work4 运行命令

基础 Phong 光照：

```bash
python -u "src/work4/Phong.py"
```

Blinn-Phong 模型：

```bash
python -u "src/work4/BlinnPhong.py"
```

硬阴影版本：

```bash
python -u "src/work4/HardShadow.py"
```

Phong 与 Blinn-Phong 对比：

```bash
python -u "src/work4/ComparePhongBlinn.py"
```

无阴影与硬阴影对比：

```bash
python -u "src/work4/CompareShadow.py"
```

该实验用于观察局部光照模型、材质参数和阴影机制对渲染结果的影响。

<a id="section-5-5"></a>

### 5.5 work5 运行命令

基础光线追踪：

```bash
python -u "src/work5/main.py"
```

玻璃折射材质：

```bash
python -u "src/work5/GlassRefraction.py"
```

MSAA 抗锯齿版本：

```bash
python -u "src/work5/AntiAliasingMSAA.py"
```

该实验用于观察主光线、阴影射线、反射射线、折射射线和多重采样抗锯齿效果。

<a id="section-5-6"></a>

### 5.6 work6 运行说明

`work6` 使用 PyTorch3D 和 CUDA 环境，推荐在 ModelScope DSW GPU Notebook 中运行。

低难度剪影优化：

```text
src/work6/work6_low_silhouette.ipynb
```

主实验 Notebook：

```text
src/work6/work6_differentiable_rendering.ipynb
```

真实纹理牛拟合：

```text
src/work6/work6_true_textured_fit.ipynb
```

该实验用于观察可微渲染如何将二维剪影、RGB 图像和纹理监督反向传播到三维网格顶点，从而实现从球体到目标奶牛模型的优化过程。

<a id="section-5-7"></a>

### 5.7 work7 运行命令

老师教程参考实现：

```bash
uv run python src/work7/test.py
```

基础质点弹簧系统：

```bash
uv run python src/work7/main.py
```

选做一：剪切弹簧与弯曲弹簧：

```bash
uv run python src/work7/optional_springs.py
```

选做二：球体碰撞：

```bash
uv run python src/work7/optional_collision.py
```

该实验用于观察质点弹簧布料在不同积分方法下的稳定性差异，并进一步展示弹簧拓扑增强和球体碰撞效果。

<a id="section-5-8"></a>

### 5.8 work8 LBS 蒙皮运行命令

`work8` 使用独立的 Python 3.10 环境运行。所有命令均在项目根目录执行。

Task 1：加载 SMPL 并输出模型基础信息：

```bat
.venv-work8\Scripts\python.exe -m src.work8.task1_model_info
```

Task 2：模板网格与右肩关节蒙皮权重：

```bat
.venv-work8\Scripts\python.exe -m src.work8.task2_template_weights
```

Task 3：Shape Blend Shapes 与关节回归：

```bat
.venv-work8\Scripts\python.exe -m src.work8.task3_shape_joints
```

Task 4：Pose Corrective Blend Shapes：

```bat
.venv-work8\Scripts\python.exe -m src.work8.task4_pose_correctives
```

Task 5：手写 Linear Blend Skinning：

```bat
.venv-work8\Scripts\python.exe -m src.work8.task5_lbs_result
```

Task 6：四阶段总对比图：

```bat
.venv-work8\Scripts\python.exe -m src.work8.task6_comparison
```

Task 7：手写 LBS 与官方 SMPL 前向验证：

```bat
.venv-work8\Scripts\python.exe -m src.work8.task7_validation
```

一键顺序运行全部任务：

```bat
.venv-work8\Scripts\python.exe -m src.work8.run_all
```

完整实验说明、每个阶段的可视化结果和误差验证见：

```text
src/work8/README.md
```

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-6"></a>

## 六、资源与文档规范

本仓库中，每个实验都配套独立的 README，子 README 的写法保持统一：

| 内容      | 说明                                  |
| ------- | ----------------------------------- |
| 实验任务与收获 | 开头说明本实验完成了什么，而不是简单罗列空泛目标            |
| 文件结构    | 用目录树说明源码和资源，文件职责写在树形结构后面的注释中        |
| 运行方式    | 每个可运行脚本单独列命令                        |
| 可视化结果   | 使用 GIF、PNG 和对比图展示实验效果               |
| 实验目标    | 对齐实验文档中的目标要求                        |
| 实验原理    | 解释核心数学模型、图形学算法和实现注意事项               |
| 基础任务实现  | 按实验任务顺序说明任务要求、实现方式和可视化结果            |
| 选做内容    | 先放实验文档中的选做截图，再分别说明任务要求、数学原理、实现思路和结果 |
| 实验总结    | 总结本实验完成情况和对后续实验的意义                  |

资源文件命名规则：

```text
assets/workX/
```

源码文件命名规则：

```text
src/workX/
```

子 README 中引用图片时，统一使用相对路径：

```text
../../assets/workX/xxx.png
```

这样 GitHub 能够正确显示每个实验的图片和 GIF。`work7` 中的 GIF 资源较多，统一保存在 `assets/work7/` 中，文件名采用英文小写加下划线，例如：

```text
assets/work7/work7_overview.gif
assets/work7/integration_methods_compare.gif
assets/work7/optional_collision_main.gif
```

`work8` 的静态可视化结果、环境验证截图和终端验证记录统一保存在 `assets/work8/` 中，例如：

```text
assets/work8/stage_a_template_weights.png
assets/work8/stage_c_pose_offsets.png
assets/work8/stage_d_lbs_result.png
assets/work8/comparison_grid.png
```

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-7"></a>

## 七、资源组织说明

为了保持仓库结构清晰，所有实验展示资源统一放在 `assets/` 目录下，并按照实验编号分文件夹管理：

```text
assets/
├── work1/        # work1 演示资源：粒子群 GIF、参数截图、运行结果图
├── work2/        # work2 演示资源：MVP 变换、立方体旋转、插值动画
├── work3/        # work3 演示资源：Bezier 曲线、反走样、B-Spline 对比
├── work4/        # work4 演示资源：Phong、Blinn-Phong、Hard Shadow
├── work5/        # work5 演示资源：光线追踪、玻璃折射、MSAA
├── work6/        # work6 演示资源：可微渲染、剪影优化、RGB 优化、纹理拟合
├── work7/        # work7 演示资源：质点弹簧、积分对比、弹簧拓扑、球体碰撞
├── work8/        # work8 演示资源：SMPL 权重、shape、pose、LBS 与官方验证记录
└── ssh_set.png   # SSH 配置记录截图
```

每个实验的 GIF、截图、结果图都保存在对应的 `assets/workX/` 目录中，并在各自的 `src/workX/README.md` 中通过相对路径引用。例如：

```text
../../assets/work5/task1_scene.png
../../assets/work6/texture_fit_optimization.gif
../../assets/work7/work7_overview.gif
../../assets/work8/comparison_grid.png
```

这种组织方式可以避免图片散落在源码目录中，也能让每个实验的代码、文档和可视化资源保持一一对应。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-8"></a>

## 八、当前仓库整理说明

相较于早期版本，本仓库在 **2026 年 4 月 9 日** 进行了较大规模的结构整理与重命名，主要包括：

1. 将实验内容按照 `work1 / work2 / work3` 的形式重新组织。

2. 将展示资源统一迁移到 `assets/` 目录下，并按照实验编号分类保存。

3. 调整整体目录结构，使代码、文档和展示资源之间的关系更加清晰。

在后续整理中，仓库继续扩展并补充了 `work4` 和 `work5`。到 **2026 年 5 月 1 日**，本仓库进一步完成了 README 风格的大规模统一和可视化资源整理，主要包括：

1. 统一每个实验 README 的结构，包括目录、文件结构、运行方式、实验原理、任务实现、选做内容和实验总结。

2. 统一 `src/workX/` 与 `assets/workX/` 的命名规则，使源码与展示资源保持对应。

3. 补充每个实验的 GIF、PNG、对比图和选做内容截图，使仓库不只是代码集合，也能够作为完整的课程实验展示页。

4. 统一使用 badge、目录跳转、图片表格、回到目录链接等格式，使 GitHub 页面更加清晰、美观、易读。

到 **2026 年 5 月 14 日**，仓库进一步补充了 `work6` 可微渲染实验，主要包括：

1. 新增 `src/work6/`，整理低难度剪影优化、高难度 RGB 联合优化、真实纹理牛拟合和正则化消融实验。

2. 新增 `assets/work6/`，保存可微渲染过程 GIF、目标图像、Loss 曲线、消融对比图和云端 Notebook 运行记录。

3. 在根目录 README 中补充 `work6` 导航、可视化预览、运行说明和 PyTorch3D / ModelScope 环境说明。

4. 保持 `src/workX/` 与 `assets/workX/` 的统一组织方式，使 `work6` 与前五个实验在仓库结构和文档风格上保持一致。

到 **2026 年 5 月 28 日**，仓库进一步补充了 `work7` 质点弹簧模型实验，主要包括：

1. 新增 `src/work7/`，整理基础质点弹簧系统、老师教程参考实现、弹簧拓扑增强选做和球体碰撞选做。

2. 新增 `assets/work7/`，保存基础布料动态、三种积分方法对比、显式欧拉爆炸、阻尼对比、剪切弹簧与弯曲弹簧对比、球体碰撞和显式欧拉碰撞反例等 GIF 与截图。

3. 在根目录 README 中补充 `work7` 导航、可视化预览、运行命令、资源结构和实验完成状态。

4. 保持 `src/workX/` 与 `assets/workX/` 的统一组织方式，使 `work7` 与前六个实验在仓库结构和文档风格上保持一致。

到 **2026 年 6 月 23 日**，仓库最后补充并完成了 `work8` SMPL Linear Blend Skinning 实验，主要包括：

1. 新增 `src/work8/`，将 SMPL 前向过程拆解为模型加载、模板网格与蒙皮权重、Shape Blend Shapes、关节回归、Pose Corrective、Forward Kinematics、手写 LBS、四阶段总览和官方前向验证七项独立任务。

2. 新增 `assets/work8/`，保存 Python 3.10 兼容环境验证、SMPL 模型信息、单关节权重热力图、主导关节分布、形状变化幅度、姿态相关校正、最终 LBS 结果、四阶段总览图以及完整终端验证记录。

3. 新增 `models/smpl/README.md`，说明 `SMPL_NEUTRAL.pkl` 的获取与放置位置；模型文件本身受许可证约束，仅保留本地，不提交到仓库。

4. 新增 `outputs/work8/summary.txt`，保存模型顶点数、面片数、关节数、shape 参数维度，以及手写 LBS 与官方 SMPL 前向的误差验证结果。

5. 在根目录 README 中同步更新 `work8` 导航、可视化预览、运行命令、资源结构、SMPL 专用环境和实验完成状态。

6. 使用完全相同的 `betas`、`global_orient` 与 `body_pose`，将手写 LBS 与官方 SMPL 前向结果逐顶点比较，最终得到：

```text
mean_absolute_error: 0.0000000000e+00
max_absolute_error:  0.0000000000e+00
```

保持 `src/workX/` 与 `assets/workX/` 的统一组织方式，使 `work8` 与前七个实验在仓库结构、运行逻辑、资源命名和文档风格上保持一致。

经过这些整理后，本仓库已经完成全部八个课程实验，并形成比较稳定、完整且可复现的课程实验组织方式。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-9"></a>

## 九、Git 提交说明

常用提交流程如下：

```bash
git status
git add -A src/workX assets/workX
git commit -m "polish workX documentation and visuals"
git push origin master:main
```

如果只提交某一个实验，例如 `work4`：

```bash
git add -A src/work4 assets/work4
git commit -m "polish work4 lighting documentation and visuals"
git push origin master:main
```

如果只提交某一个实验，例如 `work6`：

```bash
git add -A src/work6 assets/work6
git commit -m "add work6 differentiable rendering experiment"
git push origin master:main
```

如果只提交某一个实验，例如 `work7`：

```bash
git add -A src/work7 assets/work7
git commit -m "add work7 mass spring system"
git push origin master:main
```

如果只想提交根目录 README：

```bash
git add README.md
git commit -m "polish project overview readme"
git push origin master:main
```

提交前建议检查：

```bash
git status
```

重点确认：

1. `.venv/` 没有被提交。

2. `__pycache__/` 没有被提交。

3. 图片文件名和 README 中引用路径完全一致。

4. `imgui.ini` 和临时运行文件不应作为正式实验文件提交。

5. 每个 `work` 的 `README.md` 都能在 GitHub 上正常显示图片和目录链接。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-10"></a>

## 十、SSH 配置记录

如果本地已经配置好 SSH key，并且已经添加到 GitHub 账号中，可以直接使用 SSH 方式推送代码。SSH 的好处是后续 `push` 和 `pull` 不需要反复输入账号密码或 token。

检查本机是否已有 SSH key：

```bash
ls -al ~/.ssh
```

测试 GitHub SSH 连接：

```bash
ssh -T git@github.com
```

查看当前远程仓库地址：

```bash
git remote -v
```

如果需要切换为 SSH 远程地址，可以使用：

```bash
git remote set-url origin git@github.com:zxy6688/CG-Lab.git
```

如果 SSH 网络不稳定，也可以临时切换回 HTTPS：

```bash
git remote set-url origin https://github.com/zxy6688/CG-Lab.git
```

相关截图记录如下：

<p align="center">
  <img src="assets/ssh_set.png" alt="SSH Setup" width="720">
</p>

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-11"></a>

## 十一、后续维护建议

为了避免项目继续变乱，后续维护时建议遵循以下规则：

1. 每个新实验单独建立一个新的 `src/workX/` 目录。

2. 所有演示资源统一放在 `assets/workX/` 目录下。

3. 目录命名统一使用小写形式，例如 `work1`、`work2`、`work3`。

4. 每个实验都保留独立的 `README.md`，并按照当前统一格式编写。

5. 修改完成一个实验后及时提交 Git，避免多个实验的修改混在同一次提交中。

6. 不提交 `.venv/`、`__pycache__/`、`.pyc`、`imgui.ini` 和临时运行文件。

7. README 中引用图片时，确保文件名和路径与 `assets/workX/` 中的真实文件完全一致。

8. 如果某个实验新增选做内容，也应同步更新对应的源码、资源目录、README 和根目录导航表。

9. `work8` 已于 2026 年 6 月 23 日完成，并已同步新增 `src/work8/`、`assets/work8/`、`src/work8/README.md`、`models/smpl/README.md` 和 `outputs/work8/summary.txt`，同时更新了本根目录 README 的实验导航、可视化预览、运行命令、项目结构和完成状态。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-12"></a>

## 十二、仓库用途说明

本仓库主要用于整理计算机图形学课程实验，包括实验代码、运行说明、数学原理、可视化结果和 GitHub 提交记录。仓库内容不仅用于课程作业提交，也作为后续复习图形学基础知识和整理个人项目经验的材料。

从内容上看，本仓库覆盖了从图形学工程环境搭建，到 MVP 变换、曲线绘制、局部光照、阴影、反射、折射、抗锯齿、可微渲染和物理仿真等多个主题。每个实验都尽量做到代码可运行、文档可阅读、效果可展示，使整个项目既能作为课程实验仓库，也能作为个人图形学学习过程的记录。

新增的 `work6` 进一步补充了可微渲染主题，使仓库内容从传统实时渲染、曲线建模和光线追踪扩展到基于深度学习框架的三维网格反演与优化。

新增的 `work7` 进一步补充了物理仿真主题，使仓库内容扩展到质点弹簧模型、布料模拟、数值积分稳定性比较、弹簧拓扑增强和球体碰撞处理。

期末后最后新增的 `work8` 进一步补充了角色动画与人体蒙皮主题，使仓库内容扩展到参数化人体模型、SMPL、形状参数、姿态参数、蒙皮权重、Pose Corrective、Forward Kinematics 和 Linear Blend Skinning。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-13"></a>

## 十三、课程实验完结撒花与致谢

<br>

<h1 align="center">🎉 CG-Lab · 8 / 8 全部完成！🎉</h1>

<h2 align="center">从第一个 Taichi 粒子窗口，到最后一次 SMPL 验证误差为 0。</h2>

<p align="center">
  <img src="https://img.shields.io/badge/Works-8%2F8-00AEEF?style=for-the-badge" alt="Works 8/8">
  <img src="https://img.shields.io/badge/Status-Finally%20Complete-brightgreen?style=for-the-badge" alt="Finally Complete">
  <img src="https://img.shields.io/badge/CG--Lab-Complete-FF69B4?style=for-the-badge" alt="CG Lab Complete">
</p>

<br>

<p align="center">
  <strong>建模、变换、曲线、光照、光线追踪、可微渲染、物理仿真、角色蒙皮。</strong><br>
  <strong>八个实验，八段完整的图形学学习轨迹，终于全部收束成这个仓库。</strong>
</p>

<br>

> 这一学期，这个仓库从一个空目录开始，逐步记录下粒子在窗口中流动、立方体在透视投影下旋转、Bezier 曲线被控制点牵引、Phong 高光与阴影被点亮、光线在镜面和玻璃中递归传播、奶牛网格在可微渲染中被一点点优化、布料在弹簧力与数值积分中摆动，最后由 SMPL 骨架带动人体网格完成平滑蒙皮。


### 🌟 完结撒花

<div align="center">

# 🎊🎊🎊 计算机图形学实验全部完成！🎊🎊🎊

## 8 个实验 · 8 份 README · 一整个学期的图形学轨迹

### 辛苦了辛苦了。

</div>

<br>

### 致谢

感谢敬爱的老师、助教和课程资料，为建模、渲染、动画、物理仿真与角色动画提供了完整而清晰的学习路径。

感谢每一份课件、每一次调参、每一个深夜保存下来的截图，以及每一次从“怎么又错了”到“终于跑出来了”的瞬间。

不感谢每一次实验中出现的报错、黑屏、路径问题、环境冲突、数值不稳定和结果不如预期。它们让每一个最终能够稳定运行的窗口、GIF、渲染图和验证结果都更有分量。

最后，感谢坚持把每个实验都整理成完整代码、完整文档和完整可视化结果的自己。

<p align="center">
  <strong>愿以后回看这个仓库时，仍然记得：</strong><br>
  <strong>图形学理解如何表示、变换、建模、渲染与驱动这个世界。</strong>
</p>

<br>

<p align="center">
  <strong>CG-Lab · 2026.06.23 · 完结撒花 ✨</strong>
</p>

<p align="right"><a href="#toc">回到目录 ↑</a></p>

