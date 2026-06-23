from .config import (
    ASSET_DIR,
    SMPL_JOINT_NAMES,
    WEIGHT_VISUALIZATION_JOINT,
)
from .smpl_loader import load_smpl_model
from .visualization import (
    save_dominant_joint_distribution,
    save_template_and_weight_heatmap,
)


def main():
    model = load_smpl_model()
    model.eval()

    vertices = model.v_template.detach().cpu().numpy()
    faces = model.faces
    lbs_weights = model.lbs_weights.detach().cpu().numpy()

    joint_id = WEIGHT_VISUALIZATION_JOINT

    if joint_id < 0 or joint_id >= lbs_weights.shape[1]:
        raise ValueError(
            f"joint_id={joint_id} 不合法。"
            f"当前模型共有 {lbs_weights.shape[1]} 个关节。"
        )

    joint_name = SMPL_JOINT_NAMES[joint_id]
    selected_joint_weights = lbs_weights[:, joint_id]

    stage_a_path = ASSET_DIR / "stage_a_template_weights.png"
    all_joint_path = ASSET_DIR / "all_joint_weights.png"

    save_template_and_weight_heatmap(
        vertices=vertices,
        faces=faces,
        joint_weights=selected_joint_weights,
        joint_name=f"{joint_id}: {joint_name}",
        output_path=stage_a_path,
    )

    save_dominant_joint_distribution(
        vertices=vertices,
        faces=faces,
        lbs_weights=lbs_weights,
        output_path=all_joint_path,
    )

    print("[Task 2] Template mesh and skinning weights completed.")
    print(f"selected_joint: {joint_id} ({joint_name})")
    print(
        "weight_range: "
        f"[{selected_joint_weights.min():.6f}, "
        f"{selected_joint_weights.max():.6f}]"
    )
    print(f"saved: {stage_a_path}")
    print(f"saved: {all_joint_path}")


if __name__ == "__main__":
    main()