import os
import requests
import json
import numpy as np

from config.config import GEOSPHERE_INCA_GRID_URL, GEOSPHERE_INCA_TS_URL
from src.utils import calculate_date_of_interest_x_hours_before


def get_geosphere_data_grid(parameters: list, start_date: str, end_date: str, bbox: list,
                            base_path_output: str, output_format='netcdf', filename_prefix='INCA_analysis') -> str:
    """gets inca data for specified time rang and bounding box from Geosphere API

    Args:
        parameters (list): inca parameter abbreviation (e.g. RR, T2M, RH2M, UU, VV, ...)
        start_date (str): _description_
        end_date (str): _description_
        bbox (list): _description_
        base_path_output (str): _description_
        output_format (str, optional): Defaults to 'netcdf'.
        filename_prefix (str, optional): Defaults to 'INCA_analysis'.

    Returns:
        str: path to netcdf file is returned if request successfull, otherwise None
    """

    parameters_str = '&'.join([f'parameters={param}' for param in parameters])
    url = f"{GEOSPHERE_INCA_GRID_URL}?{parameters_str}&start={start_date}&end={end_date}&bbox={bbox}&output_format={output_format}"

    parameter_string_for_url = ""
    for a in parameters:
        parameter_string_for_url += f"_{a}"

    filename = f"{filename_prefix}_{parameter_string_for_url[1:]}_{start_date.replace(':', '').replace('-', '').replace('T', '_')}_{end_date.replace(':', '').replace('-', '').replace('T', '_')}.{output_format}"

    response = requests.get(url)

    if response.status_code == 200:
        path_to_file = os.path.join(base_path_output, filename)
        with open(path_to_file, 'wb') as file:
            file.write(response.content)
        print(f"Data saved to {filename}")
        return path_to_file
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def get_geosphere_data_point(parameters: list,
                             start_date: str,
                             end_date: str,
                             lon: float,
                             lat: float,
                             output_format: str = "geojson") -> dict:
    """gets inca parameters data at a specific location and timerange from Geosphere Data API

    Args:
        parameters (list): Inca parameters of interest. E.g. ["T2M", "RR"].
        start_date (str): Start of daterange for data retrieval. E.g. '2021-08-01T00:00'.
        end_date (str): End of daterange for data retrieval. E.g. '2021-08-01T00:00'.
        lat_lon (list, optional): _description_. Defaults to ['48.206248, 16.367569'].
        output_format (str, optional): Output format. Defaults to "geojson".

    Returns (dict): response from Geosphere API
    """

    lat_lon = [f"{lat}, {lon}"]
    lat_lon_params = '&lat_lon='.join(lat_lon)

    parameter_string_for_url = ""
    for a in parameters:
        parameter_string_for_url += f"parameters={a}&"

    url = f'{GEOSPHERE_INCA_TS_URL}?{parameter_string_for_url[:-1]}&start={start_date}&end={end_date}&lat_lon={lat_lon_params}&output_format={output_format}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f'Request failed with status code {response.status_code}.')


def calculate_wind_speed(uu: float, vv: float) -> float:
    """calculates wind speed from uu and vv components

    # TODO check what is uu and vv component and what unit is calculated wind speed
    Args:
        uu (float): uu component
        vv (float): vv component

    Returns:
        float: wind speed in xxx
    """
    "calculates wind speed from u and v component"
    return np.sqrt(uu**2 + vv**2)
