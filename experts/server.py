from fastapi import FastAPI
from pydantic import BaseModel
from .runners.brats_runner import run_brats

app = FastAPI()


class InferReq(BaseModel):
    study_dir: str
    mask_out: str | None = None


@app.post("/infer/brats")
def infer_brats(req: InferReq):
    seg, vol_cc, n = run_brats(req.study_dir, req.mask_out)
    return {"ok": True, "seg": seg, "lesion_volume_cc": vol_cc, "num_lesions": n}


@app.post("/infer/wmh")
def infer_wmh(req: InferReq):
    # Placeholder WMH implementation
    return {"ok": True, "seg": None, "lesion_volume_cc": 0.0, "num_lesions": 0}
