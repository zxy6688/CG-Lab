import numpy as np

from .config import ASSET_DIR
from .smpl_loader import load_smpl_model
from .smpl_math import (
    compute_manual_lbs,
    get_demo_betas,
    get_demo_pose,
)
from .visualization import save_lbs_result_with_skeleton


def main():
    model = load_smpl_model()
    model.eval()

    parameter = next(model.parameters())
    device = parameter.device
    dtype = parameter.dtype

    # 与任务 3、4 使用完全相同的 shape 与 pose 参数
    betas = get_demo_betas(device=device, dtype=dtype)

    global_orient, body_pose = get_demo_pose(
        device=device,
        dtype=dtype,
    )

    result = compute_manual_lbs(
        model=model,
        betas=betas,
        global_orient=global_orient,
        body_pose=body_pose,
    )

    v_posed = result["v_posed"][0].detach().cpu().numpy()
    verts = result["verts"][0].detach().cpu().numpy()
    joints_transformed = (
        result["J_transformed"][0]
        .detach()
        .cpu()
        .numpy()
    )

    faces = model.faces
    parents = model.parents.detach().cpu().numpy()

    output_path = ASSET_DIR / "stage_d_lbs_result.png"

    save_lbs_result_with_skeleton(
        vertices=verts,
        faces=faces,
        joints=joints_transformed,
        parents=parents,
        output_path=output_path,
    )

    # 用于终端检查：LBS 后，顶点相对 v_posed 的平均变化量
    skinning_displacement = np.linalg.norm(
        verts - v_posed,
        axis=1,
    )

    print("[Task 5] Manual LBS completed.")
    print(
        "skinning_displacement: "
        f"min={skinning_displacement.min():.6f}, "
        f"mean={skinning_displacement.mean():.6f}, "
        f"max={skinning_displacement.max():.6f}"
    )
    print(f"saved: {output_path}")


if __name__ == "__main__":
    main()