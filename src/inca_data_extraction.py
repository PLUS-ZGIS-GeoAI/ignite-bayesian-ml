import sys
import requests
import numpy as np
import pandas as pd
import json


def get_inca_data(parameter: list,
                  start_date: str,
                  end_date: str,
                  bbox: list,
                  output_format: str = "geojson") -> dict:
    """retrieves hourly inca data from Geosphere within bounding box for defined time range

    Args:
        parameter (list, optional): weather parameter. Choose between [T2M, RH2M, UU, VV, RR]. 
        start_date (_type_, optional): Start date. Must be in format 'YYY-MM-DDTHH:MM'
        end_date (_type_, optional): End data. Must be in format 'YYY-MM-DDTHH:MM'
        bbox (list, optional): Bounding Box. E.g. [47.45, 14.05, 47.50, 14.10].
        output_format (str, optional): Output format of response. Defaults to "geojson".

    Returns:
        dict: Data Values and coordinates in json format, converted to python dictionary
    """

    base_url = "https://dataset.api.hub.geosphere.at/v1/grid/historical/inca-v1-1h-1km"

    # Constructing the URL with parameters
    url = f"{base_url}?parameters={parameter}&start={start_date}&end={end_date}&bbox={','.join(map(str, bbox))}&output_format={output_format}"

    try:
        # Making the HTTP request
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad responses (4xx and 5xx)

        # Returning the data as text
        return json.loads(response.text)

    except requests.exceptions.RequestException as e:
        # Handling any exceptions that may occur during the request
        print(f"Error: {e}")
        return None


def extract_inca_data(data: dict, parameter_name: str) -> pd.DataFrame:
    """
    Extracts data from a given dictionary in the INCA format and creates a DataFrame.

    Parameters:
    - data (dict): The input dictionary in the INCA format.
    - parameter_name (str): The parameter name for which data is to be extracted.

    Returns:
    - pd.DataFrame: A DataFrame containing lon, lat, and the specified parameter data.
    """

    # Initialize an empty dictionary for data preparation
    data_prep = {"lon": [], "lat": [], parameter_name: []}

    # Iterate over features in the input data
    for row in data.get("features", []):
        # Extract lon and lat from geometry coordinates
        lon, lat = row["geometry"]["coordinates"][:2]

        # Extract the specified parameter data
        if parameter_name == "RR":
            data_agg = np.sum(
                row["properties"]["parameters"][parameter_name]["data"])
        else:
            data_agg = row["properties"]["parameters"][parameter_name]["data"][0]

        # Append data to the data_prep dictionary
        data_prep["lon"].append(lon)
        data_prep["lat"].append(lat)
        data_prep[parameter_name].append(data_agg)

    # Convert the data_prep dictionary to a DataFrame
    return pd.DataFrame(data_prep)


def calculate_wind_speed(uu: float, vv: float):
    "calculates wind speed from u and v component"
    return np.sqrt(uu**2 + vv**2)
