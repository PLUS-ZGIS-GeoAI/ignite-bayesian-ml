import os
from typing import List
import numpy as np
from osgeo import gdal
import geopandas as gpd
import rasterio

from config.config import BASE_PATH, PATH_TO_REF_RASTER, GEO
from src.gdal_wrapper import gdal_get_bool_mask_from_coords


if __name__ == "__main__":

    path_to_fire_events = os.path.join(
        BASE_PATH, "data/processed/fire_data/fire_data.shp")
    path_to_forest_type_layer = os.path.join(
        BASE_PATH, "data/processed/forest_type/tree_type_resampled_mode.tif")

    fire_data = gpd.read_file(path_to_fire_events)
    fire_events_coords = [(geom.x, geom.y) for geom in fire_data.geometry]
    bool_mask = gdal_get_bool_mask_from_coords(
        fire_events_coords, path_to_forest_type_layer)

    """
    with rasterio.open(path_to_forest_type_layer) as src:
        data = src.read()
        meta = src.profile

    with rasterio.open(PATH_TO_REF_RASTER) as src:
        data = src.read()
        meta_ref = src.profile

    print(meta)
    print(meta_ref)
    """
