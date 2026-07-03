from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from io.extract_dicoms import find_dicom_files
from image.preprocessing import convert_dicom_to_uint8_png, get_dicom_png_output_path

def _parse_workers(value: str) -> int | str:
    if value.lower() == "auto":
        return "auto"
    workers = int(value)
    if workers < 1:
        raise argparse.ArgumentTypeError("workers must be at least 1 or 'auto'")
    return workers

def _resolve_workers(workers: int | str) -> int:
    if workers == "auto":
        import os
        return max(1, min(8, os.cpu_count() or 1))
    return workers

def export_dataset_dicom_pngs(
    dataset_root: str | Path,
    output_root: str | Path,
    include_extensionless: bool = False,
    extensionless_only: bool = False,
    use_windowing: bool = False,
    workers: int | str = 1,
) -> list[Path]:
    dicom_paths = find_dicom_files(
        dataset_root,
        include_extensionless=include_extensionless,
        extensionless_only=extensionless_only,
    )
    resolved_workers = _resolve_workers(workers)

    if resolved_workers < 1:
        raise ValueError("workers must be at least 1")

    saved_paths: list[Path] = []

    with tqdm(total=len(dicom_paths), desc="Exporting PNG files", unit="file") as progress_bar:
        if resolved_workers == 1:
            for dicom_path in dicom_paths:
                output_path = get_dicom_png_output_path(dicom_path, dataset_root=dataset_root, output_root=output_root)
                saved_paths.append(
                    convert_dicom_to_uint8_png(
                        dicom_path,
                        output_path,
                        use_windowing=use_windowing,
                    )
                )
                progress_bar.update(1)
                progress_bar.set_postfix_str(dicom_path.name)
        else:
            with ThreadPoolExecutor(max_workers=resolved_workers) as executor:
                futures = {
                    executor.submit(
                        convert_dicom_to_uint8_png,
                        dicom_path,
                        get_dicom_png_output_path(dicom_path, dataset_root=dataset_root, output_root=output_root),
                        use_windowing,
                    ): index
                    for index, dicom_path in enumerate(dicom_paths)
                }
                saved_by_index: dict[int, Path] = {}

                for future in as_completed(futures):
                    index = futures[future]
                    saved_path = future.result()
                    saved_by_index[index] = saved_path
                    progress_bar.update(1)
                    progress_bar.set_postfix_str(saved_path.name)

                for index in range(len(dicom_paths)):
                    saved_paths.append(saved_by_index[index])

    return saved_paths

def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Encuentra archivos DICOM en un dataset y exporta PNGs de 8 bits manteniendo la estructura relativa.",
    )
    parser.add_argument(
        "dataset_root",
        type=Path,
        help="Directorio raiz del dataset DICOM de entrada.",
    )
    parser.add_argument(
        "output_root",
        type=Path,
        help="Directorio raiz de salida donde se replicara la estructura del dataset en PNG.",
    )
    parser.add_argument(
        "--include-extensionless",
        action="store_true",
        help="Busca tambien archivos DICOM sin extension.",
    )
    parser.add_argument(
        "--extensionless-only",
        action="store_true",
        help="Busca solo archivos DICOM sin extension.",
    )
    parser.add_argument(
        "--use-windowing",
        action="store_true",
        help="Aplica windowing antes de convertir a 8 bits en lugar de una normalizacion min-max.",
    )
    parser.add_argument(
        "--workers",
        type=_parse_workers,
        default=1,
        help="Numero de hilos para exportacion en paralelo o 'auto'. Por defecto 1.",
    )

    return parser

def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    saved_paths = export_dataset_dicom_pngs(
        dataset_root=args.dataset_root,
        output_root=args.output_root,
        include_extensionless=args.include_extensionless,
        extensionless_only=args.extensionless_only,
        use_windowing=args.use_windowing,
        workers=args.workers,
    )

    print(f"DICOM files converted: {len(saved_paths)}")
    print(f"PNG dataset root: {Path(args.output_root).expanduser().resolve()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())