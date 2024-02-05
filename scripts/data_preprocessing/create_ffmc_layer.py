import os
from typing import List
import argparse
import netCDF4 as nc
import numpy as np
import rasterio

from config.config import BASE_PATH, PATH_TO_PATH_CONFIG_FILE, BBOX_AUSTRIA
from src.utils import load_paths_from_yaml, replace_base_path
from src.gdal_wrapper import gdal_align_and_resample, gdal_create_geotiff_from_nc
from src.data_collection.inca_data_extraction import get_geosphere_data_grid
from src.data_preprocessing.inca_data_preprocessing import calculate_wind_speed, calculate_ffmc, calculate_date_of_interest_x_hours_before

RESAMPLE_ALGORITHM = "Nearest Neighbor"
FFMC_INITIAL_VALUE = 85
PARAMETER_RAINFALL = ["RR"]
PARAMETERS_OTHER = ['T2M', 'UU', 'VV', 'RH2M']


def bbox_to_str(bbox: List[float]) -> str:
    """Converts list of floats to string"""
    return ",".join(map(str, bbox))


def calculate_ffmc_from_inca_parameters(path_to_rainfall_nc: str, path_to_other_parameters_nc: str,
                                        ffmc_0: np.array = None) -> tuple:
    """Extracts arrays from INCA NetCDF files"""
    with nc.Dataset(path_to_rainfall_nc, 'r') as nc_rainfall, nc.Dataset(path_to_other_parameters_nc, 'r') as nc_inca_param:
        rainfall_data = nc_rainfall.variables["RR"][:].sum(axis=0)
        uu_data = nc_inca_param.variables["UU"][:][0]
        vv_data = nc_inca_param.variables["VV"][:][0]
        t2m_data = nc_inca_param.variables["T2M"][:][0]
        rh2m_data = nc_inca_param.variables["RH2M"][:][0]
        wind_speed_data = calculate_wind_speed(uu_data, vv_data)

        if ffmc_0 is None:
            ffmc_0 = np.full(wind_speed_data.shape, FFMC_INITIAL_VALUE)

        calculate_ffmc_vectorized = np.vectorize(calculate_ffmc)
        ffmc_data = calculate_ffmc_vectorized(
            ffmc_0, rh2m_data, t2m_data, rainfall_data, wind_speed_data)

        lon = nc_inca_param.variables['lon'][:]
        lat = nc_inca_param.variables['lat'][:]

        return ffmc_data, lon, lat


def create_ffmc_layer_paths(paths: dict, date_str_for_file_name: str) -> tuple:
    """Creates paths to intermediate and final FFMC layers"""
    path_to_intermediate_ffmc_layer = paths["ffmc"]["intermediate"] + \
        f"_{date_str_for_file_name}.tif"
    path_to_ffmc_layer = paths["ffmc"]["final"] + \
        f"_{date_str_for_file_name}.tif"
    return path_to_intermediate_ffmc_layer, path_to_ffmc_layer


def load_ffmc_layer(paths: dict, date: str, intermediate: bool) -> np.array:
    """load ffmc layer from a given date

    Args:
        paths (dict): dictionary of all project paths
        date (str): Date for which ffmc layer should be retrieved in format 'YYYY-MM-DDTHH:MM'
        intermediate (bool): If the intermediate ffmc layer (1km resolution) needs to be retrieved, set to True. Otherwise, the final ffmc layer is retrieved

    Returns:
        np.array: ffmc layer values
    """

    if intermediate:
        path_to_ffmc_layer, _ = create_ffmc_layer_paths(paths,
                                                        date.split("T")[0].replace("-", ""))
    else:
        _, path_to_ffmc_layer = create_ffmc_layer_paths(paths,
                                                        date.split("T")[0].replace("-", ""))

    if os.path.exists(path_to_ffmc_layer):
        with rasterio.open(path_to_ffmc_layer) as src:
            return src.read(1)


def create_ffmc_layer(paths: dict, date_of_interest: str, bbox: List[float]) -> None:
    """Creates FFMC layer aligned with reference grid"""

    date_of_interest_24h_before = calculate_date_of_interest_x_hours_before(
        date_of_interest, 24)
    date_str_for_file_name = date_of_interest.split("T")[0].replace("-", "")

    path_to_intermediate_ffmc_layer, path_to_ffmc_layer = create_ffmc_layer_paths(paths,
                                                                                  date_str_for_file_name)

    # TODO maybe change paths here
    path_to_rain_netcdf = get_geosphere_data_grid(
        PARAMETER_RAINFALL, date_of_interest_24h_before, date_of_interest, bbox_to_str(bbox), paths["ffmc"]["source"])
    path_to_inca_other_netcdf = get_geosphere_data_grid(
        PARAMETERS_OTHER, date_of_interest_24h_before, date_of_interest, bbox_to_str(bbox), paths["ffmc"]["source"])

    # we need intermediate ffmc layer from previous day to calculate ffmc layer of current day
    ffmc_prev_intermediate = load_ffmc_layer(
        paths, date_of_interest_24h_before, intermediate=True)

    ffmc_arr, lon_arr, lat_arr = calculate_ffmc_from_inca_parameters(
        path_to_rain_netcdf, path_to_inca_other_netcdf, ffmc_prev_intermediate)

    gdal_create_geotiff_from_nc(
        ffmc_arr, lon_arr, lat_arr, path_to_intermediate_ffmc_layer)

    gdal_align_and_resample(path_to_intermediate_ffmc_layer, path_to_ffmc_layer,
                            paths["reference_grid"]["raster"], RESAMPLE_ALGORITHM, 0)


def main():
    parser = argparse.ArgumentParser(description='Process FFMC data.')
    parser.add_argument('date_of_interest', type=str,
                        help='Date of interest in format "YYYY-MM-DDTHH:MM"')

    args = parser.parse_args()

    date_of_interest = args.date_of_interest

    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)

    create_ffmc_layer(paths, date_of_interest, BBOX_AUSTRIA)


if __name__ == "__main__":
    main()
