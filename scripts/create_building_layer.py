import os
import rasterio
import numpy as np
import pandas as pandas
import geopandas as gpd

from config.config import BASE_PATH, PATH_TO_REF_RASTER, PROJECT_EPSG
from src.utils import write_array_to_geotiff
from src.gdal_wrapper import gdal_align_and_resample


def create_polygon_density_layer(polygon_layer: gpd.GeoDataFrame, ref_grid_vector: gpd.GeoDataFrame,  ref_raster_meta: dict, output_path: str) -> None:
    """Creates a GeoTIFF file storing the area (im m2) of intersecting polygons of each cell.

    Args:
        polygon_layer (gpd.GeoDataFrame): Vector layer containing polygons.
        ref_grid_vector (gpd.GeoDataFrame): Vectorized reference grid (each polygon represents a cell).
        ref_raster_meta (dict): Specifications of the reference grid.
        output_path (str): Directory and name of the output GeoTIFF.
    """

    # Intersect ref grid vector with road layer
    ref_raster_polygon_overlay = gpd.overlay(polygon_layer, ref_grid_vector)

    # Calculate length of road segment in each cell
    ref_raster_polygon_overlay["area"] = ref_raster_polygon_overlay.geometry.area
    polygon_area_per_cell = ref_raster_polygon_overlay.groupby(
        by="index").agg({"area": "sum"}).reset_index()

    # Merge road length information and ref grid
    polygon_density_layer = ref_grid_vector.merge(
        polygon_area_per_cell, on="index", how="left")

    # Convert to numpy array
    polygon_density_layer = np.array(polygon_density_layer["area"]).reshape(
        (ref_raster_meta["height"], ref_raster_meta["width"]))

    # Save as GeoTIFF
    write_array_to_geotiff(polygon_density_layer, ref_raster_meta, output_path)


if __name__ == "__main__":

    resample_algo = "Average"

    # specify paths
    PATH_TO_OSM_FARMYARD_LAYER = os.path.join(
        BASE_PATH, "data/processed/farmyard_density_layer/osm_lu_farmyards/osm_lu_farmyards.shp")
    PATH_TO_REFERENCE_GRID_VECTOR = os.path.join(
        BASE_PATH, "data/processed/reference_grid/inca_reference_grid_100m_vector/inca_reference_grid_100m.shp")
    PATH_TO_FARMYARD_DENSITY_LAYER = os.path.join(
        BASE_PATH, "data/processed/farmyard_density_layer/farmyard_density_layer.tif")
    PATH_TO_FARMYARD_DENSITY_LAYER_RESAMPLED = os.path.join(
        BASE_PATH, f"data/processed/farmyard_density_layer/farmyard_density_layer_resampled_{resample_algo}.tif")

    # read in and prepare land use data
    farmyard_gdf = gpd.read_file(PATH_TO_OSM_FARMYARD_LAYER)
    farmyard_gdf = farmyard_gdf.to_crs(PROJECT_EPSG)

    # read in specifications of reference grid
    with rasterio.open(PATH_TO_REF_RASTER) as src:
        ref_raster_meta = src.profile

    # read in reference grid vector shapes
    ref_grid_vector = gpd.read_file(PATH_TO_REFERENCE_GRID_VECTOR)
    ref_grid_vector = ref_grid_vector.reset_index()

    # create farmyard density layer
    create_polygon_density_layer(
        farmyard_gdf, ref_grid_vector, ref_raster_meta, PATH_TO_FARMYARD_DENSITY_LAYER)

    # align to other feature layers
    gdal_align_and_resample(PATH_TO_FARMYARD_DENSITY_LAYER,
                            PATH_TO_FARMYARD_DENSITY_LAYER_RESAMPLED, PATH_TO_REF_RASTER, resample_algo)
