try:
	from ..models.metadata import AcquisitionInfo
except ImportError:
	from models.metadata import AcquisitionInfo


class AcquisitionExtractor:
	@staticmethod
	def extract(ds) -> AcquisitionInfo:
		return AcquisitionInfo(
			kvp=getattr(ds, "KVP", None),
			exposure=getattr(ds, "Exposure", None),
			exposure_time=getattr(ds, "ExposureTime", None),
			tube_current=getattr(ds, "XRayTubeCurrent", None),
			compression_force=getattr(ds, "CompressionForce", None),
		)
