from pathlib import Path

# Base directory for all job data
BASE = Path("/data/jobs")
BASE.mkdir(parents=True, exist_ok=True)

# Volume threshold for abnormality in cubic centimeters
ABNORMAL_THRESHOLD_CC = 0.5
