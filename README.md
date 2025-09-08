# MRI Analysis with MONAI

This repository contains MRI data and helper scripts for preparing it for use with NVIDIA's [MONAI](https://monai.io/) framework.

## Setup

```bash
pip install -r requirements.txt
```

## Data layout

Raw DICOM files are stored under `data/raw`. The preparation script converts them into NIfTI images saved under `data/nifti`.

## Usage

Run the conversion script:

```bash
python prepare_monai_dataset.py
```

This will generate NIfTI files suitable for MONAI training pipelines.
