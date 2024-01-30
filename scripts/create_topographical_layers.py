import os
from config.config import PATH_TO_REF_RASTER, PATH_TO_ELEVATION_DS, PATH_TO_SLOPE_DS, PATH_TO_ASPECT_DS, PATH_TO_ELEVATION_LAYER, PATH_TO_SLOPE_LAYER, PATH_TO_ASPECT_LAYER
from src.gdal_wrapper import gdal_align_and_resample


if __name__ == "__main__":

    resample_alg = "Average"

    # resample elevation layer to reference raster
    gdal_align_and_resample(PATH_TO_ELEVATION_DS,
                            PATH_TO_ELEVATION_LAYER, PATH_TO_REF_RASTER, resample_alg)

    # resample slope layer to reference raster
    gdal_align_and_resample(PATH_TO_SLOPE_DS,
                            PATH_TO_SLOPE_LAYER, PATH_TO_REF_RASTER, resample_alg)

    # resample aspect to reference raster
    gdal_align_and_resample(PATH_TO_ASPECT_DS,
                            PATH_TO_ASPECT_LAYER, PATH_TO_REF_RASTER, resample_alg)
