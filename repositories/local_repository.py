from pathlib import Path
from typing import Dict, List

from api_stable.study import MammographyStudy
from pydicom.misc import is_dicom


class LocalRepository:
    """
    Repository that stores mammography studies in the local filesystem.

    The repository builds an index using the study folder.

    Later this class can be replaced by:
        - OrthancRepository
        - DicomWebRepository
        - PACSRepository
        - CloudRepository
    """
    def __init__(self, root_folder):
        self.root = Path(root_folder)
        self._index = {}
        self._build_index()

    def _build_index(self):
        self._index.clear()
        for folder in self.root.rglob("*"):
            if not folder.is_dir():
                continue
            #dicoms = list(folder.glob("*.dcm"))
            dicoms = [x for x in folder.glob("*") if is_dicom(x)]
            if len(dicoms) == 0:
                continue
            uid = folder.name
            self._index[uid] = folder

    def list(self) -> List[str]:
        return sorted(self._index.keys())

    def exists(self, uid):
        return uid in self._index

    def load(self, uid):
        if uid not in self._index:
            raise FileNotFoundError(uid)
        return MammographyStudy.from_folder(
            self._index[uid]
        )

    def load_all(self):
        return [
            self.load(uid)
            for uid in self.list()
        ]

    def number_of_studies(self):
        return len(self._index)

    def reload(self):
        self._build_index()