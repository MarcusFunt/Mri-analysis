import json
import logging
import uuid
import zipfile
from pathlib import Path

import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .contracts import AgentAnalyzeReq, AgentAnalyzeResp
from .app_sdk_io import write_dicom_sr, write_dicom_seg
from .settings import BASE, ABNORMAL_THRESHOLD_CC
from .job_store import JobStore

AGENT_URL = "http://agent:8001/analyze"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)
store = JobStore()


@app.post("/upload")
async def upload(study: UploadFile = File(...)):
    if study.content_type != "application/zip":
        raise HTTPException(400, "file must be a ZIP archive")
    study.file.seek(0)
    if not zipfile.is_zipfile(study.file):
        raise HTTPException(400, "invalid ZIP file")

    job_id = str(uuid.uuid4())
    job = BASE / job_id
    dcm = job / "dicom"
    work = job / "work"
    out = job / "out"
    for p in (dcm, work, out):
        p.mkdir(parents=True, exist_ok=True)

    study.file.seek(0)
    with zipfile.ZipFile(study.file) as z:
        for member in z.namelist():
            member_path = (dcm / member).resolve()
            if not str(member_path).startswith(str(dcm.resolve())):
                raise HTTPException(400, "invalid file path in zip")
            z.extract(member, dcm)

    store.create(job_id, {"dicom": str(dcm), "work": str(work), "out": str(out)})
    return {"job_id": job_id}


@app.post("/analyze/{job_id}")
def analyze(job_id: str, anatomy: dict):
    job = store.get(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    paths = job["paths"]
    payload = AgentAnalyzeReq(
        study_dir=paths["dicom"],
        anatomy=anatomy.get("anatomy", "brain"),
        tools=["brats", "wmh"],
        constraints={
            "style": "radiology-impression-first",
            "limit_findings": 6,
            "explicit_uncertainty": True,
            "regulatory_disclaimer": True,
        },
        abnormal_threshold_cc=ABNORMAL_THRESHOLD_CC,
    ).dict()
    store.update_state(job_id, "running")
    try:
        r = requests.post(AGENT_URL, json=payload, timeout=600)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        logger.exception("agent request failed")
        raise HTTPException(502, "agent request failed") from e
    except ValueError as e:
        logger.exception("invalid JSON from agent")
        raise HTTPException(502, "invalid agent response") from e
    resp = AgentAnalyzeResp(**data)

    # Write DICOM SR/SEG via App SDK
    sr_path = write_dicom_sr(
        study_dir=paths["dicom"],
        impression=resp.impression,
        findings=resp.findings,
        structured=resp.structured,
        provenance=resp.provenance,
        out_dir=paths["out"],
    )
    seg_path = None
    if (
        not resp.normal
        and resp.structured.get("lesion_volume_cc", 0) > ABNORMAL_THRESHOLD_CC
        and (resp.aux or {}).get("seg_nifti")
    ):
        seg_path = write_dicom_seg(
            study_dir=paths["dicom"],
            seg_nifti=resp.aux["seg_nifti"],
            out_dir=paths["out"],
        )

    result = {
        "job_id": job_id,
        "state": "done",
        "normal": resp.normal,
        "confidence": resp.confidence,
        "impression": resp.impression,
        "findings": resp.findings,
        "downloads": {
            "dicom_sr": f"/download/sr/{Path(sr_path).name}",
            "dicom_seg": f"/download/seg/{Path(seg_path).name}" if seg_path else None,
            "json": f"/download/json/{job_id}.json",
        },
    }
    (Path(paths["out"]) / f"{job_id}.json").write_text(json.dumps(result, indent=2))
    store.set_result(job_id, result)
    return result


@app.get("/result/{job_id}")
def result(job_id: str):
    job = store.get(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    return job.get("result") or {"job_id": job_id, "state": job["state"]}
