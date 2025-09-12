from pathlib import Path
import os

# Base directory for all job data
BASE = Path(os.getenv("JOB_BASE", "/data/jobs"))
BASE.mkdir(parents=True, exist_ok=True)

# Volume threshold for abnormality in cubic centimeters
ABNORMAL_THRESHOLD_CC = float(os.getenv("ABNORMAL_THRESHOLD_CC", "0.5"))

# Persistent job state database
JOB_DB = Path(os.getenv("JOB_DB", "/data/job_state.db"))
JOB_DB.parent.mkdir(parents=True, exist_ok=True)
