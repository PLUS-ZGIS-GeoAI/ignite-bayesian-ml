import os
from typing import List
import netCDF4 as nc
import numpy as np
import pandas as pd

from config.config import PATH_TO_REF_RASTER
from src.inca_data_extraction import get_geosphere_data, calculate_wind_speed
from src.fwi_system_calculator import calculate_ffmc
from src.gdal_wrapper import gdal_align_and_resample, gdal_create_geotiff_from_nc


def bbox_to_str(bbox: List[float]) -> str:
    return ",".join([str(coord) for coord in bbox])


if __name__ == "__main__":

    resample_algo = "Nearest Neighbor"

    # TODO in production we need to implement functionality which checks if ffmc layer from previous day is available, otherwise initial value is used.
    ffmc_initial_value = 85
    parameters_rainfall = ["RR"]
    parameters_other = ['T2M', 'UU', 'VV', 'RH2M']
    date_of_interest = '2024-01-26T12:00'
    date_of_interest_24h_before = (pd.to_datetime(
        date_of_interest, format='%Y-%m-%dT%H:%M') - pd.Timedelta(hours=24)).isoformat()
    bbox = [47.421389, 12.73, 48.776944, 15.036111]
    output_format = 'netcdf'

    # TODO only temporary BASE_PATH; eliminate when ready
    BASE_PATH = r"C:/Users/David/Documents/ZGIS/inca_file_store"

    date_str_for_file_name = date_of_interest.split("T")[0].replace("-", "")
    PATH_TO_FFMC_LAYER = os.path.join(
        BASE_PATH, f"ffmc_{date_str_for_file_name}.tiff")
    PAHT_TO_FFMC_LAYER_RESAMPLED = os.path.join(
        BASE_PATH, f"ffmc_resampled_{date_str_for_file_name}.tiff")

    path_to_rain_netcdf = get_geosphere_data(
        parameters_rainfall, date_of_interest_24h_before, date_of_interest, bbox_to_str(bbox), BASE_PATH)
    path_to_inca_other_netcdf = get_geosphere_data(
        parameters_other, date_of_interest_24h_before, date_of_interest, bbox_to_str(bbox), BASE_PATH)

    with nc.Dataset(path_to_rain_netcdf, 'r') as nc_rainfall, nc.Dataset(path_to_inca_other_netcdf, 'r') as nc_inca_param:
        rainfall_data = nc_rainfall.variables["RR"][:].sum(axis=0)
        uu_data = nc_inca_param.variables["UU"][:][0]
        vv_data = nc_inca_param.variables["VV"][:][0]
        t2m_data = nc_inca_param.variables["T2M"][:][0]
        rh2m_data = nc_inca_param.variables["RH2M"][:][0]
        wind_speed_data = calculate_wind_speed(uu_data, vv_data)
        ffmc_0 = np.full(wind_speed_data.shape, ffmc_initial_value)

        calculate_ffmc_vectorized = np.vectorize(calculate_ffmc)
        ffmc_data = calculate_ffmc_vectorized(
            ffmc_0, rh2m_data, t2m_data, rainfall_data, wind_speed_data)

        lon = nc_inca_param.variables['lon'][:]
        lat = nc_inca_param.variables['lat'][:]

    # create geotiff file from numpy arrays
    gdal_create_geotiff_from_nc(ffmc_data, lon, lat, PATH_TO_FFMC_LAYER)

    # align and resample to reference grid
    gdal_align_and_resample(
        PATH_TO_FFMC_LAYER, PAHT_TO_FFMC_LAYER_RESAMPLED, PATH_TO_REF_RASTER, resample_algo)
