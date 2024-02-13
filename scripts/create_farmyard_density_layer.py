import pandas as pandas
import geopandas as gpd

from config.config import PROJECT_EPSG, BASE_PATH, PATH_TO_PATH_CONFIG_FILE
from src.utils import load_paths_from_yaml, replace_base_path
from src.gdal_wrapper import gdal_rasterize_vector_layer
from src.data_preprocessing.static_layers_preprocessing import create_density_layer_vector, calculate_area


def main():

    # Load paths from the YAML file
    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)

    # read in and prepare land use data
    farmyard_gdf = gpd.read_file(paths["farmyard_density"]["source"])
    farmyard_gdf = farmyard_gdf.to_crs(PROJECT_EPSG)

    # read in reference grid vector shapes
    ref_grid_vector = gpd.read_file(paths["reference_grid"]["vector"])
    ref_grid_vector = ref_grid_vector.reset_index()

    # create vector file of farmyard density
    create_density_layer_vector(
        farmyard_gdf, ref_grid_vector, paths["farmyard_density"]["intermediate"], calculate_area)

    # rasterize farmyard density vector file
    gdal_rasterize_vector_layer(paths["farmyard_density"]["intermediate"], paths["farmyard_density"]
                                ["final"], paths["reference_grid"]["raster"], "farmyard_density_layer_vector", "density")


if __name__ == "__main__":
    main()
