try:
	from ..models.metadata import BreastInfo
except ImportError:
	from models.metadata import BreastInfo


class BreastExtractor:
	@staticmethod
	def extract(ds) -> BreastInfo:
		implant = getattr(ds, "BreastImplantPresent", None)
		if isinstance(implant, str):
			implant = implant.upper() in {"YES", "Y", "TRUE", "1"}

		return BreastInfo(
			laterality=getattr(ds, "ImageLaterality", getattr(ds, "Laterality", None)),
			view=getattr(ds, "ViewPosition", None),
			breast_implant_present=implant,
		)
