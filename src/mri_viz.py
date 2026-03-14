from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pydicom

from .utils import ensure_dir, normalize_to_uint8, write_json, write_text


def read_dicom_series(input_path: Path) -> Tuple[np.ndarray, List[pydicom.dataset.FileDataset]]:
    if input_path.is_file():
        ds = pydicom.dcmread(str(input_path))
        arr = ds.pixel_array
        if arr.ndim == 2:
            volume = arr[np.newaxis, ...]
        elif arr.ndim == 3:
            volume = arr
        else:
            raise ValueError(f"Unsupported pixel array shape: {arr.shape}")
        return volume.astype(np.float32), [ds]

    if input_path.is_dir():
        dicom_files = sorted([p for p in input_path.rglob("*") if p.is_file() and p.suffix.lower() in {".dcm", ""}])
        datasets = []
        for p in dicom_files:
            try:
                ds = pydicom.dcmread(str(p))
                _ = ds.pixel_array
                datasets.append(ds)
            except Exception:
                continue
        if not datasets:
            raise FileNotFoundError(f"No readable DICOM files found in: {input_path}")

        datasets.sort(key=lambda ds: float(getattr(ds, "InstanceNumber", 0)))
        slices = [ds.pixel_array.astype(np.float32) for ds in datasets]
        volume = np.stack(slices, axis=0)
        return volume, datasets

    raise FileNotFoundError(f"Input path not found: {input_path}")


def apply_rescale_and_window(volume: np.ndarray, dataset: pydicom.dataset.FileDataset) -> np.ndarray:
    slope = float(getattr(dataset, "RescaleSlope", 1.0))
    intercept = float(getattr(dataset, "RescaleIntercept", 0.0))
    vol = volume * slope + intercept

    center = getattr(dataset, "WindowCenter", None)
    width = getattr(dataset, "WindowWidth", None)

    def first_value(v):
        if isinstance(v, pydicom.multival.MultiValue):
            return float(v[0])
        return float(v)

    if center is not None and width is not None:
        center = first_value(center)
        width = max(first_value(width), 1.0)
        low = center - width / 2
        high = center + width / 2
        vol = np.clip(vol, low, high)

    return vol


def describe_dataset(dataset: pydicom.dataset.FileDataset, volume: np.ndarray) -> dict:
    desc = {
        "Modality": str(getattr(dataset, "Modality", "Unknown")),
        "StudyDescription": str(getattr(dataset, "StudyDescription", "Unknown")),
        "SeriesDescription": str(getattr(dataset, "SeriesDescription", "Unknown")),
        "Rows": int(getattr(dataset, "Rows", volume.shape[-2])),
        "Columns": int(getattr(dataset, "Columns", volume.shape[-1])),
        "NumberOfSlicesOrFrames": int(volume.shape[0]),
        "PixelSpacing": str(getattr(dataset, "PixelSpacing", "Unknown")),
        "SliceThickness": str(getattr(dataset, "SliceThickness", "Unknown")),
        "BitsStored": str(getattr(dataset, "BitsStored", "Unknown")),
        "PhotometricInterpretation": str(getattr(dataset, "PhotometricInterpretation", "Unknown")),
        "Manufacturer": str(getattr(dataset, "Manufacturer", "Unknown")),
        "MagneticFieldStrength": str(getattr(dataset, "MagneticFieldStrength", "Unknown")),
    }
    return desc


def save_slice_grid(volume: np.ndarray, output_path: Path, title: str = "MRI layers") -> None:
    ensure_dir(output_path.parent)
    n_slices = volume.shape[0]
    chosen = np.linspace(0, max(0, n_slices - 1), num=min(6, n_slices), dtype=int)

    plt.figure(figsize=(15, 8))
    for i, idx in enumerate(chosen, start=1):
        plt.subplot(2, 3, i)
        plt.imshow(normalize_to_uint8(volume[idx]), cmap="gray")
        plt.title(f"Slice {idx}")
        plt.axis("off")
    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close()


def save_orthogonal_views(volume: np.ndarray, output_path: Path) -> None:
    ensure_dir(output_path.parent)
    z, y, x = volume.shape
    axial = volume[z // 2]
    coronal = volume[:, y // 2, :]
    sagittal = volume[:, :, x // 2]

    plt.figure(figsize=(15, 5))
    views = [("Axial", axial), ("Coronal", coronal), ("Sagittal", sagittal)]
    for i, (name, img) in enumerate(views, start=1):
        plt.subplot(1, 3, i)
        plt.imshow(normalize_to_uint8(img), cmap="gray")
        plt.title(name)
        plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close()


def run_mri_pipeline(input_path: Path, output_dir: Path) -> None:
    ensure_dir(output_dir)
    volume, datasets = read_dicom_series(input_path)
    primary_ds = datasets[0]
    volume = apply_rescale_and_window(volume, primary_ds)

    metadata = describe_dataset(primary_ds, volume)
    write_json(output_dir / "metadata.json", metadata)

    human_readable = "\n".join(f"{k}: {v}" for k, v in metadata.items())
    write_text(output_dir / "metadata.txt", human_readable)

    save_slice_grid(volume, output_dir / "slice_grid.png", title="MRI slice visualization")

    if volume.shape[0] > 1 and volume.shape[1] > 1 and volume.shape[2] > 1:
        save_orthogonal_views(volume, output_dir / "orthogonal_views.png")

    print("[MRI] Metadata:")
    for key, value in metadata.items():
        print(f"  - {key}: {value}")
    print(f"[MRI] Done. Results saved to: {output_dir}")
