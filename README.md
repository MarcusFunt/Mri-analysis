# MRI Auto-Report (Normal vs Abnormal)

This repository implements a minimal end-to-end pipeline for generating a
radiology report from an uploaded brain MRI study. It follows the architecture
specified in the project brief:

* **UI (React)** – single page app for uploading a study and displaying the
  result.
* **Gateway (FastAPI)** – orchestrates upload, analysis and packaging of DICOM
  SR/SEG outputs.
* **Agent Service** – wraps the MONAI Radiology Agent Framework and VILA-M3 to
  draft the report and coordinate expert tools.
* **Expert Hub** – microservice hosting segmentation models such as BraTS.

A `docker-compose` file is provided to launch all services together. Each job's
artifacts are stored under `/data/jobs/<job_id>/` on the gateway container.

> **Note**: The heavy AI models are stubbed for development purposes; the code is
> structured so real models can be integrated later.

## Desktop application

For a quick demonstration without running the full stack, a lightweight desktop
GUI is provided.  It calls into the same agent logic with stubbed AI models so
that a second-opinion report can be generated entirely offline.

```bash
pip install -r requirements.txt
python desktop_app.py
```

Use the *Analyze* button to process a selected MRI study folder.  The interface
reports whether the study appears normal or abnormal along with an impression
and bullet list of findings.

## Development

Install Python dependencies and run tests:

```bash
pip install -r requirements.txt
pytest
```

To run the full stack with Docker:

```bash
docker compose up --build
```
