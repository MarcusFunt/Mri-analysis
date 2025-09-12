from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class AgentAnalyzeReq(BaseModel):
    study_dir: str
    anatomy: str = "brain"
    tools: List[str] = ["brats"]
    constraints: Dict[str, Any] = {}
    abnormal_threshold_cc: Optional[float] = None


class AgentAnalyzeResp(BaseModel):
    normal: bool
    confidence: float
    impression: str
    findings: List[str]
    structured: Dict[str, Any]
    provenance: Dict[str, Any]
    aux: Optional[Dict[str, Any]] = None
