# SMPL Model Setup

This repository does not distribute `SMPL_NEUTRAL.pkl`.

The SMPL model file is subject to its original license and must be obtained separately for educational or non-commercial use.

## Required File

Download the neutral SMPL model through the official SMPL website and place it at:

```text
models/smpl/SMPL_NEUTRAL.pkl
```

## Expected Directory Structure

```text
models/
└── smpl/
    ├── README.md
    └── SMPL_NEUTRAL.pkl
```

`SMPL_NEUTRAL.pkl` is intentionally excluded from Git via `.gitignore`.

After placing the file correctly, run Work8 from the project root:

```bat
.venv-work8\Scripts\python.exe -m src.work8.run_all
```
