from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

from .config import ASSET_DIR


PANELS = [
    (
        "stage_a_template_weights.png",
        "(a) Template + weights",
    ),
    (
        "stage_b_shaped_joints.png",
        "(b) Shape + joints",
    ),
    (
        "stage_c_pose_offsets.png",
        "(c) Pose offsets",
    ),
    (
        "stage_d_lbs_result.png",
        "(d) Final skinned mesh",
    ),
]


def main():
    image_paths = [
        ASSET_DIR / file_name
        for file_name, _ in PANELS
    ]

    missing_paths = [
        path
        for path in image_paths
        if not path.exists()
    ]

    if missing_paths:
        missing_text = "\n".join(
            f"- {path}"
            for path in missing_paths
        )
        raise FileNotFoundError(
            "无法生成 comparison_grid.png，因为缺少阶段图：\n"
            f"{missing_text}\n\n"
            "请先依次运行 task2、task3、task4、task5。"
        )

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(14, 13),
        dpi=220,
    )

    for ax, (file_name, panel_label) in zip(
        axes.flat,
        PANELS,
    ):
        image_path = ASSET_DIR / file_name
        image = mpimg.imread(image_path)

        ax.imshow(image)
        ax.axis("off")

        ax.text(
            0.03,
            0.04,
            panel_label,
            transform=ax.transAxes,
            fontsize=12,
            fontweight="bold",
            color="black",
            bbox={
                "facecolor": "white",
                "edgecolor": "none",
                "alpha": 0.86,
                "pad": 4,
            },
        )

    fig.suptitle(
        "SMPL Linear Blend Skinning Pipeline",
        fontsize=20,
        fontweight="bold",
        y=0.98,
    )

    fig.text(
        0.5,
        0.018,
        "v_template  →  v_shaped + J  →  v_posed  →  final verts",
        ha="center",
        fontsize=12,
    )

    fig.tight_layout(
        rect=(0, 0.04, 1, 0.96),
        pad=1.0,
    )

    output_path = ASSET_DIR / "comparison_grid.png"

    fig.savefig(
        output_path,
        bbox_inches="tight",
        pad_inches=0.04,
    )
    plt.close(fig)

    print("[Task 6] Four-stage comparison grid completed.")
    print(f"saved: {output_path}")


if __name__ == "__main__":
    main()