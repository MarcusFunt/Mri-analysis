from pathlib import Path
from typing import Tuple


def run_brats(study_dir: str, mask_out: str | None) -> Tuple[str, float, int]:
    """Placeholder BraTS runner.

    In a real deployment this would load a MONAI bundle, perform segmentation
    and write the resulting mask to ``mask_out``. Here we simply create an empty
    file and return made-up statistics."""
    out = Path(mask_out) if mask_out else Path(study_dir).parent / "work" / "brats_seg.nii.gz"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(b"")
    return str(out), 12.3, 2
