import requests
import numpy as np
import os

from config.config import GEOSPHERE_INCA_GRID_URL


# TODO add doc strings
def get_geosphere_data(parameters, start_date, end_date, bbox, base_path_output, output_format='netcdf', filename_prefix='INCA_analysis'):

    # Convert parameters to a comma-separated string
    parameters_str = '&'.join([f'parameters={param}' for param in parameters])

    # Build the URL with the provided parameters
    url = f"{GEOSPHERE_INCA_GRID_URL}?{parameters_str}&start={start_date}&end={end_date}&bbox={bbox}&output_format={output_format}"

    # Generate a filename based on the parameters and dates
    parameter_string_for_url = ""
    for a in parameters:
        parameter_string_for_url += f"_{a}"

    filename = f"{filename_prefix}_{parameter_string_for_url[1:]}_{start_date.replace(':', '').replace('-', '').replace('T', '_')}_{end_date.replace(':', '').replace('-', '').replace('T', '_')}.{output_format}"

    # Make the request
    response = requests.get(url)

    if response.status_code == 200:
        # Save the response content to a file
        path_to_file = os.path.join(base_path_output, filename)
        with open(path_to_file, 'wb') as file:
            file.write(response.content)
        print(f"Data saved to {filename}")
        return path_to_file
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def calculate_wind_speed(uu: float, vv: float):
    "calculates wind speed from u and v component"
    return np.sqrt(uu**2 + vv**2)
