import geopandas as gpd


def create_density_layer_vector(input_layer: gpd.GeoDataFrame, ref_grid_vector: gpd.GeoDataFrame, path_to_density_vector_layer: str, density_function):
    """Creates a vector layer storing the density of intersecting features for each cell.

    Args:
        input_layer (gpd.GeoDataFrame): Vector layer containing features.
        ref_grid_vector (gpd.GeoDataFrame): Vectorized reference grid (each polygon represents a cell).
        path_to_density_vector_layer (str): Directory and name of the density layer as shapefile.
        density_function (function): Function to calculate density from intersecting features.
    """

    # Intersect ref grid vector with input layer
    ref_raster_overlay = gpd.overlay(input_layer, ref_grid_vector)

    # Calculate density of features in each cell
    ref_raster_overlay["density"] = density_function(ref_raster_overlay)

    # Group by and aggregate to get density per cell
    density_per_cell = ref_raster_overlay.groupby(
        by="index").agg({"density": "sum"}).reset_index()

    # Merge density information and ref grid
    density_layer = ref_grid_vector.merge(
        density_per_cell, on="index", how="left")

    # Drop all rows with no intersection
    density_layer_no_nan = density_layer.dropna()

    # Save vector layer
    density_layer_no_nan.to_file(path_to_density_vector_layer)


def calculate_area(feature_overlay):
    """Calculate the area of intersecting features."""
    return feature_overlay.geometry.area


def calculate_length(feature_overlay):
    """Calculate the length of intersecting features."""
    return feature_overlay.geometry.length
