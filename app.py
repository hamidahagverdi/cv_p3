#!/usr/bin/env python3
"""
Image Processing Assignment Runner

Usage examples:
    python app.py chemical --input data/original/chemical --output outputs/chemical
    python app.py speckle --input data/original/speckle --output outputs/speckle
    python app.py mri --input data/mri/your_file.dcm --output outputs/mri
    python app.py all --chemical data/original/chemical --speckle data/original/speckle --mri data/mri/your_file.dcm
"""
from __future__ import annotations

import argparse
from pathlib import Path

from src.chemical_noise import run_chemical_pipeline
from src.speckle_noise import run_speckle_pipeline
from src.mri_viz import run_mri_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the assignment pipelines for chemical noise, speckle noise, and MRI visualization."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    chemical = subparsers.add_parser("chemical", help="Run noise removal and reconstruction on chemical images.")
    chemical.add_argument("--input", type=Path, required=True, help="Folder with chemical images.")
    chemical.add_argument("--output", type=Path, default=Path("outputs/chemical"), help="Output folder.")
    chemical.add_argument("--max-images", type=int, default=3, help="How many random images to process.")
    chemical.add_argument("--seed", type=int, default=42, help="Random seed for reproducible selection.")

    speckle = subparsers.add_parser("speckle", help="Run speckle removal on images.")
    speckle.add_argument("--input", type=Path, required=True, help="Folder with speckle images.")
    speckle.add_argument("--output", type=Path, default=Path("outputs/speckle"), help="Output folder.")
    speckle.add_argument("--max-images", type=int, default=3, help="How many random images to process.")
    speckle.add_argument("--seed", type=int, default=42, help="Random seed for reproducible selection.")

    mri = subparsers.add_parser("mri", help="Describe and visualize a DICOM MRI file or folder.")
    mri.add_argument("--input", type=Path, required=True, help="A .dcm file or a folder with DICOM files.")
    mri.add_argument("--output", type=Path, default=Path("outputs/mri"), help="Output folder.")

    all_tasks = subparsers.add_parser("all", help="Run all three tasks.")
    all_tasks.add_argument("--chemical", type=Path, required=True, help="Folder with chemical images.")
    all_tasks.add_argument("--speckle", type=Path, required=True, help="Folder with speckle images.")
    all_tasks.add_argument("--mri", type=Path, required=True, help="DICOM file or folder.")
    all_tasks.add_argument("--output", type=Path, default=Path("outputs"), help="Base output folder.")
    all_tasks.add_argument("--max-images", type=int, default=3, help="How many random images to process per image task.")
    all_tasks.add_argument("--seed", type=int, default=42, help="Random seed for reproducible selection.")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "chemical":
        run_chemical_pipeline(args.input, args.output, max_images=args.max_images, seed=args.seed)

    elif args.command == "speckle":
        run_speckle_pipeline(args.input, args.output, max_images=args.max_images, seed=args.seed)

    elif args.command == "mri":
        run_mri_pipeline(args.input, args.output)

    elif args.command == "all":
        run_chemical_pipeline(args.chemical, args.output / "chemical", max_images=args.max_images, seed=args.seed)
        run_speckle_pipeline(args.speckle, args.output / "speckle", max_images=args.max_images, seed=args.seed)
        run_mri_pipeline(args.mri, args.output / "mri")


if __name__ == "__main__":
    main()
