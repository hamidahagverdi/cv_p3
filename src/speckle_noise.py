from __future__ import annotations

from pathlib import Path
from typing import Dict

import cv2
import numpy as np
from skimage.restoration import denoise_tv_chambolle

from .utils import (
    compute_basic_metrics,
    ensure_dir,
    load_gray_image,
    normalize_to_uint8,
    plot_comparison,
    rank_filters_by_score,
    save_image,
    select_random_images,
    write_json,
    write_text,
)


def lee_filter(image: np.ndarray, size: int = 7) -> np.ndarray:
    """Classical Lee filter for speckle noise."""
    img = image.astype(np.float32)
    local_mean = cv2.blur(img, (size, size))
    local_sq_mean = cv2.blur(img ** 2, (size, size))
    local_var = local_sq_mean - (local_mean ** 2)
    noise_var = np.var(img)
    weights = local_var / (local_var + noise_var + 1e-8)
    filtered = local_mean + weights * (img - local_mean)
    return normalize_to_uint8(filtered)


def log_bilateral_filter(image: np.ndarray) -> np.ndarray:
    img = image.astype(np.float32) / 255.0
    img = np.clip(img, 1e-6, 1.0)
    log_img = np.log(img)
    log_u8 = normalize_to_uint8(log_img)
    filtered = cv2.bilateralFilter(log_u8, 9, 45, 45)
    filtered = filtered.astype(np.float32) / 255.0
    reconstructed = np.exp(filtered)
    return normalize_to_uint8(reconstructed)


def speckle_filters(image: np.ndarray) -> Dict[str, np.ndarray]:
    img = normalize_to_uint8(image)

    gaussian = cv2.GaussianBlur(img, (5, 5), 0)
    median = cv2.medianBlur(img, 5)
    bilateral = cv2.bilateralFilter(img, 9, 55, 55)
    lee = lee_filter(img, size=7)
    tv = denoise_tv_chambolle(img.astype(np.float32) / 255.0, weight=0.08, channel_axis=None)
    tv = normalize_to_uint8(tv)
    log_bilateral = log_bilateral_filter(img)

    return {
        "original": img,
        "gaussian_blur": gaussian,
        "median_filter": median,
        "bilateral_filter": bilateral,
        "lee_filter": lee,
        "tv_chambolle": tv,
        "log_bilateral": log_bilateral,
    }


def run_speckle_pipeline(input_dir: Path, output_dir: Path, max_images: int = 3, seed: int = 42) -> None:
    ensure_dir(output_dir)
    selected = select_random_images(input_dir, max_images=max_images, seed=seed)

    overall_summary = []

    for image_path in selected:
        img = load_gray_image(image_path)
        results = speckle_filters(img)

        metrics = {
            name: compute_basic_metrics(arr)
            for name, arr in results.items()
            if name != "original"
        }
        ranking = rank_filters_by_score(metrics)
        best_name = ranking[0]
        worst_name = ranking[-1]

        item_out = output_dir / image_path.stem
        ensure_dir(item_out)

        for name, arr in results.items():
            save_image(item_out / f"{name}.png", arr)

        plot_comparison(
            title=f"Speckle Noise Removal - {image_path.name}",
            images=results,
            output_path=item_out / "comparison_filters.png",
        )

        result_payload = {
            "image": image_path.name,
            "best_filter": best_name,
            "worst_filter": worst_name,
            "ranking": ranking,
            "metrics": metrics,
        }
        write_json(item_out / "metrics.json", result_payload)

        overall_summary.append(
            f"{image_path.name}: best={best_name}, worst={worst_name}, ranking={', '.join(ranking)}"
        )

    summary_text = (
        "Speckle noise summary\n"
        "=====================\n\n"
        "Interpretation rule:\n"
        "- Better filters reduce multiplicative speckle noise while preserving edges.\n"
        "- Worse filters create blur or leave visible grain.\n\n"
        + "\n".join(overall_summary)
        + "\n\nExpected pattern:\n"
        "- lee_filter or log_bilateral usually works best for speckle.\n"
        "- gaussian_blur is often among the worst because it removes detail together with noise."
    )
    write_text(output_dir / "summary.txt", summary_text)
    print(f"[Speckle] Done. Results saved to: {output_dir}")
