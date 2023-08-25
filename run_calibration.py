import pandas as pd
from glob import glob
import os
import imgparse
from src.sensor_defs import sensor_bands_defs
import numpy as np
from PIL import Image
from src.teflon_reflectance import teflon_reflectance
import tempfile
import cv2
import tifffile as tf
from tqdm import tqdm
import shutil
import argparse
import warnings


tqdm.pandas()

def create_image_df(input_path, output_path  = None):
    image_df = pd.DataFrame()
    if not output_path:
        output_path = input_path + "_calibrada"
    image_df["image_path"] = glob(input_path + "/**/*.jpg", recursive = True)
    image_df["image_root"] = image_df.image_path.apply(os.path.dirname)
    image_df["image_name"] = image_df.image_path.apply(os.path.basename)
    image_df["parent_dir"] = image_df.image_root.apply(lambda path: os.path.split(path)[-1])
    image_df["output_base_path"] = output_path
    image_df["output_path"] = image_df.image_path.str.replace(input_path, output_path, regex = False)
    
    return image_df 


def apply_sensor_settings(image_df):
    rows = []
    for _, row in image_df.iterrows():
        parent_dir = row["parent_dir"]
        bands_def=  sensor_bands_defs[parent_dir]
        for band in bands_def:
            band_row = row.copy()
            band_row["band"] = band[0]
            band_row["band_math"] = band[1]
            band_row["band_index"] = band[2]
            
            dirname, base = os.path.split(row.output_path)
            band_row["output_path"] = os.path.join(dirname, band[0], base).replace(".jpg", ".tif")
    
            rows.append(band_row)
    
    return pd.DataFrame(rows)


def get_panel_reflectance_digital_number(row, top_left_rgb, bottom_right_rgb, top_left_nir, bottom_right_nir):
    image = np.array(Image.open(row["image_path"])).astype(np.uint8)
    
    if row["parent_dir"] == "RGB":
        bounds_indices = slice(top_left_rgb[1], bottom_right_rgb[1]), slice(top_left_rgb[0],bottom_right_rgb[0])
    elif row["parent_dir"] == "NIR":
        bounds_indices = slice(top_left_nir[1], bottom_right_nir[1]), slice(top_left_nir[0],bottom_right_nir[0])
    panel_pixels = image[bounds_indices]
    mean_reflectance_digital_number = panel_pixels.mean()
    return mean_reflectance_digital_number

def get_known_panel_reflectance(row):
    cent_arr, fwhm_arr = imgparse.get_wavelength_data(row.image_path)
    cent = int(cent_arr[int(row.band_index)])
    wfhm = int(fwhm_arr[int(row.band_index)])
    indexes = (teflon_reflectance["wavelengths"] >= cent - wfhm) & (teflon_reflectance["wavelengths"] <= cent + wfhm)
    indexes = [i for i, boolean_val in enumerate(indexes) if boolean_val == True]
    return np.average(np.take(teflon_reflectance["reflectance"], indexes))


def compute_reflectance_correction(image_df, calibration_image_name, top_left_rgb, bottom_right_rgb, top_left_nir, bottom_right_nir):
    calibration_df = image_df[image_df["image_name"] == calibration_image_name].copy()
    if len(calibration_df) == 0:
        raise Exception(f"No se ha existe la imagen{calibration_image_name}")
    calibration_df["mean_reflectance"] = calibration_df.apply(lambda row: get_panel_reflectance_digital_number(row, top_left_rgb, bottom_right_rgb, top_left_nir, bottom_right_nir), axis=1)
    
    calibration_df["slope_coefficient"] = (
        calibration_df.apply(lambda row: get_known_panel_reflectance(row), axis=1)
        / (calibration_df.mean_reflectance / calibration_df.autoexposure)
    )


    image_df = image_df.merge(
        calibration_df[["band", "slope_coefficient"]], on="band", how="outer"
    )

    return image_df



def compute_correction_coefficient(image_df_row):
    """Compute final correction coefficient."""
    return image_df_row.slope_coefficient / (
        image_df_row.autoexposure
    )



def isolate_band(image, band_math_arr):
    """
    Isolate a single band by performing bandmath on a multi-channel image.

    :param image: The multi-channel image
    :param band_math_arr: Describes the band math required to isolate the desired band
    :return: The isolated band
    """
    red_ch, green_ch, blue_ch = cv2.split(image)
    return (
        (band_math_arr[0] * red_ch if band_math_arr[0] != 0 else 0)
        + (band_math_arr[1] * green_ch if band_math_arr[1] != 0 else 0)
        + (band_math_arr[2] * blue_ch if band_math_arr[2] != 0 else 0)
    )


def apply_corrections(image_df_row):
    """Multiply input values by correction coefficients to generate reflectance values."""

    image_arr = np.asarray(Image.open(image_df_row.image_path)).astype(np.float32)
    # for images that represent data for multiple bands
    if "band_math" in image_df_row.index:
        # ignore saturated pixels
        saturation_indices = image_arr >= 255
        # ideally set to np.nan, but this messes up the stitching software
        image_arr[saturation_indices] = 255
        # perform band math
        image_arr = isolate_band(image_arr, image_df_row.band_math)

    image_arr = image_arr * image_df_row.correction_coefficient

    return image_arr

def write_image(image_arr_corrected, image_df_row, temp_dir):
    """Write corrected image to temporary location and record maximum value in case normalization is required."""
    path_list = os.path.normpath(image_df_row.image_path).split(os.path.sep)
    path_list[0] = temp_dir
    temp_path = os.path.join(*path_list)
    if "band_math" in image_df_row.index:
        dirname, base = os.path.split(temp_path)
        temp_path = os.path.join(dirname, image_df_row.band, base).replace(".jpg", ".tif")
  
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    # noinspection PyTypeChecker
    tf.imwrite(temp_path, image_arr_corrected)

    image_df_row["max_val"] = np.max(image_arr_corrected)
    image_df_row["temp_path"] = temp_path
    return image_df_row


def move_images(image_df_row):
    """Move corrected image to final destination."""
    shutil.move(image_df_row.temp_path, image_df_row.output_path)

def move_corrected_images(image_df):
    for folder in image_df.output_path.apply(os.path.dirname).unique():
        os.makedirs(folder, exist_ok=True)
    image_df.apply(lambda row: move_images(row), axis=1)


def main(input_path, calibration_image_name, top_left_rgb, bottom_right_rgb, top_left_nir, bottom_right_nir):
    image_df = create_image_df(input_path)
    print(f"'\n{len(image_df)} imagenes encontradas en el ruta: {input_path}")

    image_df = apply_sensor_settings(image_df)

    image_df["EXIF"] = image_df["image_path"].apply(imgparse.get_exif_data)

    # Get autoexposure correction:
    image_df["autoexposure"] = image_df.apply(
            lambda row: imgparse.get_autoexposure(row.image_path, row.EXIF) / 100, axis=1
    )
    # Get and sort by timestamp

    image_df["timestamp"] = image_df.apply(
            lambda row: imgparse.get_timestamp(row.image_path, row.EXIF), axis=1)

    image_df = image_df.set_index("timestamp", drop=False).sort_index()

    image_df = compute_reflectance_correction(image_df, calibration_image_name, top_left_rgb,bottom_right_rgb, top_left_nir,bottom_right_nir)

    image_df["correction_coefficient"] = image_df.apply(
        lambda row: compute_correction_coefficient(row), axis=1
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        # Apply corrections:
        image_df = image_df.progress_apply(
            lambda row: write_image(apply_corrections(row), row, temp_dir), axis=1
        )
        
        move_corrected_images(image_df)
    
    print(f'\nNuevas imagenes guardadas en {image_df.iloc[0]["output_base_path"]}')


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Entrenamiento para del modelo de entraccion de variables en los documentos ROS. Ejemplo: python train.py",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--input_path", default="./capturas/prueba",
                        help="Archivo de datos para entrenamiento")
   
    parser.add_argument("--calibration-image-name", default="IMG_00366.jpg", help="Archivo de datos con el conjunto de datos de prueba")
    
    parser.add_argument('-tlr', '--top-left-rgb', action='store',
                    type=int, nargs='*', default=[2022,938],
                    help="Examples: -tlr [2078, 967]")
    
    parser.add_argument('-brr', '--bottom-right-rgb', action='store',
                    type=int, nargs='*', default=[2078, 967],
                    help="Examples: -i item1 item2, -i item3")
    
    parser.add_argument('-tln', '--top-left-nir', action='store',
                    type=int, nargs='*', default= [2005, 1102],
                    help="Examples: -i item1 item2, -i item3")

    parser.add_argument('-brn', '--bottom-right-nir', action='store',
                    type=int, nargs='*', default=[2077, 1132],
                    help="Examples: -i item1 item2, -i item3")

    args = parser.parse_args()
    config = vars(args)
    
    main(**config)