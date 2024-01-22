import os
from config.config import BASE_PATH, PATH_TO_REF_RASTER
from src.gdal_wrapper import gdal_align_and_resample


if __name__ == "__main__":

    resample_alg = "nearest neighbor"

    path_to_input_raster = os.path.join(
        BASE_PATH, "data/raw/BWF_forest_type/forest_type_merged.tif")
    path_to_output_raster = os.path.join(
        BASE_PATH, f"data/processed/forest_type/tree_type_resampled_{resample_alg}.tif")

    gdal_align_and_resample(path_to_input_raster,
                            path_to_output_raster, PATH_TO_REF_RASTER, resample_alg)
