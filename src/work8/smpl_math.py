import torch

from smplx.lbs import (
    batch_rigid_transform,
    batch_rodrigues,
    blend_shapes,
    vertices2joints,
)


def get_demo_betas(device="cpu", dtype=torch.float32):
    """
    任务 3、4、5、7 共用的一组固定 shape 参数。
    """
    betas = torch.zeros((1, 10), dtype=dtype, device=device)

    betas[0, 0] = 1.5
    betas[0, 1] = -1.0
    betas[0, 2] = 0.8

    return betas


def get_demo_pose(device="cpu", dtype=torch.float32):
    """
    构造一组固定姿态：

    - 躯干轻微扭转
    - 右肩抬起
    - 右肘弯曲

    global_orient: 根关节 pelvis 的整体旋转，维度为 [1, 3]
    body_pose: 剩余 23 个关节的轴角旋转，维度为 [1, 69]
    """
    global_orient = torch.zeros((1, 3), dtype=dtype, device=device)
    body_pose = torch.zeros((1, 69), dtype=dtype, device=device)

    def set_joint_axis_angle(joint_id, rx=0.0, ry=0.0, rz=0.0):
        """
        body_pose 不包含 0 号 pelvis。

        例如：
        joint_id = 17 表示 right_shoulder，
        它对应 body_pose 中第 16 组轴角参数。
        """
        if joint_id < 1 or joint_id > 23:
            raise ValueError(f"joint_id 必须位于 [1, 23]，当前为 {joint_id}")

        start = (joint_id - 1) * 3
        body_pose[0, start:start + 3] = torch.tensor(
            [rx, ry, rz],
            dtype=dtype,
            device=device,
        )

    # spine3：躯干轻微扭转
    set_joint_axis_angle(9, ry=0.20)

    # right_shoulder：右臂抬起
    set_joint_axis_angle(17, rz=-1.10)

    # right_elbow：右肘弯曲
    set_joint_axis_angle(19, rz=-1.00)

    return global_orient, body_pose


def compute_v_shaped_and_joints(model, betas):
    """
    任务 3 的核心计算：

    v_shaped = v_template + B_S(beta)
    J = J_regressor(v_shaped)
    """
    device = betas.device
    dtype = betas.dtype

    v_template = model.v_template.unsqueeze(0).to(
        device=device,
        dtype=dtype,
    )
    shapedirs = model.shapedirs.to(device=device, dtype=dtype)
    j_regressor = model.J_regressor.to(device=device, dtype=dtype)

    v_shaped = v_template + blend_shapes(betas, shapedirs)
    joints = vertices2joints(j_regressor, v_shaped)

    return {
        "v_template": v_template,
        "v_shaped": v_shaped,
        "J": joints,
    }


def compute_pose_correctives(
    model,
    betas,
    global_orient,
    body_pose,
):
    """
    任务 4 的核心计算：

    1. 先得到 v_shaped 与 J
    2. 轴角姿态 -> 旋转矩阵 rot_mats
    3. pose_feature = R(theta) - I
    4. pose_offsets = pose_feature @ posedirs
    5. v_posed = v_shaped + pose_offsets

    注意：
    这里得到的是 v_posed，还没有进行 LBS。
    """
    shape_result = compute_v_shaped_and_joints(model, betas)

    v_template = shape_result["v_template"]
    v_shaped = shape_result["v_shaped"]
    joints = shape_result["J"]

    device = betas.device
    dtype = betas.dtype
    batch_size = betas.shape[0]

    full_pose = torch.cat(
        [global_orient, body_pose],
        dim=1,
    )

    rot_mats = batch_rodrigues(
        full_pose.reshape(-1, 3)
    ).reshape(batch_size, -1, 3, 3)

    identity = torch.eye(
        3,
        dtype=dtype,
        device=device,
    )

    pose_feature = (
        rot_mats[:, 1:, :, :] - identity
    ).reshape(batch_size, -1)

    posedirs = model.posedirs.to(device=device, dtype=dtype)

    pose_offsets = torch.matmul(
        pose_feature,
        posedirs,
    ).reshape(batch_size, -1, 3)

    v_posed = v_shaped + pose_offsets

    return {
        "v_template": v_template,
        "v_shaped": v_shaped,
        "J": joints,
        "full_pose": full_pose,
        "rot_mats": rot_mats,
        "pose_feature": pose_feature,
        "pose_offsets": pose_offsets,
        "v_posed": v_posed,
    }

def compute_manual_lbs(
    model,
    betas,
    global_orient,
    body_pose,
):
    """
    任务 5：完整手写 LBS。

    输入：
    - betas
    - global_orient
    - body_pose

    输出：
    - v_template
    - v_shaped
    - J
    - v_posed
    - J_transformed
    - A
    - verts
    """

    # 先复用任务 4：
    # v_template -> v_shaped -> J -> v_posed
    result = compute_pose_correctives(
        model=model,
        betas=betas,
        global_orient=global_orient,
        body_pose=body_pose,
    )

    v_posed = result["v_posed"]
    joints = result["J"]
    rot_mats = result["rot_mats"]

    device = betas.device
    dtype = betas.dtype
    batch_size = betas.shape[0]

    parents = model.parents.to(device=device)
    lbs_weights = model.lbs_weights.to(
        device=device,
        dtype=dtype,
    )

    num_joints = model.J_regressor.shape[0]

    # 1. 沿运动学树计算关节的全局刚体变换
    # J_transformed：最终姿态下各关节的位置
    # A：去除了 bind-pose 影响后的蒙皮变换矩阵
    joints_transformed, A = batch_rigid_transform(
        rot_mats=rot_mats,
        joints=joints,
        parents=parents,
        dtype=dtype,
    )

    # 2. 对每个顶点，将 24 个关节变换按 LBS 权重加权
    W = lbs_weights.unsqueeze(0).expand(
        batch_size,
        -1,
        -1,
    )

    T = torch.matmul(
        W,
        A.reshape(batch_size, num_joints, 16),
    ).reshape(batch_size, -1, 4, 4)

    # 3. 齐次坐标形式下，对每个顶点应用加权后的变换矩阵
    homogeneous_coordinate = torch.ones(
        (
            batch_size,
            v_posed.shape[1],
            1,
        ),
        dtype=dtype,
        device=device,
    )

    v_posed_homo = torch.cat(
        [v_posed, homogeneous_coordinate],
        dim=2,
    )

    v_homo = torch.matmul(
        T,
        v_posed_homo.unsqueeze(-1),
    )

    verts = v_homo[:, :, :3, 0]

    result.update(
        {
            "J_transformed": joints_transformed,
            "A": A,
            "verts": verts,
        }
    )

    return result
