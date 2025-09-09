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
