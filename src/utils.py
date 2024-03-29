import yaml
import geopandas as gpd


def load_paths_from_yaml(yaml_file_path):
    """import paths from yaml file."""
    with open(yaml_file_path, 'r') as file:
        paths_data = yaml.safe_load(file)
    return paths_data


def replace_base_path(data, base_path):
    """Replace '{base_path}' placeholders with the actual base_path."""
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = replace_base_path(value, base_path)
    elif isinstance(data, str):
        data = data.format(base_path=base_path)
    elif isinstance(data, list):
        data = [replace_base_path(item, base_path) for item in data]
    return data


def add_static_feature_from_raster(events: gpd.GeoDataFrame,
                                   path_to_raster: str, feature_name: str) -> gpd.GeoDataFrame:
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

        events_updated.loc[events_updated[feature_name] ==
                           src.profile["nodata"], feature_name] = np.nan

    return gpd.GeoDataFrame(
        events_updated, geometry="geometry", crs="EPSG:31287")  # type: ignore