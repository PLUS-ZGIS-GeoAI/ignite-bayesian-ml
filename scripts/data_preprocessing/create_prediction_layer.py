import rasterio

from config.config import BASE_PATH, PATH_TO_PATH_CONFIG_FILE
from src.utils import load_paths_from_yaml, replace_base_path


if __name__ == "__main__":

    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)

    static_features_info = [
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
