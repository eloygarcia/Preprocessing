from pathlib import Path
import argparse
import csv

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pydicom


DEFAULT_INBREAST_IMAGES_DIR = Path("~/Escritorio/Datasets/InBreast/Images").expanduser()
DEFAULT_RASTER_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")


def list_dicom_images(images_dir: str | Path = DEFAULT_INBREAST_IMAGES_DIR) -> list[Path]:
    images_path = Path(images_dir).expanduser()
    if not images_path.exists():
        raise FileNotFoundError(f"Images directory not found: {images_path}")

    dicom_paths = sorted(images_path.glob("*.dcm"))
    if not dicom_paths:
        raise FileNotFoundError(f"No DICOM images were found in: {images_path}")

    return dicom_paths


def load_dicom_image(image_path: str | Path) -> np.ndarray:
    dicom_path = Path(image_path).expanduser()
    if not dicom_path.exists():
        raise FileNotFoundError(f"Image not found: {dicom_path}")

    dataset = pydicom.dcmread(dicom_path)
    image = dataset.pixel_array.astype(np.float32)

    if getattr(dataset, "PhotometricInterpretation", "") == "MONOCHROME1":
        image = image.max() - image

    image -= image.min()
    max_value = image.max()
    if max_value > 0:
        image /= max_value

    return image


def show_dicom_image(
    image_path: str | Path | None = None,
    image_index: int = 0,
    images_dir: str | Path = DEFAULT_INBREAST_IMAGES_DIR,
    figsize: tuple[int, int] = (8, 8),
    cmap: str = "gray",
):
    dicom_paths = list_dicom_images(images_dir)

    if image_path is None:
        try:
            selected_path = dicom_paths[image_index]
        except IndexError as error:
            raise IndexError(
                f"image_index {image_index} is out of range for {len(dicom_paths)} images"
            ) from error
    else:
        selected_path = Path(image_path).expanduser()

    image = load_dicom_image(selected_path)

    figure, axis = plt.subplots(figsize=figsize)
    axis.imshow(image, cmap=cmap)
    axis.set_title(selected_path.name)
    axis.axis("off")
    figure.tight_layout()

    return figure, axis, image


def _normalize_to_unit_interval(image: np.ndarray) -> np.ndarray:
    normalized = np.asarray(image, dtype=np.float32)
    normalized -= normalized.min()
    max_value = normalized.max()
    if max_value > 0:
        normalized /= max_value
    return normalized


def load_image_for_overlay(image_path: str | Path) -> np.ndarray:
    path = Path(image_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    if path.suffix.lower() == ".dcm":
        return load_dicom_image(path)

    image = Image.open(path).convert("L")
    return _normalize_to_unit_interval(np.array(image))


def load_mask_for_overlay(mask_path: str | Path, threshold: float = 0.0) -> np.ndarray:
    path = Path(mask_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Mask not found: {path}")

    if path.suffix.lower() == ".dcm":
        mask_image = load_dicom_image(path)
        return mask_image > threshold

    mask = np.array(Image.open(path))
    if mask.ndim == 3:
        mask = mask[..., 0]

    return mask > threshold


def list_dataset_images_for_overlay(
    images_dir: str | Path,
    recursive: bool = True,
    image_extensions: tuple[str, ...] = (".dcm",) + DEFAULT_RASTER_EXTENSIONS,
) -> list[Path]:
    base_dir = Path(images_dir).expanduser()
    if not base_dir.exists():
        raise FileNotFoundError(f"Images directory not found: {base_dir}")

    normalized_extensions = {extension.lower() for extension in image_extensions}
    pattern = "**/*" if recursive else "*"
    image_paths = sorted(
        path
        for path in base_dir.glob(pattern)
        if path.is_file() and path.suffix.lower() in normalized_extensions
    )

    if not image_paths:
        raise FileNotFoundError(f"No supported image files were found in: {base_dir}")

    return image_paths


def _build_mask_path(
    image_path: Path,
    masks_dir: str | Path,
    mask_suffix: str = "",
    mask_extension: str = ".png",
) -> Path:
    extension = mask_extension if mask_extension.startswith(".") else f".{mask_extension}"
    return Path(masks_dir).expanduser() / f"{image_path.stem}{mask_suffix}{extension}"


def _resolve_overlay_path(path_value: str, base_dir: str | Path | None = None) -> Path:
    raw_path = Path(path_value).expanduser()
    if raw_path.is_absolute() or base_dir is None:
        return raw_path

    return Path(base_dir).expanduser() / raw_path


def load_overlay_pairs_from_csv(
    csv_path: str | Path,
    image_column: str = "image_path",
    mask_column: str = "mask_path",
    delimiter: str = ",",
    images_base_dir: str | Path | None = None,
    masks_base_dir: str | Path | None = None,
    mask_extension: str = ".png",
    start_index: int = 0,
    max_images: int | None = None,
) -> tuple[list[tuple[Path, Path]], list[tuple[Path, Path]]]:
    path = Path(csv_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    with path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header")

        if image_column not in reader.fieldnames or mask_column not in reader.fieldnames:
            raise ValueError(
                "CSV columns not found. "
                f"Available columns: {reader.fieldnames}. "
                f"Expected: image='{image_column}', mask='{mask_column}'"
            )

        csv_pairs: list[tuple[Path, Path]] = []
        for row in reader:
            image_value = (row.get(image_column) or "").strip()
            mask_value = (row.get(mask_column) or "").strip()
            if not image_value or not mask_value:
                continue

            image_path = _resolve_overlay_path(image_value, images_base_dir)
            mask_path = _resolve_overlay_path(mask_value, masks_base_dir)

            # When both columns are the same (common case with DICOM CSVs),
            # infer mask file extension from --mask-extension (default .png).
            if image_column == mask_column:
                extension = (
                    mask_extension
                    if mask_extension.startswith(".")
                    else f".{mask_extension}"
                )
                mask_path = mask_path.with_suffix(extension)

            csv_pairs.append((image_path, mask_path))

    if not csv_pairs:
        raise FileNotFoundError("No valid image/mask rows were found in the CSV")

    if start_index < 0 or start_index >= len(csv_pairs):
        raise IndexError(
            f"start_index {start_index} is out of range for {len(csv_pairs)} rows"
        )

    selected_pairs = csv_pairs[start_index:]
    if max_images is not None:
        if max_images <= 0:
            raise ValueError("max_images must be greater than 0 when provided")
        selected_pairs = selected_pairs[:max_images]

    pairs: list[tuple[Path, Path]] = []
    missing_pairs: list[tuple[Path, Path]] = []
    for image_path, mask_path in selected_pairs:
        if image_path.exists() and mask_path.exists():
            pairs.append((image_path, mask_path))
        else:
            missing_pairs.append((image_path, mask_path))

    return pairs, missing_pairs


def show_dataset_segmentation_overlays_batch(
    images_dir: str | Path | None = None,
    masks_dir: str | Path | None = None,
    batch_size: int = 8,
    columns: int = 4,
    alpha: float = 0.35,
    mask_cmap: str = "autumn",
    mask_threshold: float = 0.0,
    mask_suffix: str = "",
    mask_extension: str = ".png",
    start_index: int = 0,
    max_images: int | None = None,
    recursive: bool = True,
    pairs_csv: str | Path | None = None,
    csv_image_column: str = "image_path",
    csv_mask_column: str = "mask_path",
    csv_delimiter: str = ",",
) -> dict[str, int]:
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0")
    if columns <= 0:
        raise ValueError("columns must be greater than 0")
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must be in [0, 1]")

    pairs: list[tuple[Path, Path]]
    missing_pairs: list[tuple[Path, Path]]

    if pairs_csv is not None:
        pairs, missing_pairs = load_overlay_pairs_from_csv(
            pairs_csv,
            image_column=csv_image_column,
            mask_column=csv_mask_column,
            delimiter=csv_delimiter,
            images_base_dir=images_dir,
            masks_base_dir=masks_dir,
            mask_extension=mask_extension,
            start_index=start_index,
            max_images=max_images,
        )
    else:
        if images_dir is None or masks_dir is None:
            raise ValueError("images_dir and masks_dir are required when pairs_csv is not used")

        image_paths = list_dataset_images_for_overlay(images_dir, recursive=recursive)
        if start_index < 0 or start_index >= len(image_paths):
            raise IndexError(
                f"start_index {start_index} is out of range for {len(image_paths)} images"
            )

        selected_images = image_paths[start_index:]
        if max_images is not None:
            if max_images <= 0:
                raise ValueError("max_images must be greater than 0 when provided")
            selected_images = selected_images[:max_images]

        pairs = []
        missing_pairs = []

        for image_path in selected_images:
            mask_path = _build_mask_path(
                image_path,
                masks_dir=masks_dir,
                mask_suffix=mask_suffix,
                mask_extension=mask_extension,
            )

            if mask_path.exists():
                pairs.append((image_path, mask_path))
            else:
                missing_pairs.append((image_path, mask_path))

    if not pairs:
        raise FileNotFoundError(
            "No image/mask pairs were found. "
            "Check masks_dir, mask_suffix, and mask_extension values."
        )

    print(f"[overlay] Pairs found: {len(pairs)}")
    if missing_pairs:
        print(f"[overlay] Missing pairs: {len(missing_pairs)}")
        for missing_image, missing_mask in missing_pairs[:5]:
            print(f"  - image={missing_image} | mask={missing_mask}")
        if len(missing_pairs) > 5:
            print("  - ...")

    total_batches = int(np.ceil(len(pairs) / batch_size))

    for batch_index in range(total_batches):
        start = batch_index * batch_size
        end = min(start + batch_size, len(pairs))
        batch_pairs = pairs[start:end]

        rows = int(np.ceil(len(batch_pairs) / columns))
        figure, axes = plt.subplots(rows, columns, figsize=(columns * 4, rows * 4))
        axes_array = np.atleast_1d(axes).reshape(-1)

        for axis in axes_array:
            axis.axis("off")

        for axis, (image_path, mask_path) in zip(axes_array, batch_pairs):
            image = load_image_for_overlay(image_path)
            mask = load_mask_for_overlay(mask_path, threshold=mask_threshold)

            if image.shape != mask.shape:
                raise ValueError(
                    "Image and mask shapes must match. "
                    f"{image_path.name}: {image.shape} vs {mask_path.name}: {mask.shape}"
                )

            overlay = np.ma.masked_where(~mask, mask)
            coverage_percent = float(mask.mean() * 100.0)

            axis.imshow(image, cmap="gray")
            axis.imshow(overlay, cmap=mask_cmap, alpha=alpha, interpolation="nearest")
            axis.set_title(f"{image_path.name}\nmask={coverage_percent:.1f}%", fontsize=9)
            axis.axis("off")

        figure.suptitle(
            f"Batch {batch_index + 1}/{total_batches} "
            f"(images {start + 1}-{end} of {len(pairs)})",
            fontsize=12,
        )
        figure.tight_layout()
        plt.show(block=True)
        plt.close(figure)

        if batch_index < total_batches - 1:
            user_input = input("Enter para continuar al siguiente batch (q para salir): ").strip().lower()
            if user_input == "q":
                print("[overlay] Visualizacion interrumpida por el usuario")
                return {
                    "pairs_found": len(pairs),
                    "missing_masks": len(missing_pairs),
                    "batches_shown": batch_index + 1,
                }

    return {
        "pairs_found": len(pairs),
        "missing_masks": len(missing_pairs),
        "batches_shown": total_batches,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Muestra imagenes en batch con su segmentacion solapada para inspeccion visual. "
            "Por defecto busca mascara '<stem>.png' en masks_dir, o usa --pairs-csv para mapear rutas exactas."
        )
    )
    parser.add_argument(
        "images_dir",
        type=Path,
        nargs="?",
        default=None,
        help="Directorio con imagenes (DICOM o raster). Opcional si usas --pairs-csv",
    )
    parser.add_argument(
        "masks_dir",
        type=Path,
        nargs="?",
        default=None,
        help="Directorio con mascaras. Opcional si usas --pairs-csv con rutas absolutas",
    )
    parser.add_argument("--batch-size", type=int, default=8, help="Numero de imagenes por batch")
    parser.add_argument("--columns", type=int, default=4, help="Columnas de la grilla")
    parser.add_argument("--alpha", type=float, default=0.35, help="Transparencia del overlay [0,1]")
    parser.add_argument("--mask-cmap", type=str, default="autumn", help="Colormap para la mascara")
    parser.add_argument("--mask-threshold", type=float, default=0.0, help="Umbral binario de mascara")
    parser.add_argument("--mask-suffix", type=str, default="", help="Sufijo de mascara (ej: _mask)")
    parser.add_argument("--mask-extension", type=str, default=".png", help="Extension de mascaras")
    parser.add_argument("--start-index", type=int, default=0, help="Indice de inicio")
    parser.add_argument("--max-images", type=int, default=None, help="Maximo de imagenes a mostrar")
    parser.add_argument(
        "--pairs-csv",
        type=Path,
        default=None,
        help="CSV con columnas de ruta de imagen y mascara",
    )
    parser.add_argument(
        "--csv-image-column",
        type=str,
        default="image_path",
        help="Nombre de columna de imagen en CSV",
    )
    parser.add_argument(
        "--csv-mask-column",
        type=str,
        default="mask_path",
        help="Nombre de columna de mascara en CSV",
    )
    parser.add_argument(
        "--csv-delimiter",
        type=str,
        default=",",
        help="Separador del CSV (por ejemplo ',' o ';')",
    )
    parser.add_argument(
        "--non-recursive",
        action="store_true",
        help="No buscar recursivamente dentro de subcarpetas",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.pairs_csv is None and (args.images_dir is None or args.masks_dir is None):
        raise ValueError("Debes pasar images_dir y masks_dir, o usar --pairs-csv")

    summary = show_dataset_segmentation_overlays_batch(
        images_dir=args.images_dir,
        masks_dir=args.masks_dir,
        batch_size=args.batch_size,
        columns=args.columns,
        alpha=args.alpha,
        mask_cmap=args.mask_cmap,
        mask_threshold=args.mask_threshold,
        mask_suffix=args.mask_suffix,
        mask_extension=args.mask_extension,
        start_index=args.start_index,
        max_images=args.max_images,
        recursive=not args.non_recursive,
        pairs_csv=args.pairs_csv,
        csv_image_column=args.csv_image_column,
        csv_mask_column=args.csv_mask_column,
        csv_delimiter=args.csv_delimiter,
    )
    print(
        "[overlay] Finalizado. "
        f"pairs={summary['pairs_found']}, "
        f"missing_masks={summary['missing_masks']}, "
        f"batches={summary['batches_shown']}"
    )


if __name__ == "__main__":
    main()