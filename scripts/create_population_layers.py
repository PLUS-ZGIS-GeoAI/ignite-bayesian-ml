
from src.utils import load_paths_from_yaml, replace_base_path
from config.config import PATH_TO_PATH_CONFIG_FILE, BASE_PATH
from src.gdal_wrapper import gdal_align_and_resample, gdal_rasterize_vector_layer

RESAMPLE_ALGORITHM = "Average"


def create_population_layer(paths: dict, year: int):

    path_to_intermediate_pop_raster = paths["population_layers"][str(
        year)]["intermediate"]
    path_to_pop_raster = paths["population_layers"][str(year)]["final"]

    # rasterize vector layer to grid (1000m resolution)
    gdal_rasterize_vector_layer(
        paths["population_layers"]["population_all_years_vector"], path_to_intermediate_pop_raster,
        paths["population_layers"]["intermediate_pop_ref_raster"], "geostat_pop", f"POP_{year}")

    # resample and align with reference raster
    gdal_align_and_resample(path_to_intermediate_pop_raster,
                            path_to_pop_raster, paths["reference_grid"]["raster"], RESAMPLE_ALGORITHM)


def main():

    # Load paths from the YAML file
    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)

    # create population layers aligned with reference grid
    create_population_layer(paths, 2006)
    create_population_layer(paths, 2011)
    create_population_layer(paths, 2018)
    create_population_layer(paths, 2021)


if __name__ == "__main__":
    main()
