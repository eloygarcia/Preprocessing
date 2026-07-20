import pydicom
import numpy as np
from pathlib import Path
from copy import deepcopy
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import (
    ExplicitVRLittleEndian,
    SecondaryCaptureImageStorage,
    generate_uid,
    PYDICOM_IMPLEMENTATION_UID,
)

from skimage.io import imread, imsave
from skimage.color import gray2rgb, rgb2gray

from api_stable.models.metadata import View

try:
    from .metadata.factory import MetadataFactory
    from .models.image import MammographyImage
except ImportError:
    try:
        from api_stable.metadata.factory import MetadataFactory
        from api_stable.models.image import MammographyImage
    except ImportError:
        from metadata.factory import MetadataFactory
        from models.image import MammographyImage

class MammographyDicom:
    def __init__(self, ds, path: Path | None = None, metadata=None):
        self.ds = ds
        self.path = path
        if metadata is not None:
            self.metadata = metadata
        elif ds is not None:
            self.metadata = MetadataFactory.create(ds)
        else:
            self.metadata = None
        self._image = None
    
    @property
    def image(self):
        if self._image is None:
            if self.ds is None:
                raise ValueError("No pixel data available. Use from_dicom/from_dataset or set an image first.")
            self._image = MammographyImage(
                pixel_array=self.ds.pixel_array,
            )
        return self._image
    
    
    @property
    def view(self) -> View:
        laterality = self.metadata.breast.laterality
        projection = self.metadata.breast.view
        return f"{laterality}{projection}"
        # return projection
    

    def _sync_metadata_from_image(self, image_overrides=None):
        if self._image is None:
            return self

        self.metadata = MetadataFactory.refresh_image_metadata(
            self.metadata,
            self._image.to_numpy(),
            image_overrides=image_overrides,
        )
        return self

    def _ensure_monochrome2(self):
        if self.metadata.image.photometric_interpretation == 'MONOCHROME1':
            self.image.convert_to_monochrome2()
            self._sync_metadata_from_image(
                image_overrides={
                    "photometric_interpretation": "MONOCHROME2",
                    "presentation_lut_shape": "IDENTITY",
                }
            )
        return self

    def _apply_windowing(self):
        if self.metadata is None:
            raise ValueError("Metadata is required to resolve windowing parameters.")

        window_center = self.metadata.image.window_center
        window_width = self.metadata.image.window_width
        # print(len(window_center))
        # print(len(window_width))
        
        if isinstance(window_center, pydicom.multival.MultiValue) and isinstance(window_width, pydicom.multival.MultiValue):
            window_center = window_center[0]
            window_width = window_width[0]
        
        voi_func = self.metadata.image.voi_lut_function

        self.image.apply_windowing(
            window_center=window_center,
            window_width=window_width,
            voi_lut_function=voi_func,
        )
        last_windowing = self.image.last_windowing or {}
        self._sync_metadata_from_image(
            image_overrides={
                "window_center": last_windowing.get("window_center", window_center),
                "window_width": last_windowing.get("window_width", window_width),
                "voi_lut_function": last_windowing.get("voi_lut_function", voi_func),
                "window_center_width_explanation": "APPLIED",
            }
        )
        return self

    @staticmethod
    def _prepare_pixel_array_for_dicom(pixel_array):
        """Convert arbitrary 2D numpy arrays to uint16 suitable for DICOM PixelData."""
        arr = np.asarray(pixel_array)
        if arr.ndim != 2:
            raise ValueError("Only 2D grayscale images are supported for DICOM export.")

        if np.issubdtype(arr.dtype, np.floating):
            arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
            arr_min = float(arr.min())
            arr_max = float(arr.max())
            if arr_max <= arr_min:
                arr_u16 = np.zeros_like(arr, dtype=np.uint16)
            else:
                arr_norm = (arr - arr_min) / (arr_max - arr_min)
                arr_u16 = np.round(arr_norm * 65535.0).astype(np.uint16)
        elif np.issubdtype(arr.dtype, np.signedinteger):
            arr_i64 = arr.astype(np.int64)
            arr_i64 = arr_i64 - arr_i64.min()
            arr_u16 = np.clip(arr_i64, 0, 65535).astype(np.uint16)
        else:
            arr_u16 = np.clip(arr, 0, 65535).astype(np.uint16)

        max_val = int(arr_u16.max())
        bits_stored = max(1, max_val.bit_length()) if max_val > 0 else 1
        bits_stored = min(bits_stored, 16)
        return arr_u16, bits_stored

    @staticmethod
    def _load_as_numpy(path: Path):
        try:
            image_array = imread(path, as_gray=True)
        except ImportError:
            import matplotlib.image as mpimg
            image_array = mpimg.imread(path)
            if image_array.ndim == 3:
                # Convert RGB/RGBA to grayscale to keep mammography pipeline 2D.
                image_array = rgb2gray(image_array)

        return image_array

    @staticmethod
    def _resolve_metadata_for_numpy(
        pixel_array,
        ds=None,
        metadata=None,
        metadata_defaults=None,
        metadata_file=None,
        metadata_preset=None,
        metadata_overrides=None,
    ):
        if metadata is not None:
            resolved_metadata = metadata
        elif ds is not None:
            resolved_metadata = MetadataFactory.create(ds)
        elif metadata_file is not None:
            resolved_metadata = MetadataFactory.create_from_file(
                metadata_file,
                pixel_array=pixel_array,
                preset_name=metadata_preset,
            )
        elif metadata_preset is not None:
            resolved_metadata = MetadataFactory.create_preset(
                metadata_preset,
                pixel_array=pixel_array,
                overrides=metadata_overrides,
            )
            return resolved_metadata
        elif metadata_defaults is not None:
            resolved_metadata = MetadataFactory.create_from_dict(
                metadata_defaults,
                pixel_array=pixel_array,
            )
        else:
            resolved_metadata = MetadataFactory.create_default_from_array(pixel_array)

        if metadata_overrides is not None:
            resolved_metadata = MetadataFactory.create_from_dict(
                MetadataFactory._deep_merge(
                    MetadataFactory.to_dict(resolved_metadata),
                    metadata_overrides,
                ),
                pixel_array=pixel_array,
            )

        return resolved_metadata

    def to_dicom_dataset(self, prefer_original_header=True, generate_new_uids=True):
        """Build a DICOM Dataset from the current instance image + metadata."""
        if self._image is None and self.ds is None:
            raise ValueError("No image available to export. Use from_dicom/from_png/from_numpy first.")

        if prefer_original_header and self.ds is not None:
            ds = deepcopy(self.ds)
        else:
            ds = Dataset()

        pixel_array = self.image.to_numpy() if self._image is not None else self.ds.pixel_array
        pixel_u16, bits_stored = self._prepare_pixel_array_for_dicom(pixel_array)
        rows, cols = pixel_u16.shape

        if not hasattr(ds, "file_meta") or ds.file_meta is None:
            ds.file_meta = FileMetaDataset()

        ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        ds.file_meta.ImplementationClassUID = PYDICOM_IMPLEMENTATION_UID

        if not getattr(ds, "SOPClassUID", None):
            ds.SOPClassUID = SecondaryCaptureImageStorage

        if generate_new_uids or not getattr(ds, "SOPInstanceUID", None):
            ds.SOPInstanceUID = generate_uid()

        ds.file_meta.MediaStorageSOPClassUID = ds.SOPClassUID
        ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID

        ds.Rows = rows
        ds.Columns = cols
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = (
            self.metadata.image.photometric_interpretation
            if self.metadata is not None and self.metadata.image.photometric_interpretation is not None
            else "MONOCHROME2"
        )
        ds.BitsAllocated = 16
        ds.BitsStored = bits_stored
        ds.HighBit = bits_stored - 1
        ds.PixelRepresentation = 0
        ds.PixelData = pixel_u16.tobytes()

        if self.metadata is not None:
            if self.metadata.patient.patient_id is not None:
                ds.PatientID = str(self.metadata.patient.patient_id)
            if self.metadata.patient.sex is not None:
                ds.PatientSex = str(self.metadata.patient.sex)
            if self.metadata.vendor.manufacturer is not None:
                ds.Manufacturer = str(self.metadata.vendor.manufacturer)
            if self.metadata.vendor.model_name is not None:
                ds.ManufacturerModelName = str(self.metadata.vendor.model_name)
            if self.metadata.breast.laterality is not None:
                ds.ImageLaterality = str(self.metadata.breast.laterality)
            if self.metadata.breast.view is not None:
                ds.ViewPosition = str(self.metadata.breast.view)
            if self.metadata.image.window_center is not None:
                ds.WindowCenter = float(self.metadata.image.window_center)
            if self.metadata.image.window_width is not None:
                ds.WindowWidth = max(float(self.metadata.image.window_width), 1.0)
            if self.metadata.image.voi_lut_function is not None:
                ds.VOILUTFunction = str(self.metadata.image.voi_lut_function)

        if not getattr(ds, "Modality", None):
            ds.Modality = "MG"

        return ds

    def normalize(self):
        self.image.normalize()
        self._sync_metadata_from_image(
            image_overrides={
                "window_center_width_explanation": "NORMALIZED",
            }
        )
        return self
    
    def copy(self):
        return deepcopy(self)

    @classmethod
    def from_dicom(cls, path):
        path = Path(path)
        ds = pydicom.dcmread(path)
        return cls(ds, path=path)
    
    @classmethod
    def from_dataset(cls, ds):
        return cls(ds=ds)

    @classmethod
    def from_numpy(
        cls,
        pixel_array,
        ds=None,
        metadata=None,
        metadata_defaults=None,
        metadata_file=None,
        metadata_preset=None,
        metadata_overrides=None,
    ):
        path = None
        if isinstance(pixel_array, (str, Path)):
            path = Path(pixel_array)
            ## Check if the path is a PNG, JPEG, TIFF, etc... file
            # if path.suffix.lower() != ".png": 
            #    raise ValueError("from_numpy only supports PNG paths when passing a file path.")
            pixel_array = cls._load_as_numpy(path)

        if not isinstance(pixel_array, np.ndarray):
            pixel_array = np.asarray(pixel_array)

        resolved_metadata = cls._resolve_metadata_for_numpy(
            pixel_array=pixel_array,
            ds=ds,
            metadata=metadata,
            metadata_defaults=metadata_defaults,
            metadata_file=metadata_file,
            metadata_preset=metadata_preset,
            metadata_overrides=metadata_overrides,
        )

        instance = cls(ds=ds, path=path, metadata=resolved_metadata)
        instance._image = MammographyImage(
            pixel_array=pixel_array,
        )
        instance._sync_metadata_from_image()
        return instance

    @classmethod
    def from_png(
        cls,
        path,
        metadata=None,
        metadata_defaults=None,
        metadata_file=None,
        metadata_preset=None,
        metadata_overrides=None,
    ):
        return cls.from_numpy(
            pixel_array=path,
            ds=None,
            metadata=metadata,
            metadata_defaults=metadata_defaults,
            metadata_file=metadata_file,
            metadata_preset=metadata_preset,
            metadata_overrides=metadata_overrides,
        )

    def initialize_image(self):
        self._ensure_monochrome2()
        self._apply_windowing()
        return self

    def save_as_dicom(self, output_path, prefer_original_header=True, generate_new_uids=True):
        """Export current instance as a DICOM file and return output path."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        ds = self.to_dicom_dataset(
            prefer_original_header=prefer_original_header,
            generate_new_uids=generate_new_uids,
        )
        ds.save_as(str(output_path), enforce_file_format=True)
        return output_path

if __name__=="__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    path = "/home/eloygarcia/Escritorio/Datasets/Mammo-MX/B1/000077_R_MLO_B1_D2"

    mammo = MammographyDicom.from_dicom(path)
     
    plt.imshow(mammo.image.pixel_array, cmap='gray')
    plt.show()

    print(mammo.metadata)