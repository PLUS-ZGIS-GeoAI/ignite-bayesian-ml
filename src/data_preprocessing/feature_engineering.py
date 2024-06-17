import os
import numpy as np
import rasterio
import pandas as pd
import geopandas as gpd


def add_static_feature_from_raster(
    events: gpd.GeoDataFrame, path_to_raster: str, feature_name: str
) -> gpd.GeoDataFrame:
    """Adds an additional column to GeoDataFrame with values of raster at same location as point geometries

    Args:
        path_to_raster (str): path to raster that contains certain feature values (e,g, farmyard density)
        feature_name (str): name of feature column in GeoDataFrame
        events (gpd.GeoDataFrame): GeoDataFrame containing the date and location of the fire and non-fire events

    Returns:
        pd.DataFrame: fire and non-fire events with new column for feature values
    """

    with rasterio.open(path_to_raster) as src:
        coords = list(zip(events.geometry.x, events.geometry.y))
        events_updated = events.copy()
        events_updated[feature_name] = [x[0] for x in src.sample(coords)]

        events_updated.loc[
            events_updated[feature_name] == src.profile["nodata"], feature_name
        ] = np.nan

    return gpd.GeoDataFrame(events_updated, geometry="geometry", crs="EPSG:31287")  # type: ignore


def get_nearest_pop_value(row) -> float:
    """choose population data from closest year

    Args:
        row (str): one row of dataframe

    Returns:
        float: population number per square km
    """
    year = pd.to_datetime(row.date).year
    nearest_year = min([2006, 2011, 2018, 2021], key=lambda x: abs(x - year))
    pop_col_name = f"pop_{nearest_year}"
    return row[pop_col_name]


def add_static_features(
    base_path: str, event_data: gpd.GeoDataFrame, feature_info: list
) -> gpd.GeoDataFrame:
    """adds static features from rasters to dataframe.

    Args:
        feature_info (list): Column names and paths to rasters are defined in feature_info list

    Returns:
        gpd.GeoDataFrame: dataframe with labels and static features
    """

    for feature_name, rel_feature_layer_path in feature_info:
        path_to_feature_layer = os.path.join(base_path, rel_feature_layer_path)
        event_data = add_static_feature_from_raster(
            event_data, path_to_feature_layer, feature_name
        )

    # creating population column, with population values closest to event data (drop others)
    event_data["pop_dens"] = event_data.apply(get_nearest_pop_value, axis=1)
    event_data = event_data.drop(
        ["pop_2006", "pop_2011", "pop_2018", "pop_2021"], axis=1
    )  # type: ignore

    return event_data


def add_ffmc_feature(
    event_data: gpd.GeoDataFrame, path_to_ffmc_data: str
) -> gpd.GeoDataFrame:
    """add column named ffmc to training dataframe

    Args:
        event_data (gpd.GeoDataFrame): dataframe containing at least a column called index (to identify which rows of event_data correspond to which inca_data rows)
        path_to_ffmc_data (str)

    Returns:
        (gpd.GeoDataFrame): event_data with additional column called ffmc, with epsg=31287
    """

    ffmc_df = pd.read_csv(path_to_ffmc_data)
    ffmc_event_df = pd.merge(
        event_data, ffmc_df.loc[:, ["X", "ffmc"]], left_on="index", right_on="X"
    )
    ffmc_event_df.drop(columns=["X"], inplace=True)
    return ffmc_event_df  # type: ignore
