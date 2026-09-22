from pathlib import Path

import numpy as np
import pytest

from api_stable.mammography import MammographyDicom
from api_stable.study import View
from repositories.local_repository import LocalRepository
from services.studyService import StudyService


def _write_dicom(path: Path, laterality: str, view: str):
    arr = np.arange(64 * 64, dtype=np.uint16).reshape(64, 64)
    m = MammographyDicom.from_numpy(
        arr,
        metadata_overrides={
            "breast": {
                "laterality": laterality,
                "view": view,
            }
        },
    )
    m.save_as_dicom(path)


def _make_study_folder(folder: Path, include_rmlo: bool = True):
    folder.mkdir(parents=True, exist_ok=True)
    _write_dicom(folder / "img_lcc.dcm", "L", "CC")
    _write_dicom(folder / "img_rcc.dcm", "R", "CC")
    _write_dicom(folder / "img_lmlo.dcm", "L", "MLO")
    if include_rmlo:
        _write_dicom(folder / "img_rmlo.dcm", "R", "MLO")


def test_load_complete_study(tmp_path):
    study_folder = tmp_path / "study_complete"
    _make_study_folder(study_folder, include_rmlo=True)

    repository = LocalRepository(tmp_path)
    service = StudyService(repository)

    study = service.get("study_complete")

    assert len(study) == 4
    assert study.is_complete is True
    assert set(study.images.keys()) == {View.LCC, View.RCC, View.LMLO, View.RMLO}
    assert service.validate("study_complete") is True


def test_load_incomplete_study_detects_missing_view(tmp_path):
    study_folder = tmp_path / "study_incomplete"
    _make_study_folder(study_folder, include_rmlo=False)

    repository = LocalRepository(tmp_path)
    service = StudyService(repository)

    # Repository can load incomplete studies, but the service contract validates on get().
    study = repository.load("study_incomplete")

    assert len(study) == 3
    assert study.is_complete is False
    assert View.RMLO in study.missing_views

    with pytest.raises(ValueError):
        service.get("study_incomplete")
    with pytest.raises(ValueError):
        service.validate("study_incomplete")


def test_load_dataset_recursively_finds_studies(tmp_path):
    root = tmp_path / "dataset"
    _make_study_folder(root / "patient_1" / "study_a", include_rmlo=True)
    _make_study_folder(root / "patient_2" / "study_b", include_rmlo=False)

    repository = LocalRepository(root)
    service = StudyService(repository)

    studies = service.load_all()

    # load_all() uses service.get() and therefore filters out invalid/incomplete studies.
    assert len(studies) == 1
    assert len(studies[0]) == 4
