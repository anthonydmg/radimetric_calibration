import pandas as pd
from glob import glob
import os
import imgparse
from sensor_defs import sensor_bands_defs

def create_image_df(input_path, output_path  = None):
    image_df = pd.DataFrame()
    if not output_path:
        output_path = input_path + "_calibrada"
    image_df["image_path"] = glob(input_path + "/**/*.jpg", recursive = True)
    image_df["image_root"] = image_df.image_path.apply(os.path.dirname)
    image_df["parent_dir"] = image_df.image_root.apply(lambda path: os.path.split(path)[-1])
    image_df["output_path"] = image_df.image_path.str.replace(input_path, output_path, regex = False)
    
    print(image_df.head())
    return image_df 

input_path = "capturas/prueba"

image_df = create_image_df(input_path)

def apply_sensor_settings(image_df):
    rows = []
    for _, row in image_df.iterrows():
        band_row = row.copy()
        band_row["band"] = band[0]

