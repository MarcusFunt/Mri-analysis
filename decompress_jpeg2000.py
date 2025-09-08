#!/usr/bin/env python3
"""Decompress JPEG 2000 DICOM files and add `.dcm` extensions.

Recursively searches through a directory tree for files without an extension.
If the file is a DICOM object whose pixel data is encoded with JPEG 2000,
this script decompresses the dataset and writes it back with the `.dcm`
extension. Optionally the original compressed file can be deleted.
"""

from __future__ import annotations

import argparse
import os
from typing import Iterable

import pydicom
from pydicom.uid import JPEG2000, JPEG2000Lossless, ExplicitVRLittleEndian

JPEG2000_UIDS = {JPEG2000, JPEG2000Lossless}


def iter_files(path: str) -> Iterable[str]:
    """Yield paths to files under ``path`` without an extension."""
    for root, _, files in os.walk(path):
        for name in files:
            if os.path.splitext(name)[1]:
                # Skip files that already have an extension
                continue
            yield os.path.join(root, name)


def process(path: str, *, dry_run: bool = False, delete_original: bool = False) -> None:
    """Decompress JPEG 2000 encoded DICOM files in ``path``.

    Parameters
    ----------
    path: str
        Root directory to search.
    dry_run: bool, optional
        If ``True`` no files will be written; actions are only logged.
    delete_original: bool, optional
        If ``True`` delete the original compressed file after writing the
        decompressed version.
    """
    for file_path in iter_files(path):
        try:
            ds = pydicom.dcmread(file_path, force=True)
        except Exception as exc:  # pragma: no cover - logging only
            print(f"Skipping {file_path}: {exc}")
            continue

        ts = ds.file_meta.get("TransferSyntaxUID")
        if ts not in JPEG2000_UIDS:
            print(f"Skipping {file_path}: not JPEG 2000 (ts={ts})")
            continue

        out_path = f"{file_path}.dcm"
        if dry_run:
            print(f"Would write {out_path}")
            continue

        try:
            ds.decompress()
            ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
            ds.save_as(out_path)
            if delete_original:
                os.remove(file_path)
            print(f"Wrote {out_path}")
        except Exception as exc:  # pragma: no cover - logging only
            print(f"Failed to process {file_path}: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="Root folder to search")
    parser.add_argument("--dry-run", action="store_true", help="List actions without writing")
    parser.add_argument(
        "--delete-original",
        action="store_true",
        help="Delete the compressed file after successful conversion",
    )
    args = parser.parse_args()
    process(args.path, dry_run=args.dry_run, delete_original=args.delete_original)


if __name__ == "__main__":
    main()
