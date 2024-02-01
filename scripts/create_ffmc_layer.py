from typing import List
import argparse
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
    """Converts list of floats to string"""
    return ",".join(map(str, bbox))


def extract_arrays_from_inca_nc(path_to_rainfall_nc: str, path_to_other_parameters_nc: str) -> tuple:
    """Extracts arrays from INCA NetCDF files"""
    with nc.Dataset(path_to_rainfall_nc, 'r') as nc_rainfall, nc.Dataset(path_to_other_parameters_nc, 'r') as nc_inca_param:
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

        return ffmc_data, lon, lat


def calculate_date_of_interest_24h_before(date_of_interest: str) -> str:
    """Calculates date 24 hours before the date of interest"""
    return (pd.to_datetime(date_of_interest, format='%Y-%m-%dT%H:%M') - pd.Timedelta(hours=24)).isoformat()


def create_ffmc_layer_paths(paths: dict, date_str_for_file_name: str) -> tuple:
    """Creates paths to intermediate and final FFMC layers"""
    path_to_intermediate_ffmc_layer = paths["ffmc"]["intermediate"] + \
        f"_{date_str_for_file_name}.tif"
    path_to_ffmc_layer = paths["ffmc"]["final"] + \
        f"_{date_str_for_file_name}.tif"
    return path_to_intermediate_ffmc_layer, path_to_ffmc_layer


def create_ffmc_layer(paths: dict, date_of_interest: str, bbox: List[float]) -> None:
    """Creates FFMC layer aligned with reference grid"""
    date_of_interest_24h_before = calculate_date_of_interest_24h_before(
        date_of_interest)
    date_str_for_file_name = date_of_interest.split("T")[0].replace("-", "")

    # Create paths to intermediate and final FFMC layers
    path_to_intermediate_ffmc_layer, path_to_ffmc_layer = create_ffmc_layer_paths(
        date_str_for_file_name)

    # Retrieve data from geosphere API
    path_to_rain_netcdf = get_geosphere_data(
        PARAMETER_RAINFALL, date_of_interest_24h_before, date_of_interest, bbox_to_str(bbox), paths["ffmc"]["source"])
    path_to_inca_other_netcdf = get_geosphere_data(
        PARAMETERS_OTHER, date_of_interest_24h_before, date_of_interest, bbox_to_str(bbox), paths["ffmc"]["source"])

    # Extract FFMC, longitude, and latitude numpy arrays
    ffmc_arr, lon_arr, lat_arr = extract_arrays_from_inca_nc(
        path_to_rain_netcdf, path_to_inca_other_netcdf)

    # Create GeoTIFF file from numpy arrays
    gdal_create_geotiff_from_nc(
        ffmc_arr, lon_arr, lat_arr, path_to_intermediate_ffmc_layer)

    # Align and resample to reference grid
    gdal_align_and_resample(path_to_intermediate_ffmc_layer, path_to_ffmc_layer,
                            paths["reference_grid"]["raster"], RESAMPLE_ALGORITHM, 0)


def main():
    parser = argparse.ArgumentParser(description='Process FFMC data.')
    parser.add_argument('date_of_interest', type=str,
                        help='Date of interest in format "YYYY-MM-DDTHH:MM"')

    args = parser.parse_args()

    date_of_interest = args.date_of_interest

    # Load paths from the YAML file
    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)

    # TODO: In production, implement functionality to check if FFMC layer from the previous day is available; otherwise, use the initial value.
    create_ffmc_layer(paths, date_of_interest, BBOX_AUSTRIA)


if __name__ == "__main__":
    main()
