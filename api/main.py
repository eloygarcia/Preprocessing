import sys
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException

from api.schemas import StudyLoadResponse, StudySummary
from api.image_service import build_image_response
from services.studyService import StudyService

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

app = FastAPI(title="Preprocessing API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/studies/load", response_model=StudyLoadResponse)
def load_study(folder: str) -> StudyLoadResponse:
    try:
        study = StudyService.load(folder)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    summary = StudySummary(
        folder=folder,
        number_of_images=StudyService.count_images(study),
        is_complete=study.is_complete,
        missing_views=[view.name for view in study.missing_views],
        patient_name=study.patient_name,
        study_date=study.study_date,
        study_uid=study.study_uid,
    )
    return StudyLoadResponse(folder=folder, summary=summary)


@app.get("/studies", response_model=List[StudyLoadResponse])
def list_studies(folder: str) -> List[StudyLoadResponse]:
    root = Path(folder)
    if not root.exists():
        raise HTTPException(status_code=404, detail="Folder not found")

    studies = StudyService.load_dataset(root)
    results = []
    for study in studies:
        results.append(
            StudyLoadResponse(
                folder=str(root),
                summary=StudySummary(
                    folder=str(root),
                    number_of_images=StudyService.count_images(study),
                    is_complete=study.is_complete,
                    missing_views=[view.name for view in study.missing_views],
                    patient_name=study.patient_name,
                    study_date=study.study_date,
                    study_uid=study.study_uid,
                ),
            )
        )
    return results


@app.get("/studies/image")
def study_image(folder: str):
    try:
        return build_image_response(folder)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
