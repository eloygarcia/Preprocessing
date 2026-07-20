from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterator, Optional
from api_stable.models.metadata import View
from pydicom.misc import is_dicom

try:
    from .mammography import MammographyDicom
except ImportError:
    try:
        from api_stable.mammography import MammographyDicom
    except ImportError:
        from mammography import MammographyDicom


class MammographyStudy:
    """
    Represents a complete mammography study.
    A study is composed of up to four mammographic projections:
        - LCC
        - RCC
        - LMLO
        - RMLO
    """

    def __init__(self, images: Dict[View, MammographyDicom]):
        self._images = images

    @classmethod
    def from_folder(cls, folder: str | Path):
        folder = Path(folder)
        images = {}
        list_images = [x for x in sorted(folder.glob("*")) if is_dicom(x)]
        # list_images = sorted(folder.glob("*.dicom"))
        print(f"Found {len(list_images)} DICOM files in {folder}")
        for file in list_images:
            image = MammographyDicom.from_dicom(file)
            view = cls._detect_view(image)
            if view is not None:
                images[view] = image
        return cls(images)

    @staticmethod
    def _detect_view(image: MammographyDicom) -> Optional[View]:
        # Prefer normalized metadata extracted from DICOM.
        laterality = None
        projection = None

        if image.metadata is not None:
            laterality = image.metadata.breast.laterality
            projection = image.metadata.breast.view

        if laterality is None and image.ds is not None:
            laterality = getattr(image.ds, "ImageLaterality", getattr(image.ds, "Laterality", None))
        if projection is None and image.ds is not None:
            projection = getattr(image.ds, "ViewPosition", None)

        laterality = str(laterality).strip().upper() if laterality is not None else ""
        projection = str(projection).strip().upper() if projection is not None else ""

        if projection in {"LCC", "RCC", "LMLO", "RMLO"}:
            return View[projection]

        if laterality in {"LEFT", "L"}:
            laterality = "L"
        elif laterality in {"RIGHT", "R"}:
            laterality = "R"

        if projection in {"CC", "MLO"} and laterality in {"L", "R"}:
            return View[f"{laterality}{projection}"]

        return None

    @property
    def images(self):
        return self._images

    @property
    def LCC(self):
        return self._images.get(View.LCC)

    @property
    def RCC(self):
        return self._images.get(View.RCC)

    @property
    def LMLO(self):
        return self._images.get(View.LMLO)

    @property
    def RMLO(self):
        return self._images.get(View.RMLO)

    @property
    def number_of_images(self):
        return len(self._images)

    @property
    def is_complete(self):
        return self.number_of_images == 4

    @property
    def missing_views(self):
        return [v for v in View if v not in self._images]

    @property
    def patient_name(self):
        if not self._images:
            return None
        return next(iter(self._images.values())).patient_name

    @property
    def study_date(self):
        if not self._images:
            return None
        return next(iter(self._images.values())).study_date

    @property
    def study_uid(self):
        if not self._images:
            return None
        return next(iter(self._images.values())).study_uid

    def __len__(self):
        return len(self._images)

    def __iter__(self) -> Iterator[MammographyDicom]:
        return iter(self._images.values())

    def items(self):
        return self._images.items()

    def __getitem__(self, key):
        if isinstance(key, str):
            key = View[key.strip().upper()]
        return self._images[key]

    def validate(self):
        if not self.is_complete:
            raise ValueError(
                f"Study incomplete. Missing: {self.missing_views}"
            )

    def __repr__(self):
        views = ", ".join(v.name for v in self._images.keys())
        return (
            f"<MammographyStudy "
            f"images={len(self)} "
            f"views=[{views}]>"
        )
    
if __name__ == "__main__":
    study_folder = "/home/eloygarcia/Escritorio/Datasets/vinDr/physionet.org/files/vindr-mammo/1.0.0/images/004426a40da27ef22a866538b772ac44/"
    study = MammographyStudy.from_folder("study_folder")
    print(study)
    