from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm, colors
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def to_display_coordinates(vertices: np.ndarray) -> np.ndarray:
    """
    SMPL 原坐标一般是：
    x：左右
    y：上下
    z：前后

    Matplotlib 3D 图默认更适合把第三维显示为竖直方向，
    所以转换为：
    x：左右
    y：前后
    z：上下
    """
    vertices = np.asarray(vertices, dtype=np.float32)
    return vertices[:, [0, 2, 1]]


def set_equal_axes(ax, vertices: np.ndarray) -> None:
    """让三维图三个方向的显示比例一致，避免人体被压扁。"""
    mins = vertices.min(axis=0)
    maxs = vertices.max(axis=0)

    center = (mins + maxs) / 2.0
    radius = float(np.max(maxs - mins) / 2.0)

    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_zlim(center[2] - radius, center[2] + radius)

    ax.view_init(elev=7, azim=-90)
    ax.set_proj_type("ortho")
    ax.set_axis_off()
    ax.grid(False)


def add_mesh(
    ax,
    vertices: np.ndarray,
    faces: np.ndarray,
    face_colors=None,
    edge_color=(0.12, 0.12, 0.12, 0.05),
    line_width=0.02,
    alpha=1.0,
):
    display_vertices = to_display_coordinates(vertices)
    faces = np.asarray(faces, dtype=np.int64)

    triangles = display_vertices[faces]

    if face_colors is None:
        face_colors = (0.72, 0.76, 0.83, 1.0)

    mesh = Poly3DCollection(
        triangles,
        facecolors=face_colors,
        edgecolors=edge_color,
        linewidths=line_width,
        alpha=alpha,
    )

    ax.add_collection3d(mesh)
    set_equal_axes(ax, display_vertices)

    return mesh

def vertex_values_to_face_colors(
    vertex_values: np.ndarray,
    faces: np.ndarray,
    cmap_name: str,
):
    """
    将顶点标量值转换为每个三角形面片的颜色。
    三角形颜色取三个顶点数值的平均值。
    """
    values = np.asarray(vertex_values, dtype=np.float32).reshape(-1)
    faces = np.asarray(faces, dtype=np.int64)

    face_values = values[faces].mean(axis=1)

    vmin = float(values.min())
    vmax = float(values.max())

    if np.isclose(vmin, vmax):
        vmax = vmin + 1e-8

    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.get_cmap(cmap_name)

    face_colors = cmap(norm(face_values))
    scalar_map = cm.ScalarMappable(norm=norm, cmap=cmap)
    scalar_map.set_array(values)

    return face_colors, scalar_map


def save_template_and_weight_heatmap(
    vertices: np.ndarray,
    faces: np.ndarray,
    joint_weights: np.ndarray,
    joint_name: str,
    output_path: Path,
):
    output_path = Path(output_path)

    face_colors, scalar_map = vertex_values_to_face_colors(
        joint_weights,
        faces,
        cmap_name="plasma",
    )

    fig = plt.figure(figsize=(11, 5.6), dpi=220)

    ax_template = fig.add_subplot(1, 2, 1, projection="3d")
    add_mesh(ax_template, vertices, faces)
    ax_template.set_title("(a) SMPL template mesh", fontsize=11, pad=6)

    ax_weight = fig.add_subplot(1, 2, 2, projection="3d")
    add_mesh(ax_weight, vertices, faces, face_colors=face_colors)
    ax_weight.set_title(
        f"(b) LBS weight heatmap: {joint_name}",
        fontsize=11,
        pad=6,
    )

    colorbar = fig.colorbar(
        scalar_map,
        ax=ax_weight,
        shrink=0.70,
        pad=0.02,
    )
    colorbar.set_label("LBS weight", fontsize=10)

    fig.suptitle(
        "Stage A: Template Mesh and Skinning Weights",
        fontsize=15,
        y=0.98,
    )

    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(output_path, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)

def save_dominant_joint_distribution(
    vertices: np.ndarray,
    faces: np.ndarray,
    lbs_weights: np.ndarray,
    output_path: Path,
):
    """
    生成辅助图：
    色相表示主导关节编号；
    明暗表示该主导权重的大小。
    """
    output_path = Path(output_path)

    dominant_joint = np.argmax(lbs_weights, axis=1)
    dominant_weight = np.max(lbs_weights, axis=1)

    weight_min = float(dominant_weight.min())
    weight_max = float(dominant_weight.max())

    strength = (dominant_weight - weight_min) / (
        weight_max - weight_min + 1e-8
    )

    categorical_cmap = plt.get_cmap("hsv", lbs_weights.shape[1])
    base_rgb = categorical_cmap(dominant_joint)[:, :3]

    brightness = 0.35 + 0.65 * strength[:, None]
    vertex_rgb = base_rgb * brightness

    vertex_rgba = np.concatenate(
        [vertex_rgb, np.ones((vertex_rgb.shape[0], 1))],
        axis=1,
    )

    face_colors = vertex_rgba[np.asarray(faces, dtype=np.int64)].mean(axis=1)

    fig = plt.figure(figsize=(6.2, 7.0), dpi=220)
    ax = fig.add_subplot(111, projection="3d")

    add_mesh(ax, vertices, faces, face_colors=face_colors)

    ax.set_title(
        "Dominant Joint Distribution",
        fontsize=13,
        pad=12,
    )

    fig.text(
        0.5,
        0.03,
        "Hue: dominant joint    Brightness: dominant LBS weight",
        ha="center",
        fontsize=9,
    )

    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(output_path, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)

def save_shaped_mesh_with_joints(
    vertices: np.ndarray,
    faces: np.ndarray,
    joints: np.ndarray,
    parents: np.ndarray,
    output_path: Path,
):
    output_path = Path(output_path)

    fig = plt.figure(figsize=(6.8, 7.6), dpi=220)
    ax = fig.add_subplot(111, projection="3d")

    add_mesh(
        ax,
        vertices,
        faces,
        face_colors=(0.78, 0.81, 0.88, 1.0),
        edge_color=(0.15, 0.15, 0.15, 0.06),
        line_width=0.03,
        alpha=0.55,
    )

    display_joints = to_display_coordinates(joints)

    ax.scatter(
        display_joints[:, 0],
        display_joints[:, 1],
        display_joints[:, 2],
        c="crimson",
        s=34,
        depthshade=False,
    )

    parents = np.asarray(parents, dtype=np.int64)
    for child_idx, parent_idx in enumerate(parents):
        if parent_idx < 0:
            continue
        p0 = display_joints[parent_idx]
        p1 = display_joints[child_idx]
        ax.plot(
            [p0[0], p1[0]],
            [p0[1], p1[1]],
            [p0[2], p1[2]],
            color="crimson",
            linewidth=1.8,
        )

    ax.set_title("Stage B: Shaped Mesh and Regressed Joints", fontsize=13, pad=12)

    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(output_path, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)

def save_shape_difference_heatmap(
    v_template: np.ndarray,
    v_shaped: np.ndarray,
    faces: np.ndarray,
    output_path: Path,
):
    """
    可选辅助图：显示 shape deformation 的位移大小。
    """
    output_path = Path(output_path)

    displacement = np.linalg.norm(v_shaped - v_template, axis=1)
    face_colors, scalar_map = vertex_values_to_face_colors(
        displacement,
        faces,
        cmap_name="viridis",
    )

    fig = plt.figure(figsize=(6.2, 7.0), dpi=220)
    ax = fig.add_subplot(111, projection="3d")

    add_mesh(ax, v_shaped, faces, face_colors=face_colors)
    ax.set_title("Shape Deformation Magnitude", fontsize=13, pad=12)

    colorbar = fig.colorbar(scalar_map, ax=ax, shrink=0.66, pad=0.02)
    colorbar.set_label("||v_shaped - v_template||", fontsize=10)

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)

def save_pose_offset_heatmap(
    vertices: np.ndarray,
    faces: np.ndarray,
    pose_offsets: np.ndarray,
    output_path: Path,
):
    """
    保存任务 4 主图。

    网格位置使用 v_posed；
    颜色表示每个顶点 pose_offsets 的长度。
    """
    output_path = Path(output_path)

    offset_magnitude = np.linalg.norm(pose_offsets, axis=1)

    face_colors, scalar_map = vertex_values_to_face_colors(
        offset_magnitude,
        faces,
        cmap_name="inferno",
    )

    fig = plt.figure(figsize=(6.5, 7.0), dpi=220)
    ax = fig.add_subplot(111, projection="3d")

    add_mesh(
        ax,
        vertices,
        faces,
        face_colors=face_colors,
        edge_color=(0.10, 0.10, 0.10, 0.035),
        line_width=0.02,
        alpha=1.0,
    )

    ax.set_title(
        "Stage C: Pose Corrective Offset Magnitude",
        fontsize=13,
        pad=10,
    )

    colorbar = fig.colorbar(
        scalar_map,
        ax=ax,
        shrink=0.66,
        pad=0.02,
    )
    colorbar.set_label(
        r"$\|\mathrm{pose\_offsets}\|$",
        fontsize=11,
    )

    fig.text(
        0.5,
        0.035,
        "Mesh: v_posed = v_shaped + pose_offsets  (before LBS)",
        ha="center",
        fontsize=9,
    )

    fig.tight_layout(rect=(0, 0.07, 1, 0.98))
    fig.savefig(
        output_path,
        bbox_inches="tight",
        pad_inches=0.04,
    )
    plt.close(fig)

def save_lbs_result_with_skeleton(
    vertices: np.ndarray,
    faces: np.ndarray,
    joints: np.ndarray,
    parents: np.ndarray,
    output_path: Path,
):
    """
    保存任务 5 主图：
    最终 LBS 人体网格 + 最终姿态下的骨架。
    """
    output_path = Path(output_path)

    fig = plt.figure(figsize=(7.0, 7.8), dpi=220)
    ax = fig.add_subplot(111, projection="3d")

    # 轻微半透明，确保骨架在人体内部也能看见
    add_mesh(
        ax,
        vertices,
        faces,
        face_colors=(0.63, 0.72, 0.88, 1.0),
        edge_color=(0.10, 0.12, 0.18, 0.04),
        line_width=0.02,
        alpha=0.78,
    )

    display_joints = to_display_coordinates(joints)
    parents = np.asarray(parents, dtype=np.int64)

    # 先绘制骨架连线
    for child_idx, parent_idx in enumerate(parents):
        if parent_idx < 0:
            continue

        parent_joint = display_joints[parent_idx]
        child_joint = display_joints[child_idx]

        ax.plot(
            [parent_joint[0], child_joint[0]],
            [parent_joint[1], child_joint[1]],
            [parent_joint[2], child_joint[2]],
            color="crimson",
            linewidth=2.0,
        )

    # 再画关节，确保红点覆盖在线上
    ax.scatter(
        display_joints[:, 0],
        display_joints[:, 1],
        display_joints[:, 2],
        c="crimson",
        s=38,
        depthshade=False,
    )

    ax.set_title(
        "Stage D: Final Linear Blend Skinning Result",
        fontsize=13,
        pad=12,
    )

    fig.text(
        0.5,
        0.035,
        "Mesh: final verts after weighted joint transformations",
        ha="center",
        fontsize=9,
    )

    fig.tight_layout(rect=(0, 0.07, 1, 0.98))
    fig.savefig(
        output_path,
        bbox_inches="tight",
        pad_inches=0.04,
    )
    plt.close(fig)
    