from config.config import PATH_TO_REF_RASTER, PATH_TO_FOREST_TYPE_DS, PATH_TO_FOREST_TYPE_Layer
from src.gdal_wrapper import gdal_align_and_resample


if __name__ == "__main__":

    resample_alg = "mode"

    gdal_align_and_resample(PATH_TO_FOREST_TYPE_DS,
                            PATH_TO_FOREST_TYPE_Layer, PATH_TO_REF_RASTER, resample_alg)
