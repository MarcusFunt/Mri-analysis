from pathlib import Path
import importlib
import sys


def test_main_creates_nifti_and_counts(tmp_path, monkeypatch, capsys):
    # Prepare dummy MONAI modules before importing script
    class DummyDataset:
        def __init__(self, data, transform):
            self.data = data
            self.transform = transform

        def __iter__(self):
            for item in self.data:
                self.transform(item)
                yield item

    transforms_module = type("T", (), {
        "Compose": lambda transforms: lambda x: x,
        "LoadImaged": lambda keys: lambda x: x,
        "SaveImaged": lambda keys, output_dir, output_ext, resample: lambda x: x,
    })
    data_module = type("D", (), {"Dataset": DummyDataset})

    monkeypatch.setitem(sys.modules, "monai.transforms", transforms_module)
    monkeypatch.setitem(sys.modules, "monai.data", data_module)

    pmd = importlib.import_module("prepare_monai_dataset")

    # Run inside a temporary directory
    monkeypatch.chdir(tmp_path)

    # Create raw DICOM-like structure
    raw_dir = Path("data/raw")
    (raw_dir / "case1").mkdir(parents=True)
    (raw_dir / "case1" / "case1").touch()
    (raw_dir / "case2").mkdir()
    (raw_dir / "case2" / "case2").touch()

    pmd.main()

    out = capsys.readouterr().out
    assert "Converted 2 files" in out
    assert Path("data/nifti").exists()
