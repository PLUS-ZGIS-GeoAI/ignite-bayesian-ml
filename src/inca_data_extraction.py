import os
import requests
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


# TODO rewrite function to support multiple paramters and multiple locations

def get_geosphere_data_points(parameter: str, date_of_interest: str,
                              hours: int, coordinates: tuple, output_format: str = "geojson") -> float:
    """gets sum of specific inca paramter over specific time range and at a specific location 

    Args:
        parameter (str): inca parameter abbreviation (e.g. RR, T2M, RH2M, UU, VV, ...)
        date_of_interest (str): date of interest in following format '%Y-%m-%dT%H:%M'
        hours (int): start date is calculated by substracting hours from date of interest
        coordinates (tuple): (Latitude, Longitude)
        output_format (str, optional): Format of output file. Defaults to "geojson".

    Returns:
        float: sum of parameter at location over time range
    """

    start_time = calculate_date_of_interest_x_hours_before(
        date_of_interest, hours)

    url = f'{GEOSPHERE_INCA_TS_URL}?parameters={parameter}&start={start_time}&end={date_of_interest}&lat_lon={coordinates[0]},{coordinates[1]}&output_format={output_format}'

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        param_sum = np.sum(data["features"][0]["properties"]
                           ["parameters"][parameter]["data"])
        return param_sum

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
