import numpy as np

from .config import ASSET_DIR
from .smpl_loader import load_smpl_model
from .smpl_math import (
    compute_pose_correctives,
    get_demo_betas,
    get_demo_pose,
)
from .visualization import save_pose_offset_heatmap


def main():
    model = load_smpl_model()
    model.eval()

    parameter = next(model.parameters())
    device = parameter.device
    dtype = parameter.dtype

    betas = get_demo_betas(device=device, dtype=dtype)

    global_orient, body_pose = get_demo_pose(
        device=device,
        dtype=dtype,
    )

    result = compute_pose_correctives(
        model=model,
        betas=betas,
        global_orient=global_orient,
        body_pose=body_pose,
    )

    v_posed = result["v_posed"][0].detach().cpu().numpy()
    pose_offsets = result["pose_offsets"][0].detach().cpu().numpy()

    faces = model.faces
    output_path = ASSET_DIR / "stage_c_pose_offsets.png"

    save_pose_offset_heatmap(
        vertices=v_posed,
        faces=faces,
        pose_offsets=pose_offsets,
        output_path=output_path,
    )

    offset_norm = np.linalg.norm(pose_offsets, axis=1)

    print("[Task 4] Pose corrective blend shapes completed.")
    print(
        "pose_offset_norm: "
        f"min={offset_norm.min():.6f}, "
        f"mean={offset_norm.mean():.6f}, "
        f"max={offset_norm.max():.6f}"
    )
    print(f"saved: {output_path}")


if __name__ == "__main__":
    main()