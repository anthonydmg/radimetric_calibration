import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import cv2


#cent_arr, fwhm_arr = imgparse.get_wavelength_data(row.image_path)

teflon_reflectance = [0] * 380
teflon_reflectance.extend([1] * 900)

centralWavelength = [650, 548, 446]
wavelengthFWHM = [70, 45, 60]

def get_known_panel_reflectance_band(band_index):
    cent = centralWavelength[band_index]
    wfhm = wavelengthFWHM[band_index]
    return np.average(teflon_reflectance[cent - wfhm: cent + wfhm + 1])

def get_panel_reflectance_digital_number(image, band_index):
    image_band = image[:,:,band_index]
    top_left = np.array([2022, 938])
    bottom_right = np.array([2078, 967])
    bounds_indices = slice(top_left[1], bottom_right[1]), slice(top_left[0],bottom_right[0])
    panel_pixels = image_band[bounds_indices]
    mean_reflectance_digital_number = panel_pixels.mean()
    print("Mean DN: {:10.5f}".format(mean_reflectance_digital_number))
    return mean_reflectance_digital_number


input_path = "."
image_name = "IMG_00366"
image_rgb = np.asarray(Image.open(f"{input_path}/RGB/{image_name}.jpg"))


image_rgb_calibrate = image_rgb.copy()

for band in range(3):

    slope_coefficient = get_known_panel_reflectance_band(band) / get_panel_reflectance_digital_number(image_rgb_calibrate, band)
    print("slope_coefficient:", slope_coefficient)
    image_rgb_calibrate[:,:,band] = (image_rgb_calibrate[:,:,band] * slope_coefficient) * 255


fig, axes = plt.subplots(2,4, figsize = (16,10))

axes[0,0].imshow(image_rgb[:,:,0], cmap= "gray")
axes[0,0].set_title("Banda Roja")
axes[0,1].imshow(image_rgb[:,:,1], cmap= "gray")
axes[0,1].set_title("Banda Verde")
axes[0,2].imshow(image_rgb[:,:,2], cmap= "gray")
axes[0,2].set_title("Banda Azul")
axes[0,3].imshow(image_rgb, cmap= "gray")
axes[0,3].set_title("Imagen RGB")
axes[1,0].imshow(image_rgb_calibrate[:,:,0], cmap= "gray")
axes[1,0].set_title("Banda Roja Calibrada")
axes[1,1].imshow(image_rgb_calibrate[:,:,1], cmap= "gray")
axes[1,1].set_title("Banda Azul Calibrada")
axes[1,2].imshow(image_rgb_calibrate[:,:,2], cmap= "gray")
axes[1,2].set_title("Banda Verde Calibrada")
axes[1,3].imshow(image_rgb, cmap= "gray")
axes[1,3].set_title("Imagen RGB Calibrada")

plt.tight_layout()

## Split Bandas

plt.show()


#image_nir = np.asarray(Image.open(f"{input_path}/NIR/{image_name}.jpg"))

