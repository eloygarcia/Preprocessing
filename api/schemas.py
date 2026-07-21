from pydantic import BaseModel
from typing import List, Optional


class StudySummary(BaseModel):
    folder: str
    number_of_images: int
    is_complete: bool
    missing_views: List[str]
    patient_name: Optional[str] = None
    study_date: Optional[str] = None
    study_uid: Optional[str] = None


class StudyLoadResponse(BaseModel):
    folder: str
    summary: StudySummary
