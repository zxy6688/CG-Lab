from .task1_model_info import main as run_task1
from .task2_template_weights import main as run_task2
from .task3_shape_joints import main as run_task3
from .task4_pose_correctives import main as run_task4
from .task5_lbs_result import main as run_task5
from .task6_comparison import main as run_task6
from .task7_validation import main as run_task7


TASKS = [
    ("Task 1: SMPL model information", run_task1),
    ("Task 2: template mesh and skinning weights", run_task2),
    ("Task 3: shape blend shapes and joint regression", run_task3),
    ("Task 4: pose corrective blend shapes", run_task4),
    ("Task 5: manual linear blend skinning", run_task5),
    ("Task 6: four-stage comparison grid", run_task6),
    ("Task 7: validation against official SMPL forward", run_task7),
]


def main():
    print("=" * 72)
    print("Computer Graphics Experiment 8: SMPL Linear Blend Skinning")
    print("=" * 72)

    for index, (title, task_function) in enumerate(TASKS, start=1):
        print(f"\n[{index}/7] {title}")
        print("-" * 72)
        task_function()

    print("\nAll required Work8 tasks completed successfully.")


if __name__ == "__main__":
    main()