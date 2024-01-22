import os
import numpy as np
import geopandas as gpd
import rasterio

from config.config import BASE_PATH, PATH_TO_REF_RASTER, PROJECT_EPSG
from src.utils import write_array_to_geotiff
from src.gdal_wrapper import gdal_align_and_resample


def create_road_density_layer(road_layer: gpd.GeoDataFrame, ref_grid_vector: gpd.GeoDataFrame,  ref_raster_meta: dict, output_path: str) -> None:
    """Creates a GeoTIFF file storing the length (in meters) of intersecting roads for each cell.

    Args:
        road_layer (gpd.GeoDataFrame): Vector layer of road segments.
        ref_grid_vector (gpd.GeoDataFrame): Vectorized reference grid (each polygon represents a cell).
        ref_raster_meta (dict): Specifications of the reference grid.
        output_path (str): Directory and name of the output GeoTIFF.
    """

    # Intersect ref grid vector with road layer
    ref_raster_road_overlay = gpd.overlay(road_layer, ref_grid_vector)

    # Calculate length of road segment in each cell
    ref_raster_road_overlay["length"] = ref_raster_road_overlay.geometry.length
    road_len_per_cell = ref_raster_road_overlay.groupby(
        by="index").agg({"length": "sum"}).reset_index()

    # Merge road length information and ref grid
    road_density_layer = ref_grid_vector.merge(
        road_len_per_cell, on="index", how="left")

    # Convert to numpy array
    road_density_array = np.array(road_density_layer["length"]).reshape(
        (ref_raster_meta["height"], ref_raster_meta["width"]))

    # Save as GeoTIFF
    write_array_to_geotiff(road_density_array, ref_raster_meta, output_path)


if __name__ == "__main__":

    resample_algo = "Average"

    # specify directories
    PATH_TO_ROADS = os.path.join(
        BASE_PATH, "data/raw/OSM_austria/austria-latest-free/gis_osm_roads_free_1.shp")
    PATH_TO_RAILWAYS = os.path.join(
        BASE_PATH, "data/raw/OSM_austria/austria-latest-free/gis_osm_roads_free_1.shp")
    PATH_TO_REFERENCE_GRID_VECTOR = os.path.join(
        BASE_PATH, "data/processed/reference_grid/inca_reference_grid_100m_vector/inca_reference_grid_100m.shp")

    PATH_TO_RAILWAY_DENSITY_LAYER = os.path.join(
        BASE_PATH, "data/processed/road_density_layers/railway_density_layer.tif")
    PATH_TO_FORESTROAD_DENSITY_LAYER = os.path.join(
        BASE_PATH, "data/processed/road_density_layers/forestroad_density_layer.tif")
    PATH_TO_HIKINGTRAIL_DENSITY_LAYER = os.path.join(
        BASE_PATH, "data/processed/road_density_layers/hikingtrail_density_layer.tif")

    PATH_TO_RAILWAY_DENSITY_LAYER_RESAMPLED = os.path.join(
        BASE_PATH, f"data/processed/road_density_layers/railway_density_layer_resampled_{resample_algo}.tif")
    PATH_TO_FORESTROAD_DENSITY_LAYER_RESAMPLED = os.path.join(
        BASE_PATH, f"data/processed/road_density_layers/forestroad_density_layer_{resample_algo}.tif")
    PATH_TO_HIKINGTRAIL_DENSITY_LAYER_RESAMPLED = os.path.join(
        BASE_PATH, f"data/processed/road_density_layers/hikingtrail_density_layer_{resample_algo}.tif")

    # open specifications of reference raster
    with rasterio.open(PATH_TO_REF_RASTER) as src:
        REF_RASTER_META = src.profile

    # read in vector shapes of reference raster
    ref_grid_vector = gpd.read_file(PATH_TO_REFERENCE_GRID_VECTOR)
    ref_grid_vector.reset_index(inplace=True)

    # Read in and prepare railway data
    railways_gdf = gpd.read_file(PATH_TO_RAILWAYS)
    railways_gdf = railways_gdf.to_crs(PROJECT_EPSG)
    railways_gdf = railways_gdf[railways_gdf.fclass == "rail"]

    # read in and prepare hiking trails and forest road data
    roads_gdf = gpd.read_file(PATH_TO_ROADS)
    roads_gdf = roads_gdf.to_crs(PROJECT_EPSG)
    forestroads_gdf = roads_gdf[roads_gdf.fclass.isin(
        ["track", "track_grade1", "track_grade2", "track_grade3", "track_grade4", "track_grade5"])]
    hikingtrails_gdf = roads_gdf[roads_gdf.fclass == "path"]

    # create railroad density layer
    create_road_density_layer(
        railways_gdf, ref_grid_vector, REF_RASTER_META, PATH_TO_RAILWAY_DENSITY_LAYER)

    # create forestroads density layer
    create_road_density_layer(
        forestroads_gdf, ref_grid_vector, REF_RASTER_META, PATH_TO_FORESTROAD_DENSITY_LAYER)

    # create railroad density layer
    create_road_density_layer(
        hikingtrails_gdf, ref_grid_vector, REF_RASTER_META, PATH_TO_HIKINGTRAIL_DENSITY_LAYER)

    # align railroad density layer with other feature layers
    gdal_align_and_resample(PATH_TO_RAILWAY_DENSITY_LAYER,
                            PATH_TO_RAILWAY_DENSITY_LAYER_RESAMPLED, PATH_TO_REF_RASTER, resample_algo)

    # align railroad density layer with other feature layers
    gdal_align_and_resample(PATH_TO_FORESTROAD_DENSITY_LAYER,
                            PATH_TO_FORESTROAD_DENSITY_LAYER_RESAMPLED, PATH_TO_REF_RASTER, resample_algo)

    # align railroad density layer with other feature layers
    gdal_align_and_resample(PATH_TO_HIKINGTRAIL_DENSITY_LAYER,
                            PATH_TO_HIKINGTRAIL_DENSITY_LAYER_RESAMPLED, PATH_TO_REF_RASTER, resample_algo)
