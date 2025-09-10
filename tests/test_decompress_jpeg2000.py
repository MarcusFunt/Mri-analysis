import os
from unittest import mock

import pytest
from pydicom.uid import JPEG2000

import decompress_jpeg2000 as dj


def test_iter_files_yields_only_extensionless(tmp_path):
    # Create files with and without extensions in nested directories
    (tmp_path / "a").write_text("")
    (tmp_path / "b.txt").write_text("")
    sub = tmp_path / "sub"; sub.mkdir()
    (sub / "c").write_text("")
    (sub / "d.bin").write_text("")

    found = set(dj.iter_files(str(tmp_path)))
    expected = {str(tmp_path / "a"), str(sub / "c")}
    assert found == expected


@mock.patch("decompress_jpeg2000.pydicom.dcmread")
def test_process_decompresses_and_writes(mock_dcmread, tmp_path):
    src = tmp_path / "file"
    src.write_text("data")

    ds = mock.Mock()
    file_meta = mock.Mock()
    file_meta.get.return_value = JPEG2000
    file_meta.TransferSyntaxUID = JPEG2000
    ds.file_meta = file_meta
    mock_dcmread.return_value = ds

    dj.process(str(tmp_path))

    mock_dcmread.assert_called_once_with(str(src), force=True)
    ds.decompress.assert_called_once()
    ds.save_as.assert_called_once_with(str(src) + ".dcm")


@mock.patch("decompress_jpeg2000.pydicom.dcmread")
def test_process_dry_run_skips_write(mock_dcmread, tmp_path):
    src = tmp_path / "file"
    src.write_text("data")

    ds = mock.Mock()
    file_meta = mock.Mock()
    file_meta.get.return_value = JPEG2000
    file_meta.TransferSyntaxUID = JPEG2000
    ds.file_meta = file_meta
    mock_dcmread.return_value = ds

    dj.process(str(tmp_path), dry_run=True)

    ds.decompress.assert_not_called()
    ds.save_as.assert_not_called()


@mock.patch("decompress_jpeg2000.os.remove")
@mock.patch("decompress_jpeg2000.pydicom.dcmread")
def test_process_delete_original(mock_dcmread, mock_remove, tmp_path):
    src = tmp_path / "file"
    src.write_text("data")

    ds = mock.Mock()
    file_meta = mock.Mock()
    file_meta.get.return_value = JPEG2000
    file_meta.TransferSyntaxUID = JPEG2000
    ds.file_meta = file_meta
    mock_dcmread.return_value = ds

    dj.process(str(tmp_path), delete_original=True)

    mock_remove.assert_called_once_with(str(src))
