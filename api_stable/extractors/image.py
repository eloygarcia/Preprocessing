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
	def _as_list_or_none(value):
		if value is None:
			return None
		if isinstance(value, MultiValue):
			return list(value)
		return [value]

	@staticmethod
	def extract(ds) -> ImageInfo:
		return ImageInfo(
			rows=getattr(ds, "Rows", None),
			columns=getattr(ds, "Columns", None),
			bits_stored=getattr(ds, "BitsStored", None),
			pixel_spacing=_as_float_tuple(getattr(ds, "PixelSpacing", None)),
			photometric_interpretation=getattr(ds, "PhotometricInterpretation", None),
			presentation_lut_shape=getattr(ds, "PresentationLUTShape", None),
			window_center=ImageExtractor._as_list_or_none(getattr(ds, "WindowCenter", None)),
			window_width=ImageExtractor._as_list_or_none(getattr(ds, "WindowWidth", None)),
			window_center_width_explanation=ImageExtractor._as_list_or_none(getattr(ds, "WindowCenterWidthExplanation", None)),
			voi_lut_function=getattr(ds, "VOILUTFunction", None),
		)
