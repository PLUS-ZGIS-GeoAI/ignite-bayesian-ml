import os
from config import base_path
from src.gdal_wrapper import gdal_align_and_resample


if __name__ == "__main__":

    resample_alg = "nearest neighbor"

    path_to_ref_raster = os.path.join(
        base_path, "data/processed/reference_grid/INCA_ref_raster_since_2013_100m.tif")
    path_to_input_raster = os.path.join(
        base_path, "data/raw/BWF_forest_type/forest_type_merged.tif")
    path_to_output_raster = os.path.join(
        base_path, f"data/processed/forest_type/tree_type_resampled_{resample_alg}.tif")

    gdal_align_and_resample(path_to_input_raster,
                            path_to_output_raster, path_to_ref_raster, resample_alg)
