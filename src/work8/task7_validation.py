from pathlib import Path

import torch

from .config import (
    ASSET_DIR,
    OUTPUT_DIR,
    PROJECT_ROOT,
    SMPL_MODEL_PATH,
)
from .smpl_loader import load_smpl_model
from .smpl_math import (
    compute_manual_lbs,
    get_demo_betas,
    get_demo_pose,
)


def project_relative(path: Path) -> str:
    """
    将项目内绝对路径转换为 GitHub 友好的相对路径。
    例如：
    D:/.../CG-Lab/assets/work8/comparison_grid.png
    ->
    assets/work8/comparison_grid.png
    """
    return path.relative_to(PROJECT_ROOT).as_posix()


def build_summary_text(
    model,
    mean_abs_error: float,
    max_abs_error: float,
) -> str:
    """
    生成最终 summary.txt 内容。
    """

    figure_paths = [
        ASSET_DIR / "stage_a_template_weights.png",
        ASSET_DIR / "all_joint_weights.png",
        ASSET_DIR / "stage_b_shaped_joints.png",
        ASSET_DIR / "shape_offsets.png",
        ASSET_DIR / "stage_c_pose_offsets.png",
        ASSET_DIR / "stage_d_lbs_result.png",
        ASSET_DIR / "comparison_grid.png",
    ]

    lines = [
        "Computer Graphics Experiment 8: SMPL LBS",
        "",
        "[Model Information]",
        f"model_file: {project_relative(SMPL_MODEL_PATH)}",
        f"num_vertices: {int(model.v_template.shape[0])}",
        f"num_faces: {int(model.faces.shape[0])}",
        f"num_joints: {int(model.J_regressor.shape[0])}",
        f"num_betas: {int(model.betas.shape[1])}",
        "",
        "[Manual LBS vs Official SMPL Forward]",
        f"mean_absolute_error: {mean_abs_error:.10e}",
        f"max_absolute_error: {max_abs_error:.10e}",
        "",
        "[Generated Figures]",
    ]

    lines.extend(project_relative(path) for path in figure_paths)

    return "\n".join(lines) + "\n"


def main():
    model = load_smpl_model()
    model.eval()

    parameter = next(model.parameters())
    device = parameter.device
    dtype = parameter.dtype

    # 与 Task 3、4、5 使用完全一致的 shape / pose 参数
    betas = get_demo_betas(
        device=device,
        dtype=dtype,
    )

    global_orient, body_pose = get_demo_pose(
        device=device,
        dtype=dtype,
    )

    # 1. 手写 LBS
    manual_result = compute_manual_lbs(
        model=model,
        betas=betas,
        global_orient=global_orient,
        body_pose=body_pose,
    )
    manual_verts = manual_result["verts"]

    # 2. 官方 SMPL 前向
    with torch.no_grad():
        official_output = model(
            betas=betas,
            global_orient=global_orient,
            body_pose=body_pose,
            return_verts=True,
        )
        official_verts = official_output.vertices

    # 3. 逐顶点、逐坐标误差
    absolute_difference = torch.abs(
        manual_verts - official_verts
    )

    mean_abs_error = absolute_difference.mean().item()
    max_abs_error = absolute_difference.max().item()

    # 4. 写入最终摘要
    summary_text = build_summary_text(
        model=model,
        mean_abs_error=mean_abs_error,
        max_abs_error=max_abs_error,
    )

    summary_path = OUTPUT_DIR / "summary.txt"
    summary_path.write_text(
        summary_text,
        encoding="utf-8",
    )

    print("[Task 7] Validation against official SMPL forward completed.")
    print(f"mean_absolute_error: {mean_abs_error:.10e}")
    print(f"max_absolute_error:  {max_abs_error:.10e}")
    print(f"saved: {summary_path}")


if __name__ == "__main__":
    main()