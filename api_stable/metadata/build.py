from .extractors.patient import PatientExtractor
from .extractors.vendor import VendorExtractor
from .extractors.acquisition import AcquisitionExtractor
from .extractors.breast import BreastExtractor
from .extractors.image import ImageExtractor
from .models.metadata import MammographyMetadata

def build_metadata(ds):
    return MammographyMetadata(
        patient=PatientExtractor.extract(ds),
        vendor=VendorExtractor.extract(ds),
        acquisition=AcquisitionExtractor.extract(ds),
        breast=BreastExtractor.extract(ds),
        image=ImageExtractor.extract(ds),
    )