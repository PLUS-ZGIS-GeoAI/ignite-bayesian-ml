import os
import geopandas as gpd

from config.config import PATH_TO_REF_RASTER, PROJECT_EPSG, PATH_TO_REF_GRID_VECTOR, PATH_TO_ROADS_DS, PATH_TO_RAILWAYS_DS, PATH_TO_FORESTROAD_DENSITY_LAYER, PATH_TO_HIKINGTRAIL_DENSITY_LAYER, PATH_TO_RAILWAY_DENSITY_LAYER, PATH_TO_FORESTROAD_DENSITY_VECTOR, PATH_TO_RAILWAY_DENSITY_VECTOR, PATH_TO_HIKINGTRAIL_DENSITY_VECTOR

from src.gdal_wrapper import gdal_rasterize_vector_layer
from src.utils import create_density_layer_vector, calculate_length


def create_road_density_layer(roads_data: gpd.GeoDataFrame,
                              ref_grid_vector: gpd.GeoDataFrame,
                              road_types: list,
                              attribute_name: str,
                              path_to_density_layer_vector: str,
                              path_to_raster_output: str):

    road_gdf_selected = roads_data[roads_data.fclass.isin(road_types)]

    # Create road density vector layer
    create_density_layer_vector(
        road_gdf_selected, ref_grid_vector, path_to_density_layer_vector, calculate_length, attribute_name
    )

    # extract layer name from path
    layer_name = path_to_density_layer_vector.split("/")[-1].split(".")[0]

    # Rasterize vector layer
    gdal_rasterize_vector_layer(
        path_to_density_layer_vector,
        path_to_raster_output, PATH_TO_REF_RASTER, layer_name, attribute_name)


if __name__ == "__main__":

    # This is the name of the column of the vecctor layer that creates the feature value (e.g. road density)
    attribute_name = "density"

    # read in vectorized reference grid and reset index
    ref_grid_vector = gpd.read_file(PATH_TO_REF_GRID_VECTOR)
    ref_grid_vector.reset_index(inplace=True)
    ref_grid_vector = ref_grid_vector.to_crs(PROJECT_EPSG)

    # read in osm road data and reproject to project projection
    road_gdf = gpd.read_file(PATH_TO_ROADS_DS)
    road_gdf = road_gdf.to_crs(PROJECT_EPSG)
    railways_gdf = gpd.read_file(PATH_TO_RAILWAYS_DS)
    railways_gdf = railways_gdf.to_crs(PROJECT_EPSG)

    # create forestroad density layer
    create_road_density_layer(road_gdf, ref_grid_vector, ["track", "track_grade1", "track_grade2", "track_grade3", "track_grade4",
                                                          "track_grade5"], attribute_name, PATH_TO_FORESTROAD_DENSITY_VECTOR, PATH_TO_FORESTROAD_DENSITY_LAYER)

    # create hikingtrail density layer
    create_road_density_layer(road_gdf, ref_grid_vector, [
                              "path"], attribute_name, PATH_TO_HIKINGTRAIL_DENSITY_VECTOR, PATH_TO_HIKINGTRAIL_DENSITY_LAYER)

    # create railway density layer
    create_road_density_layer(railways_gdf, ref_grid_vector, [
                              "rail"], attribute_name, PATH_TO_RAILWAY_DENSITY_VECTOR, PATH_TO_RAILWAY_DENSITY_LAYER)
