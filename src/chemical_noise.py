from __future__ import annotations

from pathlib import Path
from typing import Dict

import cv2
import numpy as np

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


def reconstruct_shapes(image: np.ndarray) -> np.ndarray:
    """Threshold + morphology to make letters/lines cleaner."""
    img = normalize_to_uint8(image)
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # If foreground seems bright but occupies too little area, invert.
    foreground_ratio = (binary == 255).mean()
    if foreground_ratio < 0.15 or foreground_ratio > 0.85:
        binary = 255 - binary

    kernel_small = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    kernel_wide = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_small)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel_wide)
    return cleaned


def chemical_filters(image: np.ndarray) -> Dict[str, np.ndarray]:
    img = normalize_to_uint8(image)

    mean = cv2.blur(img, (5, 5))
    gaussian = cv2.GaussianBlur(img, (5, 5), 0)
    median = cv2.medianBlur(img, 5)
    bilateral = cv2.bilateralFilter(img, 9, 50, 50)
    nlm = cv2.fastNlMeansDenoising(img, None, h=11, templateWindowSize=7, searchWindowSize=21)

    return {
        "original": img,
        "mean_blur": mean,
        "gaussian_blur": gaussian,
        "median_filter": median,
        "bilateral_filter": bilateral,
        "nl_means": nlm,
    }


def run_chemical_pipeline(input_dir: Path, output_dir: Path, max_images: int = 3, seed: int = 42) -> None:
    ensure_dir(output_dir)
    selected = select_random_images(input_dir, max_images=max_images, seed=seed)

    overall_summary = []

    for image_path in selected:
        img = load_gray_image(image_path)
        results = chemical_filters(img)

        metrics = {
            name: compute_basic_metrics(arr)
            for name, arr in results.items()
            if name != "original"
        }
        ranking = rank_filters_by_score(metrics)
        best_name = ranking[0]
        worst_name = ranking[-1]

        reconstructed = {}
        for name, arr in results.items():
            if name == "original":
                continue
            reconstructed[f"{name}_reconstructed"] = reconstruct_shapes(arr)

        item_out = output_dir / image_path.stem
        ensure_dir(item_out)

        for name, arr in results.items():
            save_image(item_out / f"{name}.png", arr)

        for name, arr in reconstructed.items():
            save_image(item_out / f"{name}.png", arr)

        plot_comparison(
            title=f"Chemical Noise Removal - {image_path.name}",
            images=results,
            output_path=item_out / "comparison_filters.png",
        )
        plot_comparison(
            title=f"Shape Reconstruction - {image_path.name}",
            images=reconstructed,
            output_path=item_out / "comparison_reconstruction.png",
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
        "Chemical noise summary\n"
        "======================\n\n"
        "Interpretation rule:\n"
        "- Better filters remove noise while preserving the lines/letters.\n"
        "- Worse filters over-smooth the image or leave too much noise.\n\n"
        + "\n".join(overall_summary)
        + "\n\nExpected pattern:\n"
        "- median_filter or nl_means usually performs best for this task.\n"
        "- mean_blur often performs worst because it destroys fine structures."
    )
    write_text(output_dir / "summary.txt", summary_text)
    print(f"[Chemical] Done. Results saved to: {output_dir}")
