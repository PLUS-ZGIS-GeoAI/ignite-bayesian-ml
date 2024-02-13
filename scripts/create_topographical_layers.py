from config.config import BASE_PATH, PATH_TO_PATH_CONFIG_FILE
from src.utils import load_paths_from_yaml, replace_base_path
from src.gdal_wrapper import gdal_align_and_resample


RESAMPLE_ALGORITHM = "Average"


def main():

    # Load paths from the YAML file
    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)
    paths_topo = paths["topographical_layers"]

    # resample elevation layer to reference raster
    gdal_align_and_resample(paths_topo["elevation"]["source"],
                            paths_topo["elevation"]["final"], paths["reference_grid"]["raster"], RESAMPLE_ALGORITHM)

    # resample slope layer to reference raster
    gdal_align_and_resample(paths_topo["slope"]["source"],
                            paths_topo["slope"]["final"], paths["reference_grid"]["raster"], RESAMPLE_ALGORITHM)

    # resample aspect to reference raster
    gdal_align_and_resample(paths_topo["aspect"]["source"],
                            paths_topo["aspect"]["final"], paths["reference_grid"]["raster"], RESAMPLE_ALGORITHM)


if __name__ == "__main__":
    main()
