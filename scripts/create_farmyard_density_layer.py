import pandas as pandas
import geopandas as gpd

from config.config import PATH_TO_REF_RASTER, PATH_TO_REF_GRID_VECTOR, PATH_TO_FARMYARD_DENSITY_LAYER, PATH_TO_FARMYARD_DENSITY_VECTOR, PATH_TO_FARMYARD_DS, PROJECT_EPSG
from src.gdal_wrapper import gdal_rasterize_vector_layer
from src.utils import create_density_layer_vector, calculate_area


if __name__ == "__main__":

    # read in and prepare land use data
    farmyard_gdf = gpd.read_file(PATH_TO_FARMYARD_DS)
    farmyard_gdf = farmyard_gdf.to_crs(PROJECT_EPSG)

    # read in reference grid vector shapes
    ref_grid_vector = gpd.read_file(PATH_TO_REF_GRID_VECTOR)
    ref_grid_vector = ref_grid_vector.reset_index()

    # create vector file of farmyard density
    create_density_layer_vector(
        farmyard_gdf, ref_grid_vector, PATH_TO_FARMYARD_DENSITY_VECTOR, calculate_area)

    # rasterize farmyard density vector file
    gdal_rasterize_vector_layer(PATH_TO_FARMYARD_DENSITY_VECTOR, PATH_TO_FARMYARD_DENSITY_LAYER, PATH_TO_REF_RASTER,
                                "farmyard_density_layer_vector", "density")
