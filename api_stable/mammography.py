import pydicom
import numpy as np
from pathlib import Path
from copy import deepcopy

from skimage.io import imread, imsave
from skimage.color import gray2rgb, rgb2gray

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
    
    def copy(self):
        return deepcopy(self)

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

    def normalize(self):
        self.image.normalize()
        self._sync_metadata_from_image(
            image_overrides={
                "window_center_width_explanation": "NORMALIZED",
            }
        )
        return self

    
    def initialize_image(self):
        self._ensure_monochrome2()
        self._apply_windowing()
        return self

    @classmethod
    def from_dicom(cls, path):
        path = Path(path)
        ds = pydicom.dcmread(path)
        return cls(ds, path=path)
    
    @classmethod
    def from_dataset(cls, ds):
        return cls(ds=ds)

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


if __name__=="__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    path = "/home/eloygarcia/Escritorio/Datasets/Mammo-MX/B1/000077_R_MLO_B1_D2"

    mammo = MammographyDicom.from_dicom(path)
     
    plt.imshow(mammo.image.pixel_array, cmap='gray')
    plt.show()

    print(mammo.metadata)