from pathlib import Path
from dataclasses import dataclass

@dataclass
class StudyRecord:
    uid: str
    folder: Path
    patient_name: str
    study_date: str
    manufacturer: str