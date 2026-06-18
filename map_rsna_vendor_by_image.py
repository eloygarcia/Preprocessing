#!/usr/bin/env python3
"""Map RSNA train images to vendor/model using machine_id from train.csv.

The RSNA DICOM files are anonymized and usually do not include Manufacturer
tags. This script uses machine_id from train.csv and a curated mapping to
associate each image with a vendor.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def default_machine_mapping() -> pd.DataFrame:
    """Return a curated machine_id -> vendor/model mapping.

    Source: repository analysis in vendors/rsna_dicom_analysis.md.
    """
    rows = [
        {
            "machine_id": 49,
            "vendor": "Hologic",
            "model": "Selenia Dimensions",
            "vendor_confidence": "high",
            "mapping_note": "From RSNA analysis: Hologic signature geometry.",
        },
        {
            "machine_id": 48,
            "vendor": "Hologic",
            "model": "Selenia Dimensions",
            "vendor_confidence": "high",
            "mapping_note": "From RSNA analysis: Hologic signature geometry.",
        },
        {
            "machine_id": 170,
            "vendor": "Hologic",
            "model": "Selenia",
            "vendor_confidence": "high",
            "mapping_note": "From RSNA analysis: 70um Hologic profile.",
        },
        {
            "machine_id": 21,
            "vendor": "GE",
            "model": "Senographe Essential/DS",
            "vendor_confidence": "probable",
            "mapping_note": "Probable GE; Manufacturer tag stripped in DICOM.",
        },
        {
            "machine_id": 93,
            "vendor": "GE",
            "model": "Senographe DS",
            "vendor_confidence": "probable",
            "mapping_note": "Probable GE; Manufacturer tag stripped in DICOM.",
        },
        {
            "machine_id": 216,
            "vendor": "GE",
            "model": "Senographe DS",
            "vendor_confidence": "probable",
            "mapping_note": "Probable GE; Manufacturer tag stripped in DICOM.",
        },
        {
            "machine_id": 190,
            "vendor": "GE",
            "model": "Senographe DS",
            "vendor_confidence": "probable",
            "mapping_note": "Probable GE; Manufacturer tag stripped in DICOM.",
        },
        {
            "machine_id": 197,
            "vendor": "GE",
            "model": "Unknown GE model",
            "vendor_confidence": "probable",
            "mapping_note": "Probable GE; mixed matrix profiles.",
        },
        {
            "machine_id": 210,
            "vendor": "Fujifilm",
            "model": "AMULET Innovality",
            "vendor_confidence": "high",
            "mapping_note": "From RSNA analysis: 50um Fujifilm profile.",
        },
        {
            "machine_id": 29,
            "vendor": "Unknown",
            "model": "Unknown",
            "vendor_confidence": "low",
            "mapping_note": "Large-format detector; likely non-Hologic, unresolved.",
        },
    ]
    return pd.DataFrame(rows)


def load_mapping(mapping_csv: Path | None) -> pd.DataFrame:
    if mapping_csv is None:
        return default_machine_mapping()

    mapping_df = pd.read_csv(mapping_csv)
    required_cols = {"machine_id", "vendor"}
    missing_cols = required_cols - set(mapping_df.columns)
    if missing_cols:
        raise ValueError(
            f"Mapping file is missing required columns: {sorted(missing_cols)}"
        )

    if "model" not in mapping_df.columns:
        mapping_df["model"] = "Unknown"
    if "vendor_confidence" not in mapping_df.columns:
        mapping_df["vendor_confidence"] = "custom"
    if "mapping_note" not in mapping_df.columns:
        mapping_df["mapping_note"] = "custom mapping"

    return mapping_df


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Map RSNA images to vendor/model using machine_id."
    )
    parser.add_argument(
        "--train-csv",
        type=Path,
        required=True,
        help="Path to RSNA train.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output CSV path",
    )
    parser.add_argument(
        "--dicom-root",
        type=Path,
        default=None,
        help="Optional root directory of train_images for path/existence columns.",
    )
    parser.add_argument(
        "--mapping-csv",
        type=Path,
        default=None,
        help=(
            "Optional CSV with machine_id,vendor and optional model,"
            "vendor_confidence,mapping_note."
        ),
    )
    parser.add_argument(
        "--patient-ids",
        type=int,
        nargs="*",
        default=None,
        help="Optional patient_id subset for quick tests.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any machine_id remains unmapped.",
    )
    parser.add_argument(
        "--export-mapping-csv",
        type=Path,
        default=None,
        help="Optional path to export the effective machine_id mapping CSV.",
    )
    parser.add_argument(
        "--summary-machine-csv",
        type=Path,
        default=None,
        help="Optional path to save counts by machine_id/vendor/model.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    train_df = pd.read_csv(args.train_csv)
    if args.patient_ids:
        train_df = train_df[train_df["patient_id"].isin(args.patient_ids)].copy()

    mapping_df = load_mapping(args.mapping_csv)

    if args.export_mapping_csv is not None:
        export_df = mapping_df.sort_values("machine_id").drop_duplicates(
            subset=["machine_id"], keep="first"
        )
        args.export_mapping_csv.parent.mkdir(parents=True, exist_ok=True)
        export_df.to_csv(args.export_mapping_csv, index=False)

    merged = train_df.merge(mapping_df, on="machine_id", how="left")
    merged["vendor"] = merged["vendor"].fillna("Unknown")
    merged["model"] = merged["model"].fillna("Unknown")
    merged["vendor_confidence"] = merged["vendor_confidence"].fillna("unmapped")
    merged["mapping_note"] = merged["mapping_note"].fillna("machine_id not in mapping")

    if args.dicom_root is not None:
        merged["dicom_path"] = (
            str(args.dicom_root)
            + "/"
            + merged["patient_id"].astype(str)
            + "/"
            + merged["image_id"].astype(str)
            + ".dcm"
        )
        merged["dicom_exists"] = merged["dicom_path"].map(lambda p: Path(p).exists())

    unmapped_count = int((merged["vendor"] == "Unknown").sum())
    if args.strict and unmapped_count > 0:
        unknown_ids = sorted(
            merged.loc[merged["vendor"] == "Unknown", "machine_id"].dropna().unique()
        )
        raise SystemExit(
            "Strict mode failed: "
            f"{unmapped_count} rows unresolved. machine_id values: {unknown_ids}"
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.output, index=False)

    machine_summary = (
        merged.groupby(["machine_id", "vendor", "model", "vendor_confidence"], dropna=False)
        .size()
        .reset_index(name="image_count")
        .sort_values(["image_count", "machine_id"], ascending=[False, True])
    )

    summary_path = args.summary_machine_csv
    if summary_path is None:
        summary_path = args.output.with_name(f"{args.output.stem}_machine_summary.csv")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    machine_summary.to_csv(summary_path, index=False)

    vendor_counts = merged["vendor"].value_counts(dropna=False)
    print(f"Saved: {args.output}")
    print(f"Machine summary: {summary_path}")
    if args.export_mapping_csv is not None:
        print(f"Mapping export: {args.export_mapping_csv}")
    print(f"Rows: {len(merged)}")
    print("Vendor counts:")
    for vendor, count in vendor_counts.items():
        pct = (count / len(merged)) * 100 if len(merged) else 0.0
        print(f"  - {vendor}: {count} ({pct:.2f}%)")

    if args.dicom_root is not None and "dicom_exists" in merged.columns:
        exists = int(merged["dicom_exists"].sum())
        print(f"DICOM files found: {exists}/{len(merged)}")


if __name__ == "__main__":
    main()
