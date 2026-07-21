from dataclasses import dataclass, field
from datetime import datetime

from services.metadata.metadata import StudyResult
from api_stable.mammography import MammographyDicom

@dataclass
class MammographyCase:
    mammography: MammographyDicom
    results: StudyResult

@dataclass
class StudyCase:
    study_uid: str
    study_date: datetime
    patient_name: str
    manufacturer: str
    mammography_cases: list[MammographyCase] = field(default_factory=list)