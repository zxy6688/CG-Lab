from .config import OUTPUT_DIR, SMPL_MODEL_PATH
from .smpl_loader import load_smpl_model


def collect_model_info(model):
    """
    从加载后的 SMPL 模型中提取实验任务 1 要求的基础信息。
    """

    return {
        "model_file": str(SMPL_MODEL_PATH),
        "num_vertices": int(model.v_template.shape[0]),
        "num_faces": int(model.faces.shape[0]),
        "num_joints": int(model.J_regressor.shape[0]),
        "num_betas": int(model.betas.shape[1]),
    }


def format_model_info(info):
    """
    同时用于终端输出和 summary.txt。
    """

    return "\n".join(
        [
            "Computer Graphics Experiment 8: SMPL LBS",
            "",
            "[Task 1] SMPL Model Information",
            f"model_file: {info['model_file']}",
            f"num_vertices: {info['num_vertices']}",
            f"num_faces: {info['num_faces']}",
            f"num_joints: {info['num_joints']}",
            f"num_betas: {info['num_betas']}",
        ]
    )


def main():
    model = load_smpl_model()

    info = collect_model_info(model)
    report = format_model_info(info)

    print(report)

    summary_path = OUTPUT_DIR / "summary.txt"
    summary_path.write_text(report + "\n", encoding="utf-8")

    print(f"\nSaved: {summary_path}")


if __name__ == "__main__":
    main()