import os
import requests

EXPERTS = {
    "brats": {"endpoint": os.getenv("EXPERTS_URL", "http://experts:8002") + "/infer/brats"},
    "wmh": {"endpoint": os.getenv("EXPERTS_URL", "http://experts:8002") + "/infer/wmh"},
}


def run_tool(name: str, payload: dict) -> dict:
    url = EXPERTS[name]["endpoint"]
    r = requests.post(url, json=payload, timeout=600)
    r.raise_for_status()
    return r.json()
