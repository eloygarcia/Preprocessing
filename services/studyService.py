from pathlib import Path
from typing import List
from pydicom.misc import is_dicom

try:
    from api_stable.study import MammographyStudy
except ImportError:
    from ..api_stable.study import MammographyStudy


class StudyService:
    """
    Service responsible for loading and managing mammography studies.
    """
    @staticmethod
    def load(folder: str | Path) -> MammographyStudy:
        """
        Load a study from a folder.
        """
        return MammographyStudy.from_folder(folder)

    @staticmethod
    def load_dataset(root: str | Path) -> List[MammographyStudy]:
        """
        Recursively load all studies contained in a dataset.
        """
        root = Path(root)
        studies = []
        for folder in root.rglob("*"):
            if not folder.is_dir():
                continue
            list_images = [x for x in list(folder.glob("*")) if is_dicom(x)]
            if list_images:
                try:
                    studies.append(
                        MammographyStudy.from_folder(folder)
                    )
                except Exception as e:
                    print(f"Skipping {folder}: {e}")
        return studies

    @staticmethod
    def validate(study: MammographyStudy) -> bool:
        """
        Validate a study.
        """
        study.validate()
        return True

    @staticmethod
    def is_valid(study: MammographyStudy) -> bool:
        try:
            study.validate()
            return True
        except Exception:
            return False

    @staticmethod
    def count_images(study: MammographyStudy) -> int:
        return len(study)

    @staticmethod
    def list_views(study: MammographyStudy):
        return list(study.images.keys())
    
if __name__ == "__main__":
    # Example usage
    study_folder = "/home/eloygarcia/Escritorio/Datasets/vinDr/physionet.org/files/vindr-mammo/1.0.0/images/004426a40da27ef22a866538b772ac44/"
    study = StudyService.load(study_folder)
    print(f"Loaded study with {StudyService.count_images(study)} images.")
    print(f"Views: {StudyService.list_views(study)}")