from pathlib import Path
from typing import Dict, Any, List


def write_dicom_sr(study_dir: str, impression: str, findings: List[str], structured: Dict[str, Any], provenance: Dict[str, Any], out_dir: str) -> str:
    """Format report text and write a DICOM SR via MONAI Deploy App SDK.

    Falls back to writing a plain text file with .dcm extension if the SDK is
    not available. Returns the path to the written SR file."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    text = _format_sr_text(impression, findings, structured, provenance)

    try:
        from monai.deploy.operators import DICOMTextSRWriterOperator
        op = DICOMTextSRWriterOperator(app=None, output_folder=out)
        return _run_sr_writer(op, study_dir, text)
    except Exception:
        # Fallback: just write text to a fake DICOM file
        sr = out / "report_sr.dcm"
        sr.write_text(text)
        return str(sr)


def write_dicom_seg(study_dir: str, seg_nifti: str, out_dir: str) -> str:
    """Write a DICOM SEG from a NIfTI mask using MONAI Deploy App SDK.

    Falls back to copying the NIfTI path to a .dcm placeholder."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    try:
        from monai.deploy.operators import DICOMSegmentationWriterOperator
        op = DICOMSegmentationWriterOperator(app=None, output_folder=out, segment_descriptions=["Lesion"])
        return _run_seg_writer(op, study_dir, seg_nifti)
    except Exception:
        seg = out / "seg.dcm"
        Path(seg).write_text("segmentation placeholder")
        return str(seg)


def _format_sr_text(impression: str, findings: List[str], structured: Dict[str, Any], provenance: Dict[str, Any]) -> str:
    lines = ["IMPRESSION:", impression, "", "FINDINGS:"]
    lines += [f"- {f}" for f in findings[:6]]
    lines += ["", "QUANT:", f"- lesion_volume_cc: {structured.get('lesion_volume_cc', 0)}", f"- num_lesions: {structured.get('num_lesions', 0)}",
              "", "PROVENANCE:", f"- {provenance}"]
    lines += ["", "DISCLAIMER:", "AI-generated. Research use only."]
    return "\n".join(lines)


def _run_sr_writer(op, study_dir: str, text: str) -> str:
    """Helper to invoke DICOMTextSRWriterOperator."""
    try:
        op(study_list=[study_dir], text=text)
        outputs = sorted(Path(op.output_folder).glob("*.dcm"))
        if outputs:
            return str(outputs[0])
    except Exception:
        pass
    # Fallback
    sr = Path(op.output_folder) / "report_sr.dcm"
    sr.write_text(text)
    return str(sr)


def _run_seg_writer(op, study_dir: str, seg_nifti: str) -> str:
    """Helper to invoke DICOMSegmentationWriterOperator."""
    try:
        op(study_list=[study_dir], seg_image=seg_nifti)
        outputs = sorted(Path(op.output_folder).glob("*.dcm"))
        if outputs:
            return str(outputs[0])
    except Exception:
        pass
    seg = Path(op.output_folder) / "seg.dcm"
    Path(seg).write_text("segmentation placeholder")
    return str(seg)
