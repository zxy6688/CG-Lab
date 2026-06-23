from .config import ASSET_DIR
from .smpl_loader import load_smpl_model
from .smpl_math import get_demo_betas, compute_v_shaped_and_joints
from .visualization import (
    save_shaped_mesh_with_joints,
    save_shape_difference_heatmap,
)


def main():
    model = load_smpl_model()
    model.eval()

    betas = get_demo_betas()

    result = compute_v_shaped_and_joints(model, betas)

    v_template = result["v_template"][0].detach().cpu().numpy()
    v_shaped = result["v_shaped"][0].detach().cpu().numpy()
    J = result["J"][0].detach().cpu().numpy()

    faces = model.faces
    parents = model.parents.detach().cpu().numpy()

    stage_b_path = ASSET_DIR / "stage_b_shaped_joints.png"
    shape_diff_path = ASSET_DIR / "shape_offsets.png"

    save_shaped_mesh_with_joints(
        vertices=v_shaped,
        faces=faces,
        joints=J,
        parents=parents,
        output_path=stage_b_path,
    )

    save_shape_difference_heatmap(
        v_template=v_template,
        v_shaped=v_shaped,
        faces=faces,
        output_path=shape_diff_path,
    )

    print("[Task 3] Shape blend shapes and joint regression completed.")
    print(f"betas: {betas.detach().cpu().numpy().round(4).tolist()}")
    print(f"saved: {stage_b_path}")
    print(f"saved: {shape_diff_path}")


if __name__ == "__main__":
    main()