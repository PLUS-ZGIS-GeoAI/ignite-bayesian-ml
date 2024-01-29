import os
import geopandas as gpd
import rasterio

from config.config import BASE_PATH, PATH_TO_REF_RASTER, PROJECT_EPSG, REF_RASTER_EXTENT, REF_RASTER_SHAPE
from src.gdal_wrapper import gdal_rasterize_vector_layer, gdal_align_and_resample
from src.utils import create_density_layer_vector, calculate_length

if __name__ == "__main__":

    resample_algo = "nearest neighbor"

    # specify directories
    PATH_TO_ROADS = os.path.join(
        BASE_PATH, "data/raw/OSM_austria/austria-latest-free/gis_osm_roads_free_1.shp")
    PATH_TO_RAILWAYS = os.path.join(
        BASE_PATH, "data/raw/OSM_austria/austria-latest-free/gis_osm_railways_free_1.shp")
    PATH_TO_REFERENCE_GRID_VECTOR = os.path.join(
        BASE_PATH, "data/processed/reference_grid/inca_reference_grid_100m_vector_AUT/inca_ref_grid_100m_vector_AUT.shp")

    ROAD_TYPES = [
        ("rail", "railway_density_layer", "railway_density_layer_resampled"),
        (["track", "track_grade1", "track_grade2", "track_grade3", "track_grade4",
         "track_grade5"], "forestroad_density_layer", "forestroad_density_layer_resampled"),
        ("path", "hikingtrail_density_layer",
         "hikingtrail_density_layer_resampled")
    ]

    # Open specifications of reference raster
    with rasterio.open(PATH_TO_REF_RASTER) as src:
        REF_RASTER_META = src.profile

    # Read in vector shapes of reference raster
    ref_grid_vector = gpd.read_file(PATH_TO_REFERENCE_GRID_VECTOR)
    ref_grid_vector.reset_index(inplace=True)

    # Iterate over road types
    for road_type, layer_name, resampled_suffix in ROAD_TYPES:

        if road_type == "rail":
            # Read in and prepare road data
            road_gdf = gpd.read_file(PATH_TO_RAILWAYS)
        else:
            road_gdf = gpd.read_file(PATH_TO_ROADS)

        road_gdf = road_gdf.to_crs(PROJECT_EPSG)

        if isinstance(road_type, list):
            road_gdf = road_gdf[road_gdf.fclass.isin(road_type)]
        else:
            road_gdf = road_gdf[road_gdf.fclass == road_type]

        # Create road density vector layer
        create_density_layer_vector(road_gdf, ref_grid_vector, os.path.join(
            BASE_PATH, f"data/processed/road_density_layers/{layer_name}.shp"), calculate_length)

        # Rasterize vector layer
        gdal_rasterize_vector_layer(
            os.path.join(
                BASE_PATH, f"data/processed/road_density_layers/{layer_name}.shp"),
            os.path.join(
                BASE_PATH, f"data/processed/road_density_layers/{layer_name}.tif"),
            layer_name, "density", None, REF_RASTER_SHAPE, "0", REF_RASTER_EXTENT, "Float32", pixel_mode=True
        )

        # Align and resample to reference grid
        gdal_align_and_resample(
            os.path.join(
                BASE_PATH, f"data/processed/road_density_layers/{layer_name}.tif"),
            os.path.join(
                BASE_PATH, f"data/processed/road_density_layers/{resampled_suffix}_{resample_algo}.tif"),
            PATH_TO_REF_RASTER, resample_algo
        )
