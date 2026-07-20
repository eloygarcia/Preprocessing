from dataclasses import dataclass, field
from datetime import datetime

from results_api.metadata.metadata import StudyResult
from api_stable.mammography import MammographyDicom

@dataclass
class MammographyCase:
    mammography: MammographyDicom
    results: StudyResult