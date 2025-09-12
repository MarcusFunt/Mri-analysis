# MRI Auto-Report (Normal vs Abnormal)

This repository implements a minimal end-to-end pipeline for generating a radiology report from an uploaded brain MRI study. The entire pipeline now runs locally as a standalone Python desktop application built with Tkinter—no separate web services are required.

* **Desktop App (Tkinter)** – upload a study, run analysis and view results locally.

The abnormality volume threshold can be customized via the `ABNORMAL_THRESHOLD_CC` environment variable.

> **Note**: The heavy AI models are stubbed for development purposes; the code is structured so real models can be integrated later.

## Development

Install Python dependencies and run tests:

```bash
pip install -r requirements.txt
pytest
```

Launch the desktop interface:

```bash
python gui/app.py
```
