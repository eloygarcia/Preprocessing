## https://www.kaggle.com/code/davidbroberts/mammography-apply-windowing

import numpy as np
import pydicom
import matplotlib.pyplot as plt
import cv2
from pydicom.pixel_data_handlers import apply_windowing, apply_voi_lut

from windowing import _apply_windowing_np_v1, _apply_windowing_np_v2

# This function extracts pixels from a DICOM file and uses stantard normalization to crunch the image down to 8 bit.
def get_pixels(dcm_file):
    im = pydicom.dcmread(dcm_file)
    data = im.pixel_array
    if im.PhotometricInterpretation == "MONOCHROME1":
        data = np.amax(data) - data
    else:
        data = data - np.min(data)
    if np.max(data) != 0:
        data = data / np.max(data)
    data=(data * 255).astype(np.uint8)
    return data



# This function uses pydicom's apply_windowing() function to apply the default window width and level specified in the DICOM tags
def get_pixels_with_windowing(dcm_file):
    im = pydicom.dcmread(dcm_file)
    data = im.pixel_array
    # This line is the only difference in the two functions
    data = apply_windowing(data, im)
    #data = apply_voi_lut(data, im)
    if im.PhotometricInterpretation == "MONOCHROME1":
        data = np.amax(data) - data
    else:
        data = data - np.min(data)
    if np.max(data) != 0:
        data = data / np.max(data)
    data=(data * 255).astype(np.uint8)
    return data


# The apply_windowing() function from pydicom uses the DICOM WindowWidth and WindowLevel tags to apply the specified "Window" to the image.
# You can also use apply_voi_lut() here. Since there aren't any VOI LUTs in this dataset, it reverts back to using the default WW/WL tags

# Open an image and get the pixels twice .. once without windowing and once with it.
#
file = "/home/eloygarcia/Escritorio/Datasets/[2025] - Mammo-MX/B0/000439_L_MLO_B0_D3"
file = "/home/eloygarcia/Escritorio/Checking_datasets/Prueba/MG_EGITIM_2/822670054/LCC.dcm"
file = "/home/eloygarcia/Escritorio/Datasets/inbreast/ALL-IMGS/20586960_6c613a14b80a8591_MG_R_ML_ANON.dcm"

im = pydicom.dcmread(file)
data = im.pixel_array

print(im.WindowWidth, im.WindowCenter)
print(data.shape, data.dtype, data.min(), data.max())
print(im.Rows, im.Columns, im.PhotometricInterpretation)

pixels = get_pixels(file)
pixels_with_windowing = get_pixels_with_windowing(file)

if im.PhotometricInterpretation == "MONOCHROME1":
    data = np.amax(data) - data
else:
    data = data - np.min(data)

#data=((data-data.min())/(np.max(data)-np.min(data)) * 255).astype(np.uint8)

other_pixels_with_windowing = _apply_windowing_np_v2(data, window_width=data.max(), window_center=data.max()//2, voi_func='LINEAR')
other_pixels_with_windowing = (other_pixels_with_windowing - np.min(other_pixels_with_windowing)) /(np.max(other_pixels_with_windowing) - np.min(other_pixels_with_windowing)) * 255
print(np.max(other_pixels_with_windowing), np.min(other_pixels_with_windowing))

other_pixels_with_windowing_2 = _apply_windowing_np_v2(data, window_width=data.max(), window_center=data.max()//2, voi_func='LINEAR_EXACT')
other_pixels_with_windowing_2 = (other_pixels_with_windowing_2 - np.min(other_pixels_with_windowing_2)) /(np.max(other_pixels_with_windowing_2) - np.min(other_pixels_with_windowing_2)) * 255
print(np.max(other_pixels_with_windowing_2), np.min(other_pixels_with_windowing_2))

other_pixels_with_windowing_3 = _apply_windowing_np_v2(data, window_width=data.max(), window_center=data.max()//2, voi_func='SIGMOID')
other_pixels_with_windowing_3 = (other_pixels_with_windowing_3 - np.min(other_pixels_with_windowing_3)) /(np.max(other_pixels_with_windowing_3) - np.min(other_pixels_with_windowing_3)) * 255
print(np.max(other_pixels_with_windowing_3), np.min(other_pixels_with_windowing_3))

# create a CLAHE object (Arguments are optional).
clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(128,128))
other_pixels_with_windowing_a = clahe.apply(other_pixels_with_windowing.astype('uint8'))
other_pixels_with_windowing_a = (other_pixels_with_windowing_a - np.min(other_pixels_with_windowing_a)) /(np.max(other_pixels_with_windowing_a) - np.min(other_pixels_with_windowing_a)) * 255
print(np.max(other_pixels_with_windowing_a), np.min(other_pixels_with_windowing_a))

other_pixels_with_windowing_b = clahe.apply(other_pixels_with_windowing_2.astype('uint8'))
other_pixels_with_windowing_b = (other_pixels_with_windowing_b - np.min(other_pixels_with_windowing_b)) /(np.max(other_pixels_with_windowing_b) - np.min(other_pixels_with_windowing_b)) * 255
print(np.max(other_pixels_with_windowing_b), np.min(other_pixels_with_windowing_b))

other_pixels_with_windowing_c = clahe.apply(other_pixels_with_windowing_3.astype('uint8'))
other_pixels_with_windowing_c = (other_pixels_with_windowing_c - np.min(other_pixels_with_windowing_c)) /(np.max(other_pixels_with_windowing_c) - np.min(other_pixels_with_windowing_c)) * 255
print(np.max(other_pixels_with_windowing_c), np.min(other_pixels_with_windowing_c))


# Plot the images
fig, axes = plt.subplots(nrows=3, ncols=3,sharex=False, sharey=True, figsize=(14, 10))
ax = axes.ravel()
ax[0].set_title(f'Original image')
ax[0].imshow(data, cmap='gray')
ax[1].set_title(f'Standard normalization')
ax[1].imshow(pixels, cmap='gray')
ax[2].set_title(f'With windowing')
ax[2].imshow(pixels_with_windowing, cmap='gray')
ax[3].set_title(f'With windowing (LINEAR)')
ax[3].imshow(other_pixels_with_windowing, cmap='gray')
ax[4].set_title(f'With windowing (LINEAR EXACT)')
ax[4].imshow(other_pixels_with_windowing_2, cmap='gray')
ax[5].set_title(f'With windowing (SIGMOID)')
ax[5].imshow(other_pixels_with_windowing_3, cmap='gray')
ax[6].set_title(f'With windowing (LINEAR) + CLAHE')
ax[6].imshow(other_pixels_with_windowing_a, cmap='gray')
ax[7].set_title(f'With windowing (LINEAR EXACT) + CLAHE')
ax[7].imshow(other_pixels_with_windowing_b, cmap='gray')
ax[8].set_title(f'With windowing (SIGMOID) + CLAHE')
ax[8].imshow(other_pixels_with_windowing_c, cmap='gray')
plt.show()




# Conclusion
#
# Applying windowing to DICOM images provides much better contrast and width of images.
# This technique should be applied to JPG/PNG exports.
# If the pydicom function apply_voi_lut() is used, it will also apply the default WW/WL values if a LUT does not exist .. which they routinely do not exist in mammography.
# Applying windowing allows for greater range when manually adjusting brightness/contrast later