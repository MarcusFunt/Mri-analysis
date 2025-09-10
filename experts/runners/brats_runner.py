"""Run BraTS tumour segmentation on a DICOM study.

This runner downloads the `brats_mri_segmentation` bundle from the MONAI model
zoo, converts the given DICOM series into a 3D volume, performs inference and
writes the resulting mask as a NIfTI file.  It also computes simple lesion
statistics which are returned to the caller.

The implementation is intentionally light–weight and executes entirely on the
CPU so it can run inside the execution environment used for the unit tests.  It
is **not** optimised for speed nor intended for clinical use.
"""

from pathlib import Path
from typing import Tuple

import nibabel as nib
import numpy as np
import pydicom
import torch
from monai.bundle import BundleClient
from monai.inferers import sliding_window_inference
from scipy.ndimage import label


def _load_dicom_volume(study_dir: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load a DICOM study into a 3D numpy array.

    Returns ``(volume, affine, spacing)`` where ``volume`` has shape ``(D, H, W)``
    and spacing is expressed in millimetres.
    """

    files = sorted(Path(study_dir).glob("*.dcm"))
    if not files:
        raise FileNotFoundError(f"no DICOM files found in {study_dir}")

    slices = [pydicom.dcmread(str(f)) for f in files]
    slices.sort(key=lambda d: int(getattr(d, "InstanceNumber", 0)))
    volume = np.stack([s.pixel_array for s in slices]).astype(np.float32)

    px, py = map(float, slices[0].PixelSpacing)
    pz = float(getattr(slices[0], "SliceThickness", 1.0))
    spacing = np.array([px, py, pz], dtype=np.float32)
    affine = np.diag(np.append(spacing, 1.0))
    return volume, affine, spacing


def _load_bundle() -> tuple[torch.nn.Module, tuple[int, int, int]]:
    """Download and load the BraTS bundle returning the model and ROI size."""

    client = BundleClient(name="brats_mri_segmentation", bundle_dir="/tmp/brats_bundle")
    client.pull()  # download if necessary
    network = client.load("model.ts")  # TorchScript model
    roi_size = tuple(client.configs["inference"].get("roi_size", (128, 128, 128)))
    return network, roi_size


def run_brats(study_dir: str, mask_out: str | None) -> Tuple[str, float, int]:
    volume, affine, spacing = _load_dicom_volume(study_dir)

    # network expects 4 modality input; replicate single modality if necessary
    if volume.ndim == 3:
        volume = np.stack([volume] * 4, axis=0)

    model, roi_size = _load_bundle()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    data = torch.from_numpy(volume[None]).to(device)
    with torch.no_grad():
        logits = sliding_window_inference(data, roi_size, 1, model)
    mask = torch.argmax(logits, dim=1).cpu().numpy().astype(np.uint8)[0]

    out = Path(mask_out) if mask_out else Path(study_dir).parent / "work" / "brats_seg.nii.gz"
    out.parent.mkdir(parents=True, exist_ok=True)
    nib.save(nib.Nifti1Image(mask, affine), str(out))

    # compute lesion statistics
    voxel_vol_cc = float(np.prod(spacing) / 1000.0)
    labeled, n = label(mask > 0)
    vol_cc = float((mask > 0).sum() * voxel_vol_cc)

    return str(out), vol_cc, int(n)
