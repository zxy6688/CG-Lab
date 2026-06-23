import smplx

from .config import DEVICE, NUM_BETAS, SMPL_MODEL_PATH


def load_smpl_model():
    """
    加载本地的 SMPL_NEUTRAL.pkl，并返回 neutral SMPL 模型。
    """

    if not SMPL_MODEL_PATH.exists():
        raise FileNotFoundError(
            "找不到 SMPL 模型文件。\n"
            f"期望路径：{SMPL_MODEL_PATH}\n"
            "请确认 SMPL_NEUTRAL.pkl 位于 models/smpl/ 下。"
        )

    model = smplx.create(
        model_path=str(SMPL_MODEL_PATH),
        model_type="smpl",
        gender="neutral",
        ext="pkl",
        num_betas=NUM_BETAS,
        batch_size=1,
    )

    return model.to(DEVICE)