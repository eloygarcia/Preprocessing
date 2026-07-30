try:
	from ..models.metadata import ImageInfo
except ImportError:
	from models.metadata import ImageInfo

from pydicom.multival import MultiValue


def _as_float_tuple(values):
	if values is None:
		return None
	try:
		return tuple(float(v) for v in values)
	except TypeError:
		return None


class ImageExtractor:
	@staticmethod
	def extract(ds) -> ImageInfo:
		return ImageInfo(
			rows=getattr(ds, "Rows", None),
			columns=getattr(ds, "Columns", None),
			bits_stored=getattr(ds, "BitsStored", None),
			pixel_spacing=_as_float_tuple(getattr(ds, "PixelSpacing", None)),
			photometric_interpretation=getattr(ds, "PhotometricInterpretation", None),
			presentation_lut_shape=getattr(ds, "PresentationLUTShape", None),
			window_center = list(getattr(ds, "WindowCenter", None)) if isinstance(getattr(ds, "WindowCenter", None), MultiValue) else list([getattr(ds, "WindowCenter", None)]),
			window_width = list(getattr(ds, "WindowWidth", None)) if isinstance(getattr(ds, "WindowWidth", None), MultiValue) else list([getattr(ds, "WindowWidth", None)]),
			window_center_width_explanation = list(getattr(ds, "WindowCenterWidthExplanation", None)) if isinstance(getattr(ds, "WindowCenterWidthExplanation", None), MultiValue) else list([getattr(ds, "WindowCenterWidthExplanation", None)]),
			voi_lut_function=getattr(ds, "VOILUTFunction", None),
		)
