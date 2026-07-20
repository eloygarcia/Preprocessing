from pathlib import Path
from typing import List
from pydicom.misc import is_dicom

try:
    from api_stable.study import MammographyStudy
except ImportError:
    from ..api_stable.study import MammographyStudy


# class StudyService:
#     """
#     Service responsible for loading and managing mammography studies.
#     """
#     @staticmethod
#     def load(folder: str | Path) -> MammographyStudy:
#         """
#         Load a study from a folder.
#         """
#         return MammographyStudy.from_folder(folder)

#     @staticmethod
#     def load_dataset(root: str | Path) -> List[MammographyStudy]:
#         """
#         Recursively load all studies contained in a dataset.
#         """
#         root = Path(root)
#         studies = []
#         for folder in root.rglob("*"):
#             if not folder.is_dir():
#                 continue
#             list_images = [x for x in list(folder.glob("*")) if is_dicom(x)]
#             if list_images:
#                 try:
#                     studies.append(
#                         MammographyStudy.from_folder(folder)
#                     )
#                 except Exception as e:
#                     print(f"Skipping {folder}: {e}")
#         return studies

#     @staticmethod
#     def validate(study: MammographyStudy) -> bool:
#         """
#         Validate a study.
#         """
#         study.validate()
#         return True

#     @staticmethod
#     def is_valid(study: MammographyStudy) -> bool:
#         try:
#             study.validate()
#             return True
#         except Exception:
#             return False

#     @staticmethod
#     def count_images(study: MammographyStudy) -> int:
#         return len(study)

#     @staticmethod
#     def list_views(study: MammographyStudy):
#         return list(study.images.keys())
    
## Study Service v2.0 by ChatGPT
"""
Elimina la dependencia local e interpone repositorios de modo que,
si se modifica la fuente de datos, no se modifique el servicio.
"""
class StudyService:
    def __init__(self, repository):
        self.repository = repository

    def get(self, uid):
        study = self.repository.load(uid)
        study.validate()
        return study

    def list(self):
        return self.repository.list()

    def load_all(self):
        studies = []
        for uid in self.list():
            try:
                studies.append(
                    self.get(uid)
                )
            except Exception:
                pass
        return studies

    
    def validate(self, uid):
        study = self.repository.load(uid)
        study.validate()
        return True

    def find_by_patient(self, patient_name):
        result = []
        for study in self.load_all():
            if study.patient_name == patient_name:
                result.append(study)
        return result

    def find_by_date(self, date):
        result = []
        for study in self.load_all():
            if study.study_date == date:
                result.append(study)
        return result

    def number_of_studies(self):
        return self.repository.number_of_studies()
    

if __name__ == "__main__":
    # Example usage
    study_folder = "/home/eloygarcia/Escritorio/Datasets/vinDr/physionet.org/files/vindr-mammo/1.0.0/images/004426a40da27ef22a866538b772ac44/"
    study = StudyService.load(study_folder)
    print(f"Loaded study with {StudyService.count_images(study)} images.")
    print(f"Views: {StudyService.list_views(study)}")