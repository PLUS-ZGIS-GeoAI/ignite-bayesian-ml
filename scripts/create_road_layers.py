import os
from config.config import base_path, path_to_ref_raster
from src.gdal_wrapper import gdal_align_and_resample
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd


def write_array_to_geotiff(road_density_np: np.array, ref_raster_meta: dict, path_to_output: str):
    with rasterio.open(path_to_output, "w", **ref_raster_meta) as dst:
        arr = np.zeros((dst.height, dst.width), dtype=rasterio.float32)
        dst.write_band(1, road_density_np[0])


def create_road_density_layer(road_layer: gpd.GeoDataFrame, ref_grid_vector: gpd.GeoDataFrame, ref_grid_shape: tuple, ref_raster_meta: dict, path_to_raod_layer: str) -> None:
    ref_raster_road_overlay = gpd.overlay(road_layer, ref_grid_vector)
    ref_raster_road_overlay.lenght = ref_raster_road_overlay.geometry.length
    road_len_per_cell = ref_raster_road_overlay.groupby(
        by="index").agg({"length": sum})
    road_len_per_cell.reset_index(inplace=True)
    road_density_layer = pd.merge(
        ref_grid_vector, road_len_per_cell, on="index", how="left")
    road_density_layer = road_density_layer.length.values.reshape(
        ref_grid_shape)
    write_array_to_geotiff(road_density_layer, ref_raster_meta, path_to_raod_layer)


if __name__ == "__main__":

    path_to_street_layer = os.path.join(
        base_path, "data/raw/OSM_austria/austria-latest-free/gis_osm_roads_free_1.shp")

    # read in data
    street_layer = gpd.read_file(path_to_street_layer)
    street_layer = street_layer.to_crs("EPSG:31287")


    TODO
    - Test Code on small sample
    - Clean Code
    - Write/Update documentation of road features

