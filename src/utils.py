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


# TODO delete when new function is validated
'''
def create_polygon_density_layer_vector(polygon_layer: gpd.GeoDataFrame, ref_grid_vector: gpd.GeoDataFrame, path_to_polygon_density_vector_layer: str) -> None:
    """Creates a GeoTIFF file storing the area (im m2) of intersecting polygons of each cell.

    Args:
        polygon_layer (gpd.GeoDataFrame): Vector layer containing polygons.
        ref_grid_vector (gpd.GeoDataFrame): Vectorized reference grid (each polygon represents a cell).
        path_to_polygon_density_vector_layer (str): Directory and name of the polygon density layer as shape file.
    """

    # Intersect ref grid vector with road layer
    ref_raster_polygon_overlay = gpd.overlay(polygon_layer, ref_grid_vector)

    # Calculate length of road segment in each cell
    ref_raster_polygon_overlay["area"] = ref_raster_polygon_overlay.geometry.area
    polygon_area_per_cell = ref_raster_polygon_overlay.groupby(
        by="index").agg({"area": "sum"}).reset_index()

    # Merge road length information and ref grid
    polygon_density_layer = ref_grid_vector.merge(
        polygon_area_per_cell, on="index", how="left")

    # drop all rows which no intersection to farmyards
    polygon_density_layer_no_nan = polygon_density_layer.dropna()

    # save vector layer
    polygon_density_layer_no_nan.to_file(path_to_polygon_density_vector_layer)


def create_road_density_layer(road_layer: gpd.GeoDataFrame, ref_grid_vector: gpd.GeoDataFrame,  path_to_road_density_vector_layer: str) -> None:
    """Creates a GeoTIFF file storing the length (in meters) of intersecting roads for each cell.

    Args:
        road_layer (gpd.GeoDataFrame): Vector layer of road segments.
        ref_grid_vector (gpd.GeoDataFrame): Vectorized reference grid (each polygon represents a cell).
        path_to_polygon_density_vector_layer (str): Directory and name of the road density layer as shape file.
    """

    # Intersect ref grid vector with road layer
    ref_raster_road_overlay = gpd.overlay(road_layer, ref_grid_vector)

    # Calculate length of road segment in each cell
    ref_raster_road_overlay["length"] = ref_raster_road_overlay.geometry.length
    road_len_per_cell = ref_raster_road_overlay.groupby(
        by="index").agg({"length": "sum"}).reset_index()

    # Merge road length information and ref grid
    road_density_layer = ref_grid_vector.merge(
        road_len_per_cell, on="index", how="left")

    # drop all rows which do not intersect rows
    road_density_layer_no_nan = road_density_layer.dropna()

    # save vector layer
    road_density_layer_no_nan.to_file(path_to_road_density_vector_layer)

'''
