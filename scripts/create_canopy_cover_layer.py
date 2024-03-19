import os
from src.gdal_wrapper import gdal_resample, gdal_align_and_resample, set_zeros_to_nan
from config.config import BASE_PATH, PATH_TO_PATH_CONFIG_FILE
from src.utils import load_paths_from_yaml, replace_base_path

RESAMPLE_ALG = "average"

if __name__ == "__main__":

    # Load paths from the YAML file
    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)

    tiles = ["A1", "B1", "C1", "C2", "C3", "D1", "D2", "D3", "E1", "E2", "E3"]

    for tile in tiles: 

        print(tile)

        path_to_cc_1m = os.path.join(BASE_PATH, fr"data\raw\BOKU_canopy_cover\canopy_cover\{tile}_CC.tif")
        path_to_cc_10m = os.path.join(BASE_PATH, fr"data\processed\canopy_cover\{tile}_CC_10m.tif")
        path_to_cc_10m_no_zeros = os.path.join(BASE_PATH, fr"data\processed\canopy_cover\{tile}_CC_10m_no_zeros.tif")
        path_to_cc_100m = os.path.join(BASE_PATH, fr"data\processed\canopy_cover\{tile}_CC_100m.tif")

        # 1 step: aggregate to 10x10 meter with arithmetic mean (ignore nans)
        gdal_resample(path_to_cc_1m, path_to_cc_10m, 10, RESAMPLE_ALG)

        # 2 step: set zero values of 10m raster to nan, so that those pixels are ignored in the 100m aggregation
        set_zeros_to_nan(path_to_cc_10m, path_to_cc_10m_no_zeros)

        # 3 step: aggregate to 100x100 meter with arithmetic mean (ignore nans)
        gdal_align_and_resample(path_to_cc_10m_no_zeros, path_to_cc_100m, paths["reference_grid"]["raster"], RESAMPLE_ALG)
    
