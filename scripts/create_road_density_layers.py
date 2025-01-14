import geopandas as gpd

from src.utils import load_paths_from_yaml, replace_base_path
from config.config import PROJECT_EPSG, BASE_PATH, PATH_TO_PATH_CONFIG_FILE
from src.gdal_wrapper import gdal_rasterize_vector_layer
from src.data_preprocessing.static_layers_preprocessing import create_density_layer_vector, calculate_length

# This is the name of the column of the vecctor layer that creates the feature value (e.g. road density)
ATTRIBUTE_NAME = "density"


def create_road_density_layer(roads_data: gpd.GeoDataFrame,
                              ref_grid_vector: gpd.GeoDataFrame,
                              road_types: list,
                              attribute_name: str,
                              path_to_density_layer_vector: str,
                              path_to_raster_output: str,
                              path_to_ref_grid: str):

    road_gdf_selected = roads_data[roads_data.fclass.isin(road_types)]

    create_density_layer_vector(
        road_gdf_selected, ref_grid_vector,
        path_to_density_layer_vector, calculate_length, attribute_name
    )

    layer_name = path_to_density_layer_vector.split("/")[-1].split(".")[0]

    gdal_rasterize_vector_layer(
        path_to_density_layer_vector,
        path_to_raster_output, path_to_ref_grid, layer_name, attribute_name)


def main():

    paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
    paths = replace_base_path(paths, BASE_PATH)

    ref_grid_vector = gpd.read_file(paths["reference_grid"]["vector"])
    ref_grid_vector.reset_index(inplace=True)
    ref_grid_vector = ref_grid_vector.to_crs(PROJECT_EPSG)

    road_gdf = gpd.read_file(paths["roads"]["source"])
    road_gdf = road_gdf.to_crs(PROJECT_EPSG)
    railways_gdf = gpd.read_file(paths["railways"]["source"])
    railways_gdf = railways_gdf.to_crs(PROJECT_EPSG)

    path_to_ref_grid = paths["reference_grid"]["raster"]

    create_road_density_layer(road_gdf, ref_grid_vector,
                              ["track", "track_grade1", "track_grade2", "track_grade3",
                                  "track_grade4", "track_grade5"], ATTRIBUTE_NAME,
                              paths["roads"]["forestroads"]["intermediate"],
                              paths["roads"]["forestroads"]["final"], path_to_ref_grid)

    create_road_density_layer(road_gdf, ref_grid_vector, ["path"], ATTRIBUTE_NAME,
                              paths["roads"]["hikingtrails"]["intermediate"],
                              paths["roads"]["hikingtrails"]["final"], path_to_ref_grid)

    create_road_density_layer(railways_gdf, ref_grid_vector, ["rail"], ATTRIBUTE_NAME,
                              paths["railways"]["intermediate"],
                              paths["railways"]["final"], path_to_ref_grid)


if __name__ == "__main__":
    main()
