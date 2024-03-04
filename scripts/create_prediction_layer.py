import numpy as np
import pandas as pd
import geopandas as gpd
import cloudpickle
import joblib
import rasterio
from rasterio.features import geometry_mask
from shapely.geometry import shape

from config.config import BASE_PATH, PATH_TO_PATH_CONFIG_FILE
from src.utils import load_paths_from_yaml, replace_base_path
from src.modeling.encodings import convert_aspect_to_cardinal_direction
from src.modeling.predictions import BinaryClassification


def load_pymc_model(path_to_model: str):
    """loads pymc model and trace"""

    with open(path_to_model, 'rb') as buff:
        model_dict = cloudpickle.load(buff)
    idata = model_dict['idata']
    model = model_dict['model']
    return model, idata


def load_static_layers_into_df(feature_layers: list) -> pd.DataFrame:
    """loading all feature layers and saving as dataframe 
    using the names stored in each tuple as column names"""

    data = {}
    for name, path in feature_layers:
        with rasterio.open(path) as src:
            print(name)
            data[name] = src.read(1).flatten()
    return pd.DataFrame(data)


def add_ffmc_layer(features_df: pd.DataFrame, static_value=None) -> pd.DataFrame:
    """adds ffmc layer to features df - right now only placeholder function which assumes that ffmc is static for each cell"""

    if static_value:
        features_df["ffmc"] = static_value
    return features_df


def preprocess_data(path_to_preprocessor: str, features_df: pd.DataFrame):
    """apply preprocessing steps as done in model training"""

    training_order_columns = ['ffmc', 'farmyard_density', 'hikingtrail_density', 'forestroad_density',
                              'railway_density', 'elevation', 'slope', 'population_density']

    features_df["aspect_encoded"] = features_df["aspect"].apply(
        convert_aspect_to_cardinal_direction)
    #features_df["forest_type"].replace(-1, 6, inplace=True)
    features_df["forest_type"] = features_df["forest_type"].astype(int)
    features_df_reordered = features_df[training_order_columns]

    preprocessor = joblib.load(path_to_preprocessor)
    features_transformed = preprocessor.transform(features_df_reordered)

    features_transformed_df = pd.DataFrame(
        features_transformed, columns=training_order_columns)
    features_transformed_df["forest_type"] = features_df["forest_type"].values
    features_transformed_df["aspect_encoded"] = features_df["aspect_encoded"].values

    return features_transformed_df


def extract_ref_grid_ids_from_nuts_unit(path_to_nuts_data: str, path_to_ref_grid: str, nuts_code: str) -> np.array:
    """extract the ref grid ids of the teh cells which are inside the boundaries of a given nuts unit"""

    nuts_gdf = gpd.read_file(path_to_nuts_data)
    nuts_geom = nuts_gdf[nuts_gdf['NUTS_ID']
                         == nuts_code]['geometry'].values[0]

    with rasterio.open(path_to_ref_grid) as ref_grid_src:
        mask = geometry_mask([shape(nuts_geom)], out_shape=ref_grid_src.shape,
                             transform=ref_grid_src.transform, invert=True)
        data = ref_grid_src.read(1)
        ids_extract = data[mask]
    return ids_extract


def make_predictions(path_to_model: str, X_new: pd.DataFrame) -> pd.DataFrame:
    """use bayesian model to make predictions"""

    y_dummy = [0 for i in range(len(X_new))]
    X_new_blr = {
        "elevation": X_new.elevation,
        "slope": X_new.slope,
        "aspect": X_new.aspect_encoded,
        "forestroad_density": X_new.forestroad_density,
        "railway_density": X_new.railway_density,
        "hikingtrail_density": X_new.hikingtrail_density,
        "farmyard_density": X_new.farmyard_density,
        "population": X_new.population_density,
        "forest_type": X_new.forest_type,
        "ffmc": X_new.ffmc,
        "fire": y_dummy
    }

    model, idata = load_pymc_model(path_to_model)
    blr_prediction_obj = BinaryClassification(
        model, idata, X_new_blr, 0, "y_pred", "p")
    blr_prediction_obj.extend_trace()
    preds = blr_prediction_obj.predict()
    return preds


def create_prediction_layer(preds: pd.DataFrame, path_to_ref_grid: str, path_to_output: str):
        """from model predictions and reference grid, 
        create geotiff that stores p pred and hdi width for predicted cells"""

        with rasterio.open(path_to_ref_grid) as ref_grid_src:
            ref_grid_data = ref_grid_src.read(1)
            ref_grid_meta = ref_grid_src.profile

        prediction_layer = np.full_like(ref_grid_data, -1, dtype="float32")
        uncertainty_layer = np.full_like(ref_grid_data, -1, dtype="float32")

        indices = np.where(np.isin(ref_grid_data, preds['ref_grid_id'].values))

        prediction_layer[indices] = preds['p_pred']
        uncertainty_layer[indices] = preds['hdi_width']

        out_meta = ref_grid_meta
        out_meta.update({"nodata": -1, "dtype": "float32", "count": 2})  
        with rasterio.open(path_to_output, "w", **out_meta) as dst:
            dst.write(prediction_layer, 1)
            dst.write(uncertainty_layer, 2)


if __name__ == "__main__":

    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)

    nuts_code = "AT130"
    # TODO at later stage save those paths to paths config file
    path_to_blr_model = "models/blr_pickle.pkl"
    path_to_blr_preprocessor = "models/blr_preprocessor.pkl"
    path_to_prediction_layer = f"{BASE_PATH}/data/final/prediction_layers/pred_layer_{nuts_code}.geotiff"

    feature_layers = [
        ("ref_grid_id", paths["reference_grid"]["raster"]),
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

    features_df = load_static_layers_into_df(feature_layers)
    
    features_df = add_ffmc_layer(features_df, 65)
    
    ref_grid_ids_aoi = extract_ref_grid_ids_from_nuts_unit(
        paths["nuts_data"]["final"], paths["reference_grid"]["raster"], nuts_code)
    
    features_df_aoi = features_df[features_df["ref_grid_id"].isin(
        ref_grid_ids_aoi)]
    
    features_df_aoi = features_df_aoi[features_df_aoi["forest_type"] != -1]
    print(len(features_df_aoi))

    features_df_preproc = preprocess_data(
        path_to_blr_preprocessor, features_df_aoi)
    
    preds = make_predictions(path_to_blr_model, features_df_preproc)

    preds["ref_grid_id"] = features_df_aoi["ref_grid_id"].values
    
    create_prediction_layer(preds, paths["reference_grid"]["raster"], path_to_prediction_layer)

