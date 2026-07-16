try:
    from ..models.metadata import PatientInfo
except ImportError:
    from models.metadata import PatientInfo

class PatientExtractor:
    @staticmethod
    def extract(ds) -> PatientInfo:
        patient_id = ds.get("PatientID", None)
        age = ds.get("PatientAge", None)
        if age is not None:
            age_str = str(age)
            age_digits = "".join(ch for ch in age_str if ch.isdigit())
            age = int(age_digits) if age_digits else None
        sex = ds.get("PatientSex", None)
        return PatientInfo(patient_id=patient_id, age=age, sex=sex)