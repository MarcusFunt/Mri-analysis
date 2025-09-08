from pathlib import Path
from monai.transforms import Compose, LoadImaged, SaveImaged
from monai.data import Dataset

def main():
    raw_dir = Path("data/raw")
    nifti_dir = Path("data/nifti")
    nifti_dir.mkdir(parents=True, exist_ok=True)

    items = []
    for p in sorted(raw_dir.iterdir()):
        if p.is_dir():
            dicom_file = p / p.name
            if dicom_file.exists():
                items.append({"image": str(dicom_file)})

    transforms = Compose([
        LoadImaged(keys="image"),
        SaveImaged(keys="image", output_dir=str(nifti_dir), output_ext=".nii.gz", resample=False)
    ])

    dataset = Dataset(data=items, transform=transforms)
    for _ in dataset:
        pass
    print(f"Converted {len(items)} files to {nifti_dir}")

if __name__ == "__main__":
    main()
