# extractors/vendor.py

try:
    from ..models.metadata import VendorInfo
except ImportError:
    from models.metadata import VendorInfo


class VendorExtractor:
    @staticmethod
    def extract(ds):
        return VendorInfo(
            manufacturer=getattr(ds, "Manufacturer", None),
            model_name=getattr(
                ds,
                "ManufacturerModelName",
                None
            ),
            #software_version=getattr(ds, "SoftwareVersions", None),
        )