import os
import numpy as np
import rasterio
import geopandas as gpd

from config.config import BASE_PATH


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


def calculate_ffmc_for_specific_locations():
    pass


if __name__ == "__main__":

    path_to_fire_events = os.path.join(
        BASE_PATH, "data/processed/fire_data/fire_data.shp")

    FEATURE_INFO = [
        ("pop_2006", "data/proceseed/population_data/geostat_2006_resampled_Average.tif"),
        ("pop_2011", "data/proceseed/population_data/geostat_2011_resampled_Average.tif"),
        ("pop_2018", "data/proceseed/population_data/geostat_2018_resampled_Average.tif"),
        ("pop_2021", "data/proceseed/population_data/geostat_2021_resampled_Average.tif"),
        ("farmyard_density", "data/processed/farmyard_density_layer/farmyard_density.tif"),
        ("hinkingtrail_density",
         "data/processed/road_density_layers/hikingtrail_density.tif"),
        ("forestroad_density", "data/processed/road_density_layers/forestroad_density.tif")
        ("railway_density", "data/processed/road_density_layers/railway_density.tif"),
        ("elevation", "data/processed/topographical_data/elevation_resampled_Average.tif"),
        ("slope", "data/processed/topographical_data/slope_resampled_Average.tif"),
        ("aspect", "data/processed/topographical_data/aspect_resampled_Average.tif"),
        ("forest_type", "data/processed/forest_type/tree_type_resampled_mode.tif")

    ]

    event_data = gpd.read_file(path_to_fire_events)

    # add all static features to training data
    for feature_name, rel_feature_layer_path in FEATURE_INFO:
        path_to_feature_layer = os.path.join(BASE_PATH, rel_feature_layer_path)
        event_data = add_feature_from_raster(
            event_data, path_to_feature_layer, feature_name)

    # add FFMC values to training data
    calculate_ffmc_for_specific_locations()
