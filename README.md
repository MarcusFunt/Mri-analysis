# MRI Analysis

This repository has been cleaned to remove raw MRI data from version control and provide a starting point for experiments using [NVIDIA MONAI](https://monai.io/).

## Setup

1. Create a Python environment and install dependencies:

```bash
pip install -r requirements.txt
```

2. Place your MRI data under the `data/` directory (which is ignored by git).

3. Verify that MONAI is installed and accessible:

```bash
python prep_monai.py
```

## Notes

The original raw files have been moved to `data/raw/` locally and are no longer tracked in git.
