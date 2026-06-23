from pathlib import Path

# 项目根目录：CG-Lab/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 本地模型文件：不提交到 GitHub
SMPL_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "smpl"
    / "SMPL_NEUTRAL.pkl"
)

# 本实验所有可提交结果统一放这里
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "work8"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 这次模型规模很小，CPU 就足够
DEVICE = "cpu"

# 实验要求记录的 shape 参数维度
NUM_BETAS = 10

# 可提交的可视化图片目录
ASSET_DIR = PROJECT_ROOT / "assets" / "work8"
ASSET_DIR.mkdir(parents=True, exist_ok=True)

# SMPL 的 24 个基础关节顺序
SMPL_JOINT_NAMES = (
    "pelvis",
    "left_hip",
    "right_hip",
    "spine1",
    "left_knee",
    "right_knee",
    "spine2",
    "left_ankle",
    "right_ankle",
    "spine3",
    "left_foot",
    "right_foot",
    "neck",
    "left_collar",
    "right_collar",
    "head",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hand",
    "right_hand",
)

# 任务 2 默认展示右肩关节的 LBS 权重
WEIGHT_VISUALIZATION_JOINT = 17