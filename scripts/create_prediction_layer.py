import pandas as pd
import cloudpickle
import joblib
import rasterio

from config.config import BASE_PATH, PATH_TO_PATH_CONFIG_FILE
from src.utils import load_paths_from_yaml, replace_base_path
from src.modeling.encodings import convert_aspect_to_cardinal_direction


def load_pymc_model(path_to_model: str):
    """loads pymc model and trace"""

    with open(path_to_model, 'rb') as buff:
        model_dict = cloudpickle.load(buff)
    idata = model_dict['idata']
    model = model_dict['model']
    return model, idata


def load_static_layers_into_df(feature_layers: list) -> pd.DataFrame:
    """loading all feature layers and saving as dataframe using the names stored in each tuple as column names

    Args:
        feature_layers (list): list of tuples with (layer_name, path_to_layer)

    Returns:
        pd.DataFrame: dataframe with features 
    """

    data = {}

    for name, path in feature_layers:
        with rasterio.open(path) as src:
            print(name)
            data[name] = src.read(1).flatten()

    return pd.DataFrame(data)


def data_preprocessing():
    pass


if __name__ == "__main__":

    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)
    path_to_blr_model = "models/blr_pickle.pkl"
    training_order_columns = ['ffmc', 'farmyard_density', 'hikingtrail_density', 'forestroad_density',
                              'railway_density', 'elevation', 'slope', 'population_density']

    feature_layers = [
        ("population_density", paths["population_layers"]["2021"]["final"]),
        ("farmyard_density", paths["farmyard_density"]["final"]),
        ("hikingtrail_density", paths["roads"]["hikingtrails"]["final"]),
        ("forestroad_density", paths["roads"]["forestroads"]["final"]),
        ("railway_density", paths["railways"]["final"]),
        ("elevation", paths["topographical_layers"]["elevation"]["final"]),
        ("slope", paths["topographical_layers"]["slope"]["final"]),
        ("aspect", paths["topographical_layers"]["aspect"]["final"]),
        ("forest_type", paths["forest_type"]["final"])
    ]

    blr_model, blr_idata = load_pymc_model(path_to_blr_model)
    features_df = load_static_layers_into_df(feature_layers)
    features_df["ffmc"] = 85

    features_df["aspect_encoded"] = features_df["aspect"].apply(
        convert_aspect_to_cardinal_direction)
    features_df["forest_type"].fillna(6, inplace=True)
    features_df["forest_type"] = features_df["forest_type"].astype(int)
    features_df_reordered = features_df[training_order_columns]

    preprocessor = joblib.load('models/blr_preprocessor.pkl')
    features_transformed = preprocessor.transform(features_df_reordered)

    features_transformed_df = pd.DataFrame(
        features_transformed, columns=training_order_columns)
    features_transformed_df["forest_type"] = features_df["forest_type"]
    features_transformed_df["aspect_encoded"] = features_df["aspect_encoded"]

    print(features_transformed_df.head())
