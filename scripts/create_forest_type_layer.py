from config.config import BASE_PATH, PATH_TO_PATH_CONFIG_FILE
from src.utils import load_paths_from_yaml, replace_base_path
from src.gdal_wrapper import gdal_align_and_resample

RESAMPLE_ALGORITHM = "mode"


if __name__ == "__main__":

    # Load paths from the YAML file
    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)

    # resample forest type layer to reference grid
    gdal_align_and_resample(paths["forest_type"]["source"],
                            paths["forest_type"]["final"], paths["reference_grid"]["raster"], RESAMPLE_ALGORITHM)
