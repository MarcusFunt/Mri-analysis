from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import shutil, zipfile, requests, uuid, json
from .contracts import AgentAnalyzeReq, AgentAnalyzeResp
from .app_sdk_io import write_dicom_sr, write_dicom_seg
from .settings import BASE, ABNORMAL_THRESHOLD_CC

AGENT_URL = "http://agent:8001/analyze"

app = FastAPI()
STATE: dict = {}


@app.post("/upload")
async def upload(study: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    job = BASE / job_id
    dcm = job / "dicom"
    work = job / "work"
    out = job / "out"
    for p in (dcm, work, out):
        p.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(study.file) as z:
        z.extractall(dcm)
    STATE[job_id] = {"state": "uploaded", "paths": {"dicom": str(dcm), "work": str(work), "out": str(out)}}
    return {"job_id": job_id}


@app.post("/analyze/{job_id}")
def analyze(job_id: str, anatomy: dict):
    if job_id not in STATE:
        raise HTTPException(404, "job not found")
    paths = STATE[job_id]["paths"]
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
    ).dict()
    STATE[job_id]["state"] = "running"
    r = requests.post(AGENT_URL, json=payload, timeout=600)
    r.raise_for_status()
    resp = AgentAnalyzeResp(**r.json())

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
    STATE[job_id]["state"] = "done"
    STATE[job_id]["result"] = result
    return result


@app.get("/result/{job_id}")
def result(job_id: str):
    if job_id not in STATE:
        raise HTTPException(404, "job not found")
    return STATE[job_id].get("result") or {"job_id": job_id, "state": STATE[job_id]["state"]}
