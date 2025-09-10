from pathlib import Path
from typing import Dict, Any, List


def write_dicom_sr(
    study_dir: str,
    impression: str,
    findings: List[str],
    structured: Dict[str, Any],
    provenance: Dict[str, Any],
    out_dir: str,
) -> str:
    """Format report text and write a DICOM SR via MONAI Deploy App SDK.

    Raises ``RuntimeError`` if the MONAI Deploy operator is unavailable or fails
    to generate an SR."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    text = _format_sr_text(impression, findings, structured, provenance)

    try:
        from monai.deploy.operators import DICOMTextSRWriterOperator
    except Exception as e:  # pragma: no cover - import guarded
        raise RuntimeError(
            "DICOMTextSRWriterOperator is not available. Install monai-deploy-app-sdk."
        ) from e

    op = DICOMTextSRWriterOperator(app=None, output_folder=out)
    return _run_sr_writer(op, study_dir, text)


def write_dicom_seg(study_dir: str, seg_nifti: str, out_dir: str) -> str:
    """Write a DICOM SEG from a NIfTI mask using MONAI Deploy App SDK.

    Raises ``RuntimeError`` if the MONAI Deploy operator is unavailable or fails
    to generate a SEG."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    try:
        from monai.deploy.operators import DICOMSegmentationWriterOperator
    except Exception as e:  # pragma: no cover - import guarded
        raise RuntimeError(
            "DICOMSegmentationWriterOperator is not available. Install monai-deploy-app-sdk."
        ) from e

    op = DICOMSegmentationWriterOperator(app=None, output_folder=out, segment_descriptions=["Lesion"])
    return _run_seg_writer(op, study_dir, seg_nifti)


def _format_sr_text(impression: str, findings: List[str], structured: Dict[str, Any], provenance: Dict[str, Any]) -> str:
    lines = ["IMPRESSION:", impression, "", "FINDINGS:"]
    lines += [f"- {f}" for f in findings[:6]]
    lines += ["", "QUANT:", f"- lesion_volume_cc: {structured.get('lesion_volume_cc', 0)}", f"- num_lesions: {structured.get('num_lesions', 0)}",
              "", "PROVENANCE:", f"- {provenance}"]
    lines += ["", "DISCLAIMER:", "AI-generated. Research use only."]
    return "\n".join(lines)


def _run_sr_writer(op, study_dir: str, text: str) -> str:
    """Helper to invoke :class:`DICOMTextSRWriterOperator`.

    Returns the path to the generated SR and surfaces any errors from the
    underlying operator."""
    try:
        op(study_list=[study_dir], text=text)
    except Exception as e:
        raise RuntimeError("Failed to write DICOM SR") from e

    outputs = sorted(Path(op.output_folder).glob("*.dcm"))
    if not outputs:
        raise RuntimeError("DICOM SR writer produced no output")
    return str(outputs[0])


def _run_seg_writer(op, study_dir: str, seg_nifti: str) -> str:
    """Helper to invoke :class:`DICOMSegmentationWriterOperator`.

    Returns the path to the generated SEG and surfaces any errors from the
    underlying operator."""
    try:
        op(study_list=[study_dir], seg_image=seg_nifti)
    except Exception as e:
        raise RuntimeError("Failed to write DICOM SEG") from e

    outputs = sorted(Path(op.output_folder).glob("*.dcm"))
    if not outputs:
        raise RuntimeError("DICOM SEG writer produced no output")
    return str(outputs[0])
