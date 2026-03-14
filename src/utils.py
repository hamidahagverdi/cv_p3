from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, Iterable, List

import cv2
import matplotlib.pyplot as plt
import numpy as np
from skimage.restoration import estimate_sigma


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def list_image_files(folder: Path) -> List[Path]:
    if not folder.exists():
        raise FileNotFoundError(f"Input folder does not exist: {folder}")
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
    if not files:
        raise FileNotFoundError(f"No supported image files found in: {folder}")
    return sorted(files)


def select_random_images(folder: Path, max_images: int = 3, seed: int = 42) -> List[Path]:
    files = list_image_files(folder)
    rng = random.Random(seed)
    if len(files) <= max_images:
        return files
    return sorted(rng.sample(files, max_images))


def load_gray_image(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    return image


def normalize_to_uint8(image: np.ndarray) -> np.ndarray:
    image = np.asarray(image, dtype=np.float32)
    image = image - image.min()
    max_val = image.max()
    if max_val > 0:
        image = image / max_val
    return (image * 255).clip(0, 255).astype(np.uint8)


def save_image(path: Path, image: np.ndarray) -> None:
    ensure_dir(path.parent)
    cv2.imwrite(str(path), normalize_to_uint8(image))


def plot_comparison(
    title: str,
    images: Dict[str, np.ndarray],
    output_path: Path,
    cmap: str = "gray",
    cols: int = 3,
) -> None:
    ensure_dir(output_path.parent)
    names = list(images.keys())
    n = len(names)
    rows = int(np.ceil(n / cols))
    plt.figure(figsize=(5 * cols, 4 * rows))
    for i, name in enumerate(names, start=1):
        plt.subplot(rows, cols, i)
        plt.imshow(images[name], cmap=cmap)
        plt.title(name)
        plt.axis("off")
    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close()


def compute_basic_metrics(image: np.ndarray) -> Dict[str, float]:
    img = normalize_to_uint8(image)
    lap_var = float(cv2.Laplacian(img, cv2.CV_64F).var())
    edges = cv2.Canny(img, 50, 150)
    edge_density = float(edges.mean() / 255.0)
    sigma = float(estimate_sigma(img.astype(np.float32) / 255.0, channel_axis=None, average_sigmas=True))
    mean_intensity = float(img.mean())
    return {
        "laplacian_variance": round(lap_var, 4),
        "edge_density": round(edge_density, 6),
        "estimated_noise_sigma": round(sigma, 6),
        "mean_intensity": round(mean_intensity, 4),
    }


def rank_filters_by_score(metrics: Dict[str, Dict[str, float]]) -> List[str]:
    """
    Simple unsupervised ranking:
    - reward edge preservation (laplacian variance, edge density)
    - penalize remaining noise
    """
    names = list(metrics.keys())
    lap = np.array([metrics[n]["laplacian_variance"] for n in names], dtype=float)
    edge = np.array([metrics[n]["edge_density"] for n in names], dtype=float)
    noise = np.array([metrics[n]["estimated_noise_sigma"] for n in names], dtype=float)

    def norm(x: np.ndarray) -> np.ndarray:
        if np.allclose(x.max(), x.min()):
            return np.ones_like(x)
        return (x - x.min()) / (x.max() - x.min())

    score = 0.45 * norm(lap) + 0.35 * norm(edge) - 0.20 * norm(noise)
    ranked = sorted(zip(names, score), key=lambda t: t[1], reverse=True)
    return [name for name, _ in ranked]


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")
