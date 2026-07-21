from pathlib import Path
from typing import Optional

from fastapi.responses import FileResponse


def resolve_first_dicom_file(folder: str | Path) -> Optional[Path]:
    folder_path = Path(folder)
    if not folder_path.exists():
        return None

    for path in sorted(folder_path.iterdir()):
        if path.is_file() and path.suffix.lower() in {'.dcm', '.dicom'}:
            return path
    return None


def build_image_response(folder: str | Path):
    dicom_path = resolve_first_dicom_file(folder)
    if dicom_path is None:
        raise FileNotFoundError('No DICOM files found')
    return FileResponse(path=dicom_path, media_type='application/dicom')
