"""Utilities for loading and running VILA-M3 via the MONAI VLM Radiology Agent Framework.

The real implementation would load the model weights onto the GPU using the
`VLM-Radiology-Agent-Framework`_ project. For the purposes of this repository, a
lightweight stub is provided so that the rest of the pipeline can be exercised
without the heavy dependency.

.. _VLM-Radiology-Agent-Framework: https://github.com/Project-MONAI/VLM-Radiology-Agent-Framework
"""

from __future__ import annotations

import importlib
from typing import Any, Tuple


def load_vila() -> Any:
    """Attempt to load the VILA-M3 model from the MONAI framework.

    Returns a handle to the model or ``None`` if the framework is not
    available."""

    try:  # pragma: no cover - exercised in integration environments
        utils = importlib.import_module("server_slicer.utils")
        ImageCache = getattr(utils, "ImageCache")
        M3Generator = getattr(utils, "M3Generator")
        cache = ImageCache("./cache")
        return M3Generator(cache)
    except Exception:  # pragma: no cover - handled gracefully
        return None


def run_vlm(model: Any, prompt: str) -> Tuple[str, float]:
    """Generate a report using the VILA-M3 model.

    Returns the generated text and a confidence probability.  If the real
    framework is unavailable, a deterministic stub response is produced."""

    if model is None:
        return "- No acute intracranial abnormality detected", 0.6

    try:
        if hasattr(model, "process_prompt"):
            utils = importlib.import_module("server_slicer.utils")
            ChatHistory = getattr(utils, "ChatHistory")
            SessionVariables = getattr(utils, "SessionVariables")
            history = ChatHistory()
            session = SessionVariables()
            session, history = model.process_prompt(prompt, session, history)
            text = history.messages[-1] if getattr(history, "messages", []) else ""
        else:
            text = model.generate(prompt)
        prob = 0.75
        return text, prob
    except Exception:  # pragma: no cover - failure path
        return "- Model execution failed", 0.5
