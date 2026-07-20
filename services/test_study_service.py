from pathlib import Path

import numpy as np
import pytest

from ..api_stable.mammography import MammographyDicom
from ..api_stable.study import View
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

    study = StudyService.load(study_folder)

    assert StudyService.count_images(study) == 4
    assert study.is_complete is True
    assert set(StudyService.list_views(study)) == {View.LCC, View.RCC, View.LMLO, View.RMLO}
    assert StudyService.validate(study) is True


def test_load_incomplete_study_detects_missing_view(tmp_path):
    study_folder = tmp_path / "study_incomplete"
    _make_study_folder(study_folder, include_rmlo=False)

    study = StudyService.load(study_folder)

    assert StudyService.count_images(study) == 3
    assert study.is_complete is False
    assert View.RMLO in study.missing_views
    assert StudyService.is_valid(study) is False
    with pytest.raises(ValueError):
        StudyService.validate(study)


def test_load_dataset_recursively_finds_studies(tmp_path):
    root = tmp_path / "dataset"
    _make_study_folder(root / "patient_1" / "study_a", include_rmlo=True)
    _make_study_folder(root / "patient_2" / "study_b", include_rmlo=False)

    studies = StudyService.load_dataset(root)

    assert len(studies) == 2
    assert sorted(len(s) for s in studies) == [3, 4]
