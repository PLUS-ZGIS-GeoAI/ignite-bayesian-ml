"""
The goal of the script is to create a training dataset for wildfire igntiion prediction,
utilizing the static feature layers and the ffmc.
"""

import geopandas as gpd

from config.config import BASE_PATH, PATH_TO_PATH_CONFIG_FILE
from src.data_preprocessing.feature_engineering import (
    add_static_features,
    add_ffmc_feature,
)
from src.utils import load_paths_from_yaml, replace_base_path


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
        ("foresttype", paths["forest_type"]["final"]),
        ("canopy_cover", paths["canopy_cover"]["final"]),
    ]

    train_data = add_static_features(BASE_PATH, event_data, feature_info)
    train_data = add_ffmc_feature(train_data, paths["ffmc_events"]["source"])

    train_data.to_file(paths["training_data"])


if __name__ == "__main__":
    main()
