import os
import numpy as np
from datetime import datetime
import rasterio
import geopandas as gpd

from config.config import BASE_PATH, PATH_TO_PATH_CONFIG_FILE
from src.utils import load_paths_from_yaml, replace_base_path
from src.inca_data_extraction import get_geosphere_data_points, calculate_wind_speed
from src.fwi_system_calculator import calculate_ffmc


def add_feature_from_raster(events: gpd.GeoDataFrame, path_to_raster: str, feature_name: str) -> gpd.GeoDataFrame:
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
        coords = [(x, y) for x, y in zip(events.geometry.x, events.geometry.y)]
        events_updated = events.copy()
        events_updated[feature_name] = [x[0] for x in src.sample(coords)]

        events_updated.loc[events_updated[feature_name] ==
                           src.profile["nodata"], feature_name] = np.nan
    return events_updated


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

    FEATURE_INFO = [
        ("pop_2006", paths["population_layers"]["2006"]["final"]),
        ("pop_2011", paths["population_layers"]["2011"]["final"]),
        ("pop_2018", paths["population_layers"]["2018"]["final"]),
        ("pop_2021", paths["population_layers"]["2021"]["final"]),
        ("farmyard_density", paths["farmyard_density"]["final"]),
        ("hinkingtrail_density", paths["roads"]["hikingtrails"]["final"]),
        ("forestroad_density", paths["roads"]["forestroads"]["final"]),
        ("railway_density", paths["railways"]["final"]),
        ("elevation", paths["topographical_layers"]["elevation"]["final"]),
        ("slope", paths["topographical_layers"]["slope"]["final"]),
        ("aspect", paths["topographical_layers"]["aspect"]["final"]),
        ("forest_type", paths["forest_type"]["final"])
    ]

    def transform_date(input_date):
        """transforms date from "%m/%d/%Y" into '%Y-%m-%dT12:00' format"""
        date_object = datetime.strptime(input_date, "%m/%d/%Y")
        output_date = date_object.strftime('%Y-%m-%dT12:00')
        return str(output_date)

    # read in data
    # FIXME use only subset of data - as Geosphere API only provides values up 2011/2012
    event_data = gpd.read_file(paths["fire_events"]["final"])
    event_data = event_data[event_data["year"].astype(
        "int") >= 2012].sample(5)

    # convert datetime format
    event_data["date"] = event_data["date"].apply(
        lambda x: transform_date(x))

    # convert binary fire column to integer
    event_data.fire = event_data.fire.astype("int8")

    # add all static features to training data
    for feature_name, rel_feature_layer_path in FEATURE_INFO:
        path_to_feature_layer = os.path.join(BASE_PATH, rel_feature_layer_path)
        event_data = add_feature_from_raster(
            event_data, path_to_feature_layer, feature_name)

    # add ffmc feature
    event_data = add_ffmc_feature(event_data)

    print(event_data.head())


if __name__ == "__main__":
    main()
