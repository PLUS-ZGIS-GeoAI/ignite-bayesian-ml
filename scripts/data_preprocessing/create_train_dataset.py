'''
The goal of the script is to create a training dataset for wildfire igntiion prediction, 
utilizing the static feature layers and the ffmc.
'''

import os
from datetime import datetime
import numpy as np
import rasterio
import pandas as pd
import geopandas as gpd

from config.config import BASE_PATH, PATH_TO_PATH_CONFIG_FILE
from src.utils import load_paths_from_yaml, replace_base_path
from src.inca_data_extraction import get_geosphere_data_points, calculate_wind_speed
from src.fwi_system_calculator import calculate_ffmc


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


def add_ffmc_feature(events: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """adds a column called FFMC, which contains the Fine Fuel Moisture Code, calculated from Rain, Temp, Humidity and Wind Speed, retrieved from Geosphere API

    Args:
        events (gpd.GeoDataFrame): GeoDataFrame containing the date and location of the fire and non-fire events

    Returns:
        gpd.GeoDataFrame: fire and non-fire events with new column for feature values
    """

    data_copy = events.copy()
    data_copy.to_crs("EPSG:4326", inplace=True)

    data_copy["UU"] = data_copy.apply(lambda row:  get_geosphere_data_points(
        "UU", row["date"], 0, (row["geometry"].y, row["geometry"].x)), axis=1)
    data_copy["VV"] = data_copy.apply(lambda row:  get_geosphere_data_points(
        "VV", row["date"], 0, (row["geometry"].y, row["geometry"].x)), axis=1)
    data_copy["T2M"] = data_copy.apply(lambda row:  get_geosphere_data_points(
        "T2M", row["date"], 0, (row["geometry"].y, row["geometry"].x)), axis=1)
    data_copy["RH2M"] = data_copy.apply(lambda row:  get_geosphere_data_points(
        "RH2M", row["date"], 0, (row["geometry"].y, row["geometry"].x)), axis=1)
    data_copy["RR"] = data_copy.apply(lambda row:  get_geosphere_data_points(
        "RR", row["date"], 24, (row["geometry"].y, row["geometry"].x)), axis=1)
    data_copy["windspeed"] = data_copy.apply(
        lambda row: calculate_wind_speed(row["UU"], row["VV"]), axis=1)
    data_copy["ffmc"] = data_copy.apply(lambda row:  calculate_ffmc(
        85, row["RH2M"], row["T2M"], row["RR"], row["windspeed"]), axis=1)

    events["ffmc"] = data_copy["ffmc"]
    return events


def main():

    # Load paths from the YAML file
    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)

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

    def transform_date(input_date):
        """transforms date from "%m/%d/%Y" into '%Y-%m-%dT12:00' format"""
        date_object = datetime.strptime(input_date, "%m/%d/%Y")
        output_date = date_object.strftime('%Y-%m-%dT12:00')
        return str(output_date)

    # FIXME use only subset of data - as Geosphere API only provides values up 2011/2012
    event_data = gpd.read_file(paths["fire_events"]["final"])
    event_data = event_data[event_data["year"].astype("int") >= 2012]
    # this date conversion is neccessary so that get_geosphere_data_points can be applied to the dataframe
    event_data["date"] = event_data["date"].apply(transform_date)

    event_data = add_static_features(event_data, feature_info)
    event_data = add_ffmc_feature(event_data)

    event_data.to_file(paths["training_data"]["subset"])


if __name__ == "__main__":
    main()
