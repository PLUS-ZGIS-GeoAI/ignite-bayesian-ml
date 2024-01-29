import os
import rasterio
import pandas as pandas
import geopandas as gpd

from config.config import BASE_PATH, PATH_TO_REF_RASTER, PROJECT_EPSG, REF_RASTER_EXTENT, REF_RASTER_SHAPE
from src.gdal_wrapper import gdal_rasterize_vector_layer, gdal_align_and_resample
from src.utils import create_density_layer_vector, calculate_area


if __name__ == "__main__":

    resample_algo = "nearest neighbor"

    # specify paths
    PATH_TO_OSM_FARMYARD_LAYER = os.path.join(
        BASE_PATH, "data/processed/farmyard_density_layer/osm_lu_farmyards/osm_lu_farmyards.shp")
    PATH_TO_REFERENCE_GRID_VECTOR = os.path.join(
        BASE_PATH, "data/processed/reference_grid/inca_reference_grid_100m_vector_AUT/inca_ref_grid_100m_vector_AUT.shp")

    PATH_TO_FARMYARD_DENSITY_LAYER_VECTOR = os.path.join(
        BASE_PATH, "data/processed/farmyard_density_layer/farmyard_density_layer_vector.shp")
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

    # create vector file of farmyard density
    create_density_layer_vector(
        farmyard_gdf, ref_grid_vector, PATH_TO_FARMYARD_DENSITY_LAYER_VECTOR, calculate_area)

    # rasterize farmyard density vector file
    gdal_rasterize_vector_layer(PATH_TO_FARMYARD_DENSITY_LAYER_VECTOR, PATH_TO_FARMYARD_DENSITY_LAYER,
                                "farmyard_density_layer_vector", "density", None, REF_RASTER_SHAPE, "0", REF_RASTER_EXTENT, "Float32", pixel_mode=True)

    # align to other feature layers
    gdal_align_and_resample(PATH_TO_FARMYARD_DENSITY_LAYER,
                            PATH_TO_FARMYARD_DENSITY_LAYER_RESAMPLED, PATH_TO_REF_RASTER, resample_algo)
