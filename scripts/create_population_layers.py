
from src.utils import load_paths_from_yaml, replace_base_path
from config.config import PATH_TO_PATH_CONFIG_FILE, BASE_PATH
from src.gdal_wrapper import gdal_align_and_resample, gdal_rasterize_vector_layer

RESAMPLE_ALGORITHM = "Average"


def create_population_layer(year: int, path_to_intermediate_pop_raster: str, path_to_pop_raster: str):

    # rasterize vector layer to grid (1000m resolution)
    gdal_rasterize_vector_layer(
        paths_pop["population_all_years_vector"], path_to_intermediate_pop_raster, paths_pop["intermediate_pop_ref_raster"], "geostat_pop", f"POP_{year}")

    # resample and align with reference raster
    gdal_align_and_resample(path_to_intermediate_pop_raster,
                            path_to_pop_raster, paths["reference_grid"]["raster"], RESAMPLE_ALGORITHM)


if __name__ == "__main__":

    # Load paths from the YAML file
    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)
    paths_pop = paths["population_layers"]

    create_population_layer(
        2006, paths_pop["2006"]["intermediate"], paths_pop["2006"]["final"])
    create_population_layer(
        2011, paths_pop["2011"]["intermediate"], paths_pop["2011"]["final"])
    create_population_layer(
        2018, paths_pop["2018"]["intermediate"], paths_pop["2018"]["final"])
    create_population_layer(
        2021, paths_pop["2021"]["intermediate"], paths_pop["2021"]["final"])
