"""
Este módulo proporciona funciones para buscar archivos DICOM recursivamente en un dataset
y exportar sus tags a un CSV.

WARNING: Utilicese con cuidado. Los datasets de DICOM pueden ser muy grandes y contener muchos archivos,
lo que puede llevar a un uso intensivo de memoria y tiempo de procesamiento.
Este módulo es particularmente útil para datasets donde los metadatos de windowing DICOM
no son confiables o están ausentes, y se requiere una extracción precisa de los tags DICOM para 
análisis o procesamiento adicional.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import json
import os
from pathlib import Path
import tempfile

from pydicom.misc import is_dicom
from tqdm import tqdm

from image.preprocessing import DEFAULT_DICOM_TAG_SUMMARY_FIELDS, collect_dicom_tag_record
from utils.extract_dicoms import find_dicom_files

DEFAULT_DICOM_SUFFIXES = {".dcm", ".dicom"}


def _parse_workers(value: str) -> int | str:
    if value.lower() == "auto":
        return "auto"
    workers = int(value)
    if workers < 1:
        raise argparse.ArgumentTypeError("workers must be at least 1 or 'auto'")
    return workers


def _resolve_workers(workers: int | str) -> int:
    if workers == "auto":
        return max(1, min(8, os.cpu_count() or 1))
    return workers


def _iter_leaf_directory_files(root: Path):
    for current_root, dirnames, filenames in os.walk(root):
        if dirnames:
            continue

        leaf_dir = Path(current_root)
        yield leaf_dir, sorted(leaf_dir / file_name for file_name in filenames)



"""
def find_dicom_files(
    dataset_root: str | Path,
    include_extensionless: bool = False,
    extensionless_only: bool = False,
) -> list[Path]:
    
    root = Path(dataset_root).expanduser()
    if not root.exists():
        raise FileNotFoundError(f"Dataset directory not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Dataset root must be a directory: {root}")

    if extensionless_only and not include_extensionless:
        include_extensionless = True

    dicom_paths: list[Path] = []

    with tqdm(desc="Discovering DICOM files", unit="leaf_dir") as discovery_bar:
        for leaf_dir, leaf_paths in _iter_leaf_directory_files(root):
            discovery_bar.update(1)
            discovery_bar.set_postfix_str(leaf_dir.name or str(leaf_dir))

            extension_candidates = [path for path in leaf_paths if path.suffix.lower() in DEFAULT_DICOM_SUFFIXES]
            extension_dicom_paths: list[Path] = []

            if not extensionless_only:
                extension_dicom_paths = [path for path in extension_candidates if is_dicom(path)]
                dicom_paths.extend(extension_dicom_paths)

            should_check_extensionless = include_extensionless and not extension_dicom_paths
            if extensionless_only:
                should_check_extensionless = True

            if should_check_extensionless:
                extensionless_candidates = [path for path in leaf_paths if path.suffix == ""]
                dicom_paths.extend(path for path in extensionless_candidates if is_dicom(path))

    dicom_paths = sorted(set(dicom_paths))

    if not dicom_paths:
        raise FileNotFoundError(f"No DICOM files were found in: {root}")

    return dicom_paths
"""

def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Busca archivos DICOM recursivamente desde un dataset y exporta sus tags a un CSV.",
    )
    parser.add_argument(
        "dataset_root",
        type=Path,
        help="Directorio raíz del dataset que se recorrerá recursivamente.",
    )
    parser.add_argument(
        "output_csv",
        type=Path,
        help="Ruta del CSV de salida.",
    )
    parser.add_argument(
        "--include-private-tags",
        action="store_true",
        help="Incluye tags privados de DICOM en el CSV.",
    )
    parser.add_argument(
        "--exclude-file-meta",
        action="store_true",
        help="Excluye los tags de file meta del CSV.",
    )
    parser.add_argument(
        "--exclude-pixel-summary",
        action="store_true",
        help="Excluye columnas derivadas del array de pixeles de NumPy.",
    )
    parser.add_argument(
        "--delimiter",
        default=";",
        help="Separador del CSV. Por defecto ';'.",
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
        "--workers",
        type=_parse_workers,
        default=1,
        help="Numero de hilos para procesar archivos en paralelo o 'auto'. Por defecto 1.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Numero de archivos a procesar por lote antes de volcar resultados a disco. Por defecto 500.",
    )

    return parser


def _collect_record(
    index: int,
    image_path: Path,
    include_pixel_summary: bool,
    include_file_meta: bool,
    include_private_tags: bool,
) -> tuple[int, str, dict[str, str]]:
    record = collect_dicom_tag_record(
        image_path=image_path,
        include_pixel_summary=include_pixel_summary,
        include_file_meta=include_file_meta,
        include_private_tags=include_private_tags,
    )
    return index, image_path.name, record


def export_dataset_dicom_tags(
    image_paths: list[Path],
    output_path: str | Path,
    include_pixel_summary: bool = True,
    include_file_meta: bool = True,
    include_private_tags: bool = False,
    delimiter: str = ";",
    workers: int | str = 1,
    batch_size: int = 500,
) -> Path:
    
    workers = _resolve_workers(workers)

    if workers < 1:
        raise ValueError("workers must be at least 1")
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")

    progress_bar = tqdm(image_paths, desc="Extracting DICOM tags", unit="file")

    destination = Path(output_path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)

    ordered_fieldnames: list[str] = []
    discovered_fieldnames: set[str] = set()

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".jsonl") as temp_file:
        temp_path = Path(temp_file.name)

        for batch_start in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[batch_start:batch_start + batch_size]
            records_by_index: dict[int, dict[str, str]] = {}

            if workers == 1:
                for offset, image_path in enumerate(batch_paths):
                    absolute_index = batch_start + offset
                    progress_bar.set_postfix_str(image_path.name)
                    tqdm.write(f"Reading: {image_path.name}")
                    records_by_index[absolute_index] = collect_dicom_tag_record(
                        image_path=image_path,
                        include_pixel_summary=include_pixel_summary,
                        include_file_meta=include_file_meta,
                        include_private_tags=include_private_tags,
                    )
                    progress_bar.update(1)
            else:
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    futures = {
                        executor.submit(
                            _collect_record,
                            batch_start + offset,
                            image_path,
                            include_pixel_summary,
                            include_file_meta,
                            include_private_tags,
                        ): image_path
                        for offset, image_path in enumerate(batch_paths)
                    }

                    for future in as_completed(futures):
                        index, image_name, record = future.result()
                        progress_bar.update(1)
                        progress_bar.set_postfix_str(image_name)
                        tqdm.write(f"Reading: {image_name}")
                        records_by_index[index] = record

            for index in sorted(records_by_index):
                record = records_by_index[index]
                for key in record:
                    if key not in discovered_fieldnames:
                        discovered_fieldnames.add(key)
                        if key not in DEFAULT_DICOM_TAG_SUMMARY_FIELDS:
                            ordered_fieldnames.append(key)

                temp_file.write(json.dumps(record, ensure_ascii=True) + "\n")

    progress_bar.close()

    summary_fieldnames = [field for field in DEFAULT_DICOM_TAG_SUMMARY_FIELDS if field in discovered_fieldnames]
    dynamic_fieldnames = sorted(ordered_fieldnames)
    fieldnames = summary_fieldnames + dynamic_fieldnames

    with destination.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()

        with temp_path.open("r", encoding="utf-8") as temp_file:
            for line in temp_file:
                record = json.loads(line)
                writer.writerow({field: record.get(field, "") for field in fieldnames})

    temp_path.unlink(missing_ok=True)

    return destination


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    dicom_paths = find_dicom_files(
        args.dataset_root,
        include_extensionless=args.include_extensionless,
        extensionless_only=args.extensionless_only,
    )
    output_path = export_dataset_dicom_tags(
        image_paths=dicom_paths,
        output_path=args.output_csv,
        include_pixel_summary=not args.exclude_pixel_summary,
        include_file_meta=not args.exclude_file_meta,
        include_private_tags=args.include_private_tags,
        delimiter=args.delimiter,
        workers=args.workers,
        batch_size=args.batch_size,
    )

    print(f"DICOM files found: {len(dicom_paths)}")
    print(f"CSV written to: {output_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())