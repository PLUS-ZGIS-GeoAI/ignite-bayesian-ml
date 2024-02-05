'''
The goal of the script is to create a training dataset for wildfire igntiion prediction, 
utilizing the static feature layers and the ffmc.
'''

import os
import re
import json
import numpy as np
import rasterio
import shapely
import pandas as pd
import geopandas as gpd

from config.config import BASE_PATH, PATH_TO_PATH_CONFIG_FILE
from src.utils import load_paths_from_yaml, replace_base_path
from src.data_preprocessing.inca_data_preprocessing import calculate_wind_speed, calculate_ffmc


INITIAL_FFMC_VALUE = 85


def add_static_feature_from_raster(events: gpd.GeoDataFrame,
                                   path_to_raster: str, feature_name: str) -> gpd.GeoDataFrame:
    """Adds an additional column to GeoDataFrame with values of raster at same location as point geometries

    Args:
        path_to_raster (str): path to raster that contains certain feature values (e,g, farmyard density)
        feature_name (str): name of feature column in GeoDataFrame
        events (gpd.GeoDataFrame): GeoDataFrame containing the date and location of the fire and non-fire events

    Returns:
        gpd.GeoDataFrame: fire and non-fire events with new column for feature values
    """

    with rasterio.open(path_to_raster) as src:
        events_updated = events.copy()
        coords = list(zip(events.geometry.x, events.geometry.y))
        events_updated = events.copy()
        events_updated[feature_name] = [x[0] for x in src.sample(coords)]

        events_updated.loc[events_updated[feature_name] ==
                           src.profile["nodata"], feature_name] = np.nan
    return events_updated


def get_nearest_pop_value(row) -> float:
    """choose population data from closest year

    Args:
        row (str): one row of dataframe

    Returns:
        float: population number per square km
    """
    year = pd.to_datetime(row.date).year
    nearest_year = min([2006, 2011, 2018, 2021], key=lambda x: abs(x-year))
    pop_col_name = f"pop_{nearest_year}"
    return row[pop_col_name]


def add_static_features(event_data: gpd.GeoDataFrame, feature_info: dict) -> gpd.GeoDataFrame:
    """adds static features from rasters to dataframe. 

    Args:
        feature_info (dict): Column names and paths to rasters are defined in feature_info dict

    Returns:
        gpd.GeoDataFrame: dataframe with labels and static features
    """

    for feature_name, rel_feature_layer_path in feature_info:
        path_to_feature_layer = os.path.join(BASE_PATH, rel_feature_layer_path)
        event_data = add_static_feature_from_raster(
            event_data, path_to_feature_layer, feature_name)

    # creating population column, with population values closest to event data (drop others)
    event_data['pop_dens'] = event_data.apply(
        get_nearest_pop_value, axis=1)
    event_data = event_data.drop(
        ["pop_2006", "pop_2011", "pop_2018", "pop_2021"], axis=1)

    return event_data


def convert_inca_data_from_json_to_dataframe(path_to_inca_data: str) -> gpd.GeoDataFrame:
    """Convert the raw inca data, retrieved from Geosphere Data API to GeoDataFrame. 
    For rainfall the sum of full time range is calculated. For the other parameters only the last value is taken. 

    Args:
        path_to_inca_data (str): Path to raw inca data

    Returns:
        gpd.GeoDataFrame: GeoDataFrame with epsg:4326
    """

    data_list = []

    with open(path_to_inca_data, 'r') as file:
        for line in file:
            # Use regular expression to extract ID and JSON content
            match = re.match(r'(\d+)(\{.+})', line)
            if match:
                numeric_id = int(match.group(1))
                json_data = json.loads(match.group(2))

                last_timestamp = json_data["timestamps"][-1]
                last_T2M = json_data["features"][0]["properties"]["parameters"]["T2M"]["data"][-1]
                last_RH2M = json_data["features"][0]["properties"]["parameters"]["RH2M"]["data"][-1]
                last_UU = json_data["features"][0]["properties"]["parameters"]["UU"]["data"][-1]
                last_VV = json_data["features"][0]["properties"]["parameters"]["VV"]["data"][-1]

                # Chechking for None values here is neccessary - because None's appear in RR
                rr_data = json_data["features"][0]["properties"]["parameters"]["RR"]["data"]
                if any(val is None for val in rr_data):
                    sum_RR = None
                else:
                    sum_RR = np.sum(rr_data)

                coordinates = json_data["features"][0]["geometry"]["coordinates"]
                point = shapely.Point(coordinates)

                data_list.append({
                    "ID": numeric_id,
                    "Timestamp": last_timestamp,
                    "T2M": last_T2M,
                    "RH2M": last_RH2M,
                    "UU": last_UU,
                    "VV": last_VV,
                    "RR_sum_24h": sum_RR,
                    "geometry": point
                })

    gdf = gpd.GeoDataFrame(data_list, geometry='geometry', crs="EPSG:4326")
    return gdf


def add_ffmc_feature(event_data: gpd.GeoDataFrame, path_to_inca_data: str) -> gpd.GeoDataFrame:
    """add column named ffmc to training dataframe

    Args:
        event_data (gpd.GeoDataFrame): dataframe containing at least a column called index (to identify which rows of event_data correspond to which inca_data rows)
        path_to_inca_data (str): path to file with raw inca data

    Returns:
        (gpd.GeoDataFrame): event_data with additional column called ffmc, with epsg=31287
    """

    inca_data_gdf = convert_inca_data_from_json_to_dataframe(path_to_inca_data)
    inca_data_gdf.dropna(inplace=True)

    inca_data_gdf["windspeed"] = inca_data_gdf.apply(
        lambda row: calculate_wind_speed(row["UU"], row["VV"]), axis=1)
    inca_data_gdf["ffmc"] = inca_data_gdf.apply(lambda row:  calculate_ffmc(
        INITIAL_FFMC_VALUE, row["RH2M"], row["T2M"], row["RR_sum_24h"], row["windspeed"]), axis=1)

    train_data = pd.merge(event_data, inca_data_gdf,
                          left_on="index", right_on="ID")
    train_data = train_data.loc[:, [
        "date", "Pufferradi", "fire", "ffmc", "geometry_x"]]
    train_data.rename(columns={"geometry_x": "geometry"}, inplace=True)

    return gpd.GeoDataFrame(
        train_data, geometry="geometry", crs="EPSG:31287")


def main():

    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)

    event_data = gpd.read_file(paths["fire_events"]["final"])
    event_data.reset_index(inplace=True)

    feature_info = [
        ("pop_2006", paths["population_layers"]["2006"]["final"]),
        ("pop_2011", paths["population_layers"]["2011"]["final"]),
        ("pop_2018", paths["population_layers"]["2018"]["final"]),
        ("pop_2021", paths["population_layers"]["2021"]["final"]),
        ("farmyard_ds", paths["farmyard_density"]["final"]),
        ("hiking_ds", paths["roads"]["hikingtrails"]["final"]),
        ("forest_ds", paths["roads"]["forestroads"]["final"]),
        ("rail_dens", paths["railways"]["final"]),
        ("elevation", paths["topographical_layers"]["elevation"]["final"]),
        ("slope", paths["topographical_layers"]["slope"]["final"]),
        ("aspect", paths["topographical_layers"]["aspect"]["final"]),
        ("foresttype", paths["forest_type"]["final"])
    ]

    train_data = add_static_features(event_data, feature_info)
    train_data = add_ffmc_feature(train_data)
    train_data.to_file(paths["training_data"]["subset"])


if __name__ == "__main__":
    main()
