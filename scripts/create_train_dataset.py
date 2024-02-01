import os
import numpy as np
import rasterio
import geopandas as gpd

from config.config import BASE_PATH, PATH_TO_PATH_CONFIG_FILE
from src.utils import load_paths_from_yaml, replace_base_path


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

    event_data = gpd.read_file(paths["fire_events"]["final"])

    # add all static features to training data
    for feature_name, rel_feature_layer_path in FEATURE_INFO:
        path_to_feature_layer = os.path.join(BASE_PATH, rel_feature_layer_path)
        event_data = add_feature_from_raster(
            event_data, path_to_feature_layer, feature_name)

    # add FFMC values to training data
    # calculate_ffmc_for_specific_locations()

    print(event_data.head())


if __name__ == "__main__":
    main()
