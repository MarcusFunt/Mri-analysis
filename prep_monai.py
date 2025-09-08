"""Utility script to verify MONAI installation."""

import importlib
import sys

def check_monai() -> None:
    """Check that MONAI can be imported."""
    try:
        importlib.import_module("monai")
    except ModuleNotFoundError as exc:  # pragma: no cover - simple installation check
        raise SystemExit("MONAI is not installed. Run `pip install -r requirements.txt`.") from exc

if __name__ == "__main__":
    check_monai()
    print("MONAI is available.")
