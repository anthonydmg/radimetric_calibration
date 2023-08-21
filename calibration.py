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

slope_coefficient = get_known_panel_reflectance_band(0) / get_panel_reflectance_digital_number(image_rgb, 0)

print("slope_coefficient:", slope_coefficient)
print("Banda Roja")
get_panel_reflectance_digital_number(image_rgb[:,:,0])
print("Banda Verde")
get_panel_reflectance_digital_number(image_rgb[:,:,1])
print("Banda Azul")
get_panel_reflectance_digital_number(image_rgb[:,:,2])
top_left = np.array([2022, 938])
bottom_right = np.array([2078, 967])
color = (255,0,0)
thickness = 3
image_rgb = cv2.rectangle(image_rgb, top_left, bottom_right, color, thickness)

plt.figure(figsize = (16,9))
plt.imshow(image_rgb)
plt.tight_layout()
plt.show()
#image_nir = np.asarray(Image.open(f"{input_path}/NIR/{image_name}.jpg"))

