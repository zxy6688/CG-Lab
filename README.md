# CG-Lab 计算机图形学实验仓库

本仓库用于存放计算机图形学课程实验代码与说明文档，基于 Python 与 Taichi 实现。

目前包含以下实验内容：

- **Work0**：万有引力粒子群仿真实验
- **Work1**：3D MVP 变换实验（Model-View-Projection）


## 仓库结构

```text
CG-Lab/
├── assets/
├── src/
│   ├── Work0/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── physics.py
│   │   ├── main.py
│   │   └── README.md
│   └── Work1/
│       ├── __init__.py
│       ├── main.py
│       ├── test.py
│       └── README.md
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
└── README.md
```
## 环境说明

本项目推荐使用 uv 或 conda 配置 Python 环境。

### 使用 uv

在项目根目录执行：
```bash
uv add taichi
uv run python src/Work0/main.py
uv run python src/Work1/main.py
```
### 使用 conda

在项目根目录执行：
```bash
conda create -n cg_env python=3.12 -y
conda activate cg_env
pip install taichi
python src/Work0/main.py
python src/Work1/main.py
```
## 各实验说明
### Work0：万有引力粒子群仿真
实现二维空间中的粒子引力相互作用与可视化。
详细说明请见：```src/Work0/README.md```

### Work1：3D MVP 变换实验
实现三维空间中三角形的模型变换、视图变换与投影变换，并将其映射到二维屏幕空间进行绘制。
详细说明请见：```src/Work1/README.md```