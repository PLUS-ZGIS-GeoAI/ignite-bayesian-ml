import os
from config.config import BASE_PATH, PATH_TO_REF_RASTER
from src.gdal_wrapper import gdal_align_and_resample


if __name__ == "__main__":

    resample_alg = "Average"

    path_to_elevation = os.path.join(
        BASE_PATH, "data/raw/OGD_Topographie/dhm_at_lamb_10m_2018.tif")
    path_to_slope = os.path.join(
        BASE_PATH, "data/processed/topographical_data/aspect_10m.tif")
    path_to_aspect = os.path.join(
        BASE_PATH, "data/processed/topographical_data/aspect_10m.tif")

    path_to_elevation_resampled = os.path.join(
        BASE_PATH, f"data/processed/topographical_data/elevation_resampled_{resample_alg}.tif")
    path_to_slope_resampled = os.path.join(
        BASE_PATH, f"data/processed/topographical_data/slope_resampled_{resample_alg}.tif")
    path_to_aspect_resampled = os.path.join(
        BASE_PATH, f"data/processed/topographical_data/aspect_resampled_{resample_alg}.tif")

    # resample elevation layer to reference raster
    gdal_align_and_resample(path_to_elevation,
                            path_to_elevation_resampled, PATH_TO_REF_RASTER, resample_alg)

    # resample slope layer to reference raster
    gdal_align_and_resample(path_to_slope,
                            path_to_slope_resampled, PATH_TO_REF_RASTER, resample_alg)

    # resample aspect to reference raster
    gdal_align_and_resample(path_to_aspect,
                            path_to_aspect_resampled, PATH_TO_REF_RASTER, resample_alg)
