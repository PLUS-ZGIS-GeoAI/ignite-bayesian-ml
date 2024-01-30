from typing import List
import netCDF4 as nc
import numpy as np
import pandas as pd

from config.config import BASE_PATH, PATH_TO_PATH_CONFIG_FILE, BBOX_AUSTRIA
from src.utils import load_paths_from_yaml, replace_base_path
from src.inca_data_extraction import get_geosphere_data, calculate_wind_speed
from src.fwi_system_calculator import calculate_ffmc
from src.gdal_wrapper import gdal_align_and_resample, gdal_create_geotiff_from_nc


RESAMPLE_ALGORITHM = "Nearest Neighbor"
FFMC_INITIAL_VALUE = 85
PARAMETER_RAINFALL = ["RR"]
PARAMETERS_OTHER = ['T2M', 'UU', 'VV', 'RH2M']


def bbox_to_str(bbox: List[float]) -> str:
    """converts list of floats to string"""
    return ",".join([str(coord) for coord in bbox])


if __name__ == "__main__":

    # Load paths from the YAML file
    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)

    # TODO outsource to functions "create_ffmc_layer"
    # TODO in production we need to implement functionality which checks if ffmc layer from previous day is available, otherwise initial value is used.
    date_of_interest = '2024-01-26T12:00'

    date_of_interest_24h_before = (pd.to_datetime(
        date_of_interest, format='%Y-%m-%dT%H:%M') - pd.Timedelta(hours=24)).isoformat()
    date_str_for_file_name = date_of_interest.split("T")[0].replace("-", "")

    path_to_intermediate_ffmc_layer = paths["ffmc"]["intermediate"] + \
        f"_{date_str_for_file_name}"
    path_to_ffmc_layer = paths["ffmc"]["final"] + \
        f"_{date_str_for_file_name}"

    path_to_rain_netcdf = get_geosphere_data(
        PARAMETER_RAINFALL, date_of_interest_24h_before, date_of_interest, bbox_to_str(BBOX_AUSTRIA), BASE_PATH)
    path_to_inca_other_netcdf = get_geosphere_data(
        PARAMETERS_OTHER, date_of_interest_24h_before, date_of_interest, bbox_to_str(BBOX_AUSTRIA), BASE_PATH)

    with nc.Dataset(path_to_rain_netcdf, 'r') as nc_rainfall, nc.Dataset(path_to_inca_other_netcdf, 'r') as nc_inca_param:
        rainfall_data = nc_rainfall.variables["RR"][:].sum(axis=0)
        uu_data = nc_inca_param.variables["UU"][:][0]
        vv_data = nc_inca_param.variables["VV"][:][0]
        t2m_data = nc_inca_param.variables["T2M"][:][0]
        rh2m_data = nc_inca_param.variables["RH2M"][:][0]
        wind_speed_data = calculate_wind_speed(uu_data, vv_data)
        ffmc_0 = np.full(wind_speed_data.shape, FFMC_INITIAL_VALUE)

        calculate_ffmc_vectorized = np.vectorize(calculate_ffmc)
        ffmc_data = calculate_ffmc_vectorized(
            ffmc_0, rh2m_data, t2m_data, rainfall_data, wind_speed_data)

        lon = nc_inca_param.variables['lon'][:]
        lat = nc_inca_param.variables['lat'][:]

    # create geotiff file from numpy arrays
    gdal_create_geotiff_from_nc(
        ffmc_data, lon, lat, path_to_intermediate_ffmc_layer)

    # align and resample to reference grid
    gdal_align_and_resample(
        path_to_intermediate_ffmc_layer, path_to_ffmc_layer, paths["reference_grid"]["raster"], RESAMPLE_ALGORITHM)
