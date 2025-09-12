"""
Local end-to-end analysis pipeline for the desktop application.

Combines the previous gateway and agent functionality into a single
function that operates purely on local files.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict

from agent.vila_loader import load_vila, run_vlm
from agent.server import render_prompt, _impression, _bullets
from gateway.app_sdk_io import write_dicom_sr, write_dicom_seg
from gateway.settings import ABNORMAL_THRESHOLD_CC


def analyze_zip(zip_path: str, anatomy: str = "brain") -> Dict[str, Any]:
    """Run the MRI analysis pipeline on a ZIP archive.

    The archive is extracted into a temporary working directory, BraTS
    segmentation is performed locally, a VLM drafts the report and DICOM SR/SEG
    files are optionally written.  Returns a dictionary mirroring the previous
    gateway response structure.
    """
    with TemporaryDirectory() as tmpdir:
        job = Path(tmpdir)
        dcm = job / "dicom"
        work = job / "work"
        out = job / "out"
        for p in (dcm, work, out):
            p.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path) as zf:
            for member in zf.namelist():
                member_path = (dcm / member).resolve()
                if not str(member_path).startswith(str(dcm.resolve())):
                    raise ValueError("invalid file path in zip")
                zf.extract(member, dcm)

        from experts.runners.brats_runner import run_brats

        seg_path, vol_cc, n_lesions = run_brats(str(dcm), str(work / "brats_seg.nii.gz"))
        stats = {"lesion_volume_cc": vol_cc, "num_lesions": n_lesions}

        try:
            vlm = load_vila()
        except Exception:
            vlm = None
        prompt = render_prompt(anatomy, stats, {})
        text, prob = run_vlm(vlm, prompt)
        abnormal = (stats.get("lesion_volume_cc", 0) or 0) > ABNORMAL_THRESHOLD_CC

        impression = _impression(text, abnormal)
        findings = _bullets(text)

        sr_path = seg_dcm = None
        try:
            sr_path = write_dicom_sr(
                study_dir=str(dcm),
                impression=impression,
                findings=findings,
                structured=stats,
                provenance={
                    "vlm": {"name": "VILA-M3", "ckpt": "<fill>"},
                    "tools": [{"name": "brats", "version": "<fill>"}]
                },
                out_dir=str(out),
            )
            if abnormal and seg_path:
                seg_dcm = write_dicom_seg(
                    study_dir=str(dcm), seg_nifti=seg_path, out_dir=str(out)
                )
        except Exception:
            sr_path = seg_dcm = None

        result = {
            "normal": not abnormal,
            "confidence": max(prob, 0.5),
            "impression": impression,
            "findings": findings,
            "structured": stats,
            "downloads": {
                "dicom_sr": sr_path,
                "dicom_seg": seg_dcm,
            },
        }
        return result
