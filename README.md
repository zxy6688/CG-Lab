# CG-Lab：计算机图形学课程实验仓库

<br>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Taichi-1.7.4-orange?style=for-the-badge" alt="Taichi">
  <img src="https://img.shields.io/badge/Backend-Vulkan-green?style=for-the-badge" alt="Backend">
  <img src="https://img.shields.io/badge/Package-uv-purple?style=for-the-badge" alt="uv">
  <img src="https://img.shields.io/badge/Works-1--5-brightgreen?style=for-the-badge" alt="Works">
</p>

<p align="center">
  A Taichi-based computer graphics lab repository covering particle simulation, MVP transformation, Bézier curves, Phong lighting, and Whitted-style ray tracing.
</p>

<br>

本仓库用于整理 **计算机图形学课程实验** 的代码、实验说明文档与可视化展示资源。项目主要基于 **Python + Taichi** 实现，采用统一的 `src/workX` 源码结构与 `assets/workX` 资源结构，便于后续维护、展示和提交课程作业。

<a id="toc"></a>

## 目录

<details open>
<summary><strong>一、实验总览</strong></summary>

- [一、实验总览](#section-1)
  - [1.1 实验导航表](#section-1-1)
  - [1.2 实验总览卡片](#section-1-2)
  - [1.3 实验完成状态](#section-1-3)

</details>

<details open>
<summary><strong>二、可视化预览</strong></summary>

- [二、可视化预览](#section-2)

</details>

<details open>
<summary><strong>三、项目结构</strong></summary>

- [三、项目结构](#section-3)

</details>

<details open>
<summary><strong>四、环境说明</strong></summary>

- [四、环境说明](#section-4)
  - [4.1 推荐环境](#section-4-1)
  - [4.2 Taichi 后端说明](#section-4-2)

</details>

<details open>
<summary><strong>五、快速运行</strong></summary>

- [五、快速运行](#section-5)
  - [5.1 Work1 运行命令](#section-5-1)
  - [5.2 Work2 运行命令](#section-5-2)
  - [5.3 Work3 运行命令](#section-5-3)
  - [5.4 Work4 运行命令](#section-5-4)
  - [5.5 Work5 运行命令](#section-5-5)

</details>

<details open>
<summary><strong>六、资源与文档规范</strong></summary>

- [六、资源与文档规范](#section-6)

</details>

<details open>
<summary><strong>七、资源组织说明</strong></summary>

- [七、资源组织说明](#section-7)

</details>

<details open>
<summary><strong>八、当前仓库整理说明</strong></summary>

- [八、当前仓库整理说明](#section-8)

</details>

<details open>
<summary><strong>九、Git 提交说明</strong></summary>

- [九、Git 提交说明](#section-9)

</details>

<details open>
<summary><strong>十、SSH 配置记录</strong></summary>

- [十、SSH 配置记录](#section-10)

</details>

<details open>
<summary><strong>十一、后续维护建议</strong></summary>

- [十一、后续维护建议](#section-11)

</details>

<details open>
<summary><strong>十二、仓库用途说明</strong></summary>

- [十二、仓库用途说明](#section-12)

</details>

<a id="section-1"></a>

## 一、实验总览

<a id="section-1-1"></a>

### 1.1 实验导航表

当前仓库已经整理了五个实验。每个实验都配套独立源码目录、展示资源目录和子 README 文档。

| 实验编号 | 实验名称 | 关键词 | 子 README |
| --- | --- | --- | --- |
| Work1 | 图形学开发工具 | `uv`、`src` 布局、Taichi、粒子群仿真 | [进入 Work1 文档](src/work1/README.md) |
| Work2 | 旋转与变换 | MVP 变换、透视投影、立方体旋转、旋转插值 | [进入 Work2 文档](src/work2/README.md) |
| Work3 | 贝塞尔曲线 | De Casteljau、光栅化、反走样、B-Spline 对比 | [进入 Work3 文档](src/work3/README.md) |
| Work4 | Phong 光照模型 | Phong、Blinn-Phong、硬阴影、交互式参数调节 | [进入 Work4 文档](src/work4/README.md) |
| Work5 | 光线追踪 | Ray Tracing、反射、硬阴影、玻璃折射、MSAA | [进入 Work5 文档](src/work5/README.md) |

<a id="section-1-2"></a>

### 1.2 实验总览卡片

<table align="center">
  <tr>
    <td align="center">
      <strong>Work1</strong><br>
      图形学开发工具<br>
      粒子群仿真<br>
      <a href="src/work1/README.md">查看文档</a>
    </td>
    <td align="center">
      <strong>Work2</strong><br>
      旋转与变换<br>
      MVP Transformation<br>
      <a href="src/work2/README.md">查看文档</a>
    </td>
    <td align="center">
      <strong>Work3</strong><br>
      贝塞尔曲线<br>
      Bézier Curve<br>
      <a href="src/work3/README.md">查看文档</a>
    </td>
    <td align="center">
      <strong>Work4</strong><br>
      Phong 光照模型<br>
      Lighting Model<br>
      <a href="src/work4/README.md">查看文档</a>
    </td>
    <td align="center">
      <strong>Work5</strong><br>
      光线追踪<br>
      Ray Tracing<br>
      <a href="src/work5/README.md">查看文档</a>
    </td>
  </tr>
</table>

<a id="section-1-3"></a>

### 1.3 实验完成状态

| 实验 | 基础任务 | 选做内容 | README | 可视化资源 |
| --- | --- | --- | --- | --- |
| Work1 | ✅ | — | ✅ | ✅ |
| Work2 | ✅ | ✅ | ✅ | ✅ |
| Work3 | ✅ | ✅ | ✅ | ✅ |
| Work4 | ✅ | ✅ | ✅ | ✅ |
| Work5 | ✅ | ✅ | ✅ | ✅ |

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-2"></a>

## 二、可视化预览

<table align="center">
  <tr>
    <td align="center"><strong>Work1 粒子群仿真</strong></td>
    <td align="center"><strong>Work2 MVP 变换</strong></td>
    <td align="center"><strong>Work3 贝塞尔曲线</strong></td>
  </tr>
  <tr>
    <td align="center">
      <img src="assets/work1/demo_basic.gif" alt="Work1 Demo" width="260">
    </td>
    <td align="center">
      <img src="assets/work2/work2_demo.gif" alt="Work2 Demo" width="260">
    </td>
    <td align="center">
      <img src="assets/work3/demo_basic.gif" alt="Work3 Demo" width="260">
    </td>
  </tr>
  <tr>
    <td align="center"><strong>Work4 Phong 光照</strong></td>
    <td align="center"><strong>Work5 光线追踪</strong></td>
    <td align="center"><strong>更多实验说明</strong></td>
  </tr>
  <tr>
    <td align="center">
      <img src="assets/work4/phong_demo.gif" alt="Work4 Demo" width="260">
    </td>
    <td align="center">
      <img src="assets/work5/task4_ui.gif" alt="Work5 Demo" width="260">
    </td>
    <td align="center">
      <br>
      <a href="#section-1">查看实验总览</a><br>
      <a href="#section-5">查看运行命令</a><br>
      <a href="#section-3">查看项目结构</a>
    </td>
  </tr>
</table>

该预览区展示了每个实验最具有代表性的运行效果。完整的实验目标、数学原理、任务实现、选做内容和更多效果图，请进入各个 `src/workX/README.md` 查看。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-3"></a>

## 三、项目结构

本仓库统一采用 `assets/workX` 存放可视化资源，`src/workX` 存放实验源码与子 README。根目录 README 负责总览所有实验，子 README 负责记录每个实验的任务、原理、运行方式和可视化结果。

```text
CG-Lab/
├── assets/
│   ├── work1/                         # Work1 可视化资源：粒子群 GIF、截图、参数图
│   ├── work2/                         # Work2 可视化资源：MVP、立方体、旋转插值效果图
│   ├── work3/                         # Work3 可视化资源：Bezier、反走样、B-Spline 对比图
│   ├── work4/                         # Work4 可视化资源：Phong、Blinn-Phong、硬阴影效果图
│   ├── work5/                         # Work5 可视化资源：光线追踪、玻璃折射、MSAA 效果图
│   └── ssh_set.png                    # SSH 配置说明截图
│
├── src/
│   ├── work1/
│   │   ├── __init__.py                # Python 包初始化文件
│   │   ├── config.py                  # 粒子数量、窗口大小、颜色、引力、阻尼等参数配置
│   │   ├── physics.py                 # Taichi Field、粒子初始化 kernel、粒子更新 kernel
│   │   ├── main.py                    # 程序入口：Taichi 初始化、窗口创建、鼠标交互和粒子绘制
│   │   └── README.md                  # Work1 实验说明文档
│   │
│   ├── work2/
│   │   ├── __init__.py                # Python 包初始化文件
│   │   ├── main.py                    # 基础版：三角形 MVP 变换、透视除法和屏幕映射
│   │   ├── cube_demo.py               # 选做一：三维线框立方体透视旋转
│   │   ├── cube_interp_demo.py        # 选做二：两个立方体姿态之间的旋转插值动画
│   │   ├── test.py                    # 参考代码测试版
│   │   └── README.md                  # Work2 实验说明文档
│   │
│   ├── work3/
│   │   ├── bezier_curve.py            # 基础版：De Casteljau 贝塞尔曲线交互绘制
│   │   ├── bezier_curve_antialias.py  # 选做一：反走样贝塞尔曲线绘制
│   │   ├── bspline_curve_compare.py   # 选做二：Bezier 与 B-Spline 曲线对比
│   │   ├── test.py                    # 参考代码测试版
│   │   └── README.md                  # Work3 实验说明文档
│   │
│   ├── work4/
│   │   ├── Phong.py                   # 基础版：Phong 光照模型与 UI 参数调节
│   │   ├── BlinnPhong.py              # 选做一：Blinn-Phong 半程向量高光模型
│   │   ├── HardShadow.py              # 选做二：暗影射线与硬阴影
│   │   ├── ComparePhongBlinn.py       # 对比展示：Phong 与 Blinn-Phong 并排比较
│   │   ├── CompareShadow.py           # 对比展示：无阴影与硬阴影并排比较
│   │   ├── test.py                    # 参考代码测试版
│   │   └── README.md                  # Work4 实验说明文档
│   │
│   └── work5/
│       ├── main.py                    # 基础版：Whitted-Style 光线追踪、反射、硬阴影和 UI 控制
│       ├── GlassRefraction.py         # 选做一：玻璃折射材质、全反射和 Fresnel 近似
│       ├── AntiAliasingMSAA.py        # 选做二：MSAA 多重采样抗锯齿
│       ├── test.py                    # 参考代码测试版
│       └── README.md                  # Work5 实验说明文档
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

4. `.gitignore`、`pyproject.toml` 和 `uv.lock` 均需要保留；`.venv/`、`__pycache__/`、`.pyc`、`imgui.ini` 和本地临时运行文件不应提交到仓库。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-4"></a>

## 四、环境说明

<a id="section-4-1"></a>

### 4.1 推荐环境

本仓库推荐使用 `uv` 管理 Python 环境。当前实验主要使用：

| 项目 | 版本 / 说明 |
| --- | --- |
| Python | 3.13 |
| Taichi | 1.7.4 |
| Backend | Vulkan / GPU compatible backend |
| Package Manager | uv |
| Platform | Windows |

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

| 后端 | 含义 |
| --- | --- |
| `cuda` | 使用 NVIDIA 独立显卡 |
| `metal` | 使用 macOS Apple Silicon 图形后端 |
| `vulkan` | Windows / Linux 常见现代图形后端 |
| `opengl` | 兼容性图形后端 |
| `cpu` | 未调用 GPU，只使用 CPU 执行 |

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-5"></a>

## 五、快速运行

所有命令均在项目根目录下运行。

<a id="section-5-1"></a>

### 5.1 Work1 运行命令

```bash
python -u "src/work1/main.py"
```

或使用 `uv`：

```bash
uv run python src/work1/main.py
```

该实验会打开粒子群仿真窗口，鼠标移动时粒子会受到吸引并产生聚集、流动、反弹等动态效果。

<a id="section-5-2"></a>

### 5.2 Work2 运行命令

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

### 5.3 Work3 运行命令

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

### 5.4 Work4 运行命令

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

### 5.5 Work5 运行命令

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

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-6"></a>

## 六、资源与文档规范

本仓库中，每个实验都配套独立的 README，子 README 的写法保持统一：

| 内容 | 说明 |
| --- | --- |
| 实验任务与收获 | 开头说明本实验完成了什么，而不是简单罗列空泛目标 |
| 文件结构 | 用目录树说明源码和资源，文件职责写在树形结构后面的注释中 |
| 运行方式 | 每个可运行脚本单独列命令 |
| 可视化结果 | 使用 GIF、PNG 和对比图展示实验效果 |
| 实验目标 | 对齐实验文档中的目标要求 |
| 实验原理 | 解释核心数学模型、图形学算法和实现注意事项 |
| 基础任务实现 | 按实验任务顺序说明任务要求、实现方式和可视化结果 |
| 选做内容 | 先放实验文档中的选做截图，再分别说明任务要求、数学原理、实现思路和结果 |
| 实验总结 | 总结本实验完成情况和对后续实验的意义 |

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

这样 GitHub 能够正确显示每个实验的图片和 GIF。

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-7"></a>

## 七、资源组织说明

为了保持仓库结构清晰，所有实验展示资源统一放在 `assets/` 目录下，并按照实验编号分文件夹管理：

```text
assets/
├── work1/        # Work1 演示资源：粒子群 GIF、参数截图、运行结果图
├── work2/        # Work2 演示资源：MVP 变换、立方体旋转、插值动画
├── work3/        # Work3 演示资源：Bezier 曲线、反走样、B-Spline 对比
├── work4/        # Work4 演示资源：Phong、Blinn-Phong、Hard Shadow
├── work5/        # Work5 演示资源：光线追踪、玻璃折射、MSAA
└── ssh_set.png   # SSH 配置记录截图
```

每个实验的 GIF、截图、结果图都保存在对应的 `assets/workX/` 目录中，并在各自的 `src/workX/README.md` 中通过相对路径引用。例如：

```text
../../assets/work5/task1_scene.png
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

经过这些整理后，本仓库已经形成比较稳定的课程实验组织方式，后续新增实验可以继续沿用当前结构。

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

如果只提交某一个实验，例如 Work4：

```bash
git add -A src/work4 assets/work4
git commit -m "polish work4 lighting documentation and visuals"
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

5. 每个 work 的 `README.md` 都能在 GitHub 上正常显示图片和目录链接。

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

<p align="right"><a href="#toc">回到目录 ↑</a></p>

<a id="section-12"></a>

## 十二、仓库用途说明

本仓库主要用于整理计算机图形学课程实验，包括实验代码、运行说明、数学原理、可视化结果和 GitHub 提交记录。仓库内容不仅用于课程作业提交，也作为后续复习图形学基础知识和整理个人项目经验的材料。

从内容上看，本仓库覆盖了从图形学工程环境搭建，到 MVP 变换、曲线绘制、局部光照、阴影、反射、折射和抗锯齿等多个主题。每个实验都尽量做到代码可运行、文档可阅读、效果可展示，使整个项目既能作为课程实验仓库，也能作为个人图形学学习过程的记录。

<p align="right"><a href="#toc">回到目录 ↑</a></p>