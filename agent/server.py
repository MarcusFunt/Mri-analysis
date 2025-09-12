from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from .tools_registry import EXPERTS, run_tool
from .vila_loader import load_vila, run_vlm
from .settings import ABNORMAL_THRESHOLD_CC

app = FastAPI()
vlm = load_vila()


class AnalyzeReq(BaseModel):
    study_dir: str
    anatomy: str = "brain"
    tools: List[str] = ["brats"]
    constraints: Dict[str, Any] = {}
    abnormal_threshold_cc: Optional[float] = None


@app.post("/analyze")
def analyze(req: AnalyzeReq):
    evidence: Dict[str, Dict[str, Any]] = {}
    seg_path: Optional[str] = None
    for tool in req.tools:
        if tool in EXPERTS:
            out = run_tool(tool, {"study_dir": req.study_dir})
            evidence[tool] = out
            if "seg" in out:
                seg_path = out["seg"]

    stats = _summarize_stats(evidence)
    prompt = render_prompt(req.anatomy, stats, req.constraints)

    text, prob = run_vlm(vlm, prompt)
    threshold = (
        req.abnormal_threshold_cc
        if req.abnormal_threshold_cc is not None
        else ABNORMAL_THRESHOLD_CC
    )
    abnormal = (stats.get("lesion_volume_cc", 0) or 0) > threshold

    return {
        "normal": not abnormal,
        "confidence": max(prob, 0.5),
        "impression": _impression(text, abnormal),
        "findings": _bullets(text),
        "structured": {
            "lesion_volume_cc": stats.get("lesion_volume_cc", 0.0),
            "num_lesions": stats.get("num_lesions", 0),
        },
        "provenance": {
            "vlm": {"name": "VILA-M3", "ckpt": "<fill>"},
            "tools": [{"name": k, "version": "<fill>"} for k in req.tools],
        },
        "aux": {"seg_nifti": seg_path},
    }


def render_prompt(anatomy: str, stats: Dict[str, Any], constraints: Dict[str, Any]) -> str:
    return (
        f"You are a radiology assistant for {anatomy} MRI.\n"
        f"Evidence (JSON): {stats}\n"
        "Write an IMPRESSION-FIRST report. State NORMAL vs ABNORMAL with uncertainty. <=6 findings. Avoid overdiagnosis."
    )


def _summarize_stats(ev: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    s: Dict[str, Any] = {}
    if "brats" in ev:
        s["lesion_volume_cc"] = ev["brats"].get("lesion_volume_cc", 0.0)
        s["num_lesions"] = ev["brats"].get("num_lesions", 0)
    return s


def _impression(text: str, abnormal: bool) -> str:
    prefix = "Abnormal brain MRI. " if abnormal else "No convincing acute intracranial abnormality. "
    return prefix + text.strip()[:800]


def _bullets(text: str) -> List[str]:
    return [ln.strip("- ").strip() for ln in text.split("\n") if ln.strip().startswith("-")][:6]

