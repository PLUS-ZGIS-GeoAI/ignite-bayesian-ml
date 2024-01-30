import os

# Geosphere Data API INCA grid data
GEOSPHERE_INCA_GRID_URL = "https://dataset.api.hub.geosphere.at/v1/grid/historical/inca-v1-1h-1km"

# Project EPSG - every layer should be in this projection
PROJECT_EPSG = "EPSG:31287"

# Path to project directory
BASE_PATH = "C:/Users/David/Documents/ZGIS/Nextcloud_MyFiles/Projects/IGNITE"

# Path to reference raster
PATH_TO_REF_RASTER = os.path.join(
    BASE_PATH, "data/processed/reference_grid/INCA_ref_raster_since_2013_100m.tif")
PATH_TO_REF_GRID_VECTOR = os.path.join(BASE_PATH,
                                       "data/processed/reference_grid/inca_ref_grid_100m_vector/inca_ref_grid_100m_vector.shp")

# Paths to forest type layers
PATH_TO_FOREST_TYPE_DS = os.path.join(
    BASE_PATH, "data/raw/BWF_forest_type/forest_type_merged.tif")
PATH_TO_FOREST_TYPE_Layer = os.path.join(
    BASE_PATH, "data/processed/forest_type/forest_type_layer.tif")

# Paths to road layers
PATH_TO_ROADS_DS = os.path.join(
    BASE_PATH, "data/raw/OSM_austria/austria-latest-free/gis_osm_roads_free_1.shp")
PATH_TO_RAILWAYS_DS = os.path.join(
    BASE_PATH, "data/raw/OSM_austria/austria-latest-free/gis_osm_railways_free_1.shp")

PATH_TO_FORESTROAD_DENSITY_VECTOR = os.path.join(
    BASE_PATH, "data/processed/road_density_layers/forestroad_density_vector/forestroad_density_vector.shp")
PATH_TO_RAILWAY_DENSITY_VECTOR = os.path.join(
    BASE_PATH, "data/processed/road_density_layers/railway_density_vector/railway_density_vector.shp")
PATH_TO_HIKINGTRAIL_DENSITY_VECTOR = os.path.join(
    BASE_PATH, "data/processed/road_density_layers/hikingtrail_density_vector/hikingtrail_density_vector.shp")

PATH_TO_FORESTROAD_DENSITY_LAYER = os.path.join(
    BASE_PATH, "data/processed/road_density_layers/forestroad_density_layer.tif")
PATH_TO_RAILWAY_DENSITY_LAYER = os.path.join(
    BASE_PATH, "data/processed/road_density_layers/railway_density_layer.tif")
PATH_TO_HIKINGTRAIL_DENSITY_LAYER = os.path.join(
    BASE_PATH, "data/processed/road_density_layers/hikingtrail_density_layer.tif")

# paths to farmyard density layers
PATH_TO_FARMYARD_DS = os.path.join(
    BASE_PATH, "data/processed/farmyard_density_layer/osm_lu_farmyards/osm_lu_farmyards.shp")
PATH_TO_FARMYARD_DENSITY_VECTOR = os.path.join(
    BASE_PATH, "data/processed/farmyard_density_layer/farmyard_density_layer_vector.shp")
PATH_TO_FARMYARD_DENSITY_LAYER = os.path.join(
    BASE_PATH, "data/processed/farmyard_density_layer/farmyard_density_layer.tif")


# paths to topograhical layers
PATH_TO_ELEVATION_DS = os.path.join(
    BASE_PATH, "data/raw/OGD_Topographie/dhm_at_lamb_10m_2018.tif")
PATH_TO_SLOPE_DS = os.path.join(
    BASE_PATH, "data/processed/topographical_data/slope_10m.tif")
PATH_TO_ASPECT_DS = os.path.join(
    BASE_PATH, "data/processed/topographical_data/aspect_10m.tif")

PATH_TO_ELEVATION_LAYER = os.path.join(
    BASE_PATH, f"data/processed/topographical_data/elevation_layer.tif")
PATH_TO_SLOPE_LAYER = os.path.join(
    BASE_PATH, f"data/processed/topographical_data/slope_layer.tif")
PATH_TO_ASPECT_LAYER = os.path.join(
    BASE_PATH, f"data/processed/topographical_data/aspect_layer.tif")


# TODO not finished yet; still needs to define intermediate paths
# paths to population layers
PATH_TO_NUTS_DATA = os.path.join(
    BASE_PATH, "data/raw/EU_NUTS/NUTS_RG_01M_2021_3035.shp")

PATH_TO_GEOSTAT_2006_DS = os.path.join(
    BASE_PATH, "data/raw/GEOSTAT_Population/GEOSTAT_Grid_POP_2006_1K/GEOSTAT_grid_EU_POP_2006_1K_V1_1_1.csv")
PATH_TO_GEOSTAT_2011_DS = os.path.join(
    BASE_PATH, "data/raw/GEOSTAT_Population/GEOSTAT-grid-POP-1K-2011-V2-0-1/Version 2_0_1/GEOSTAT_grid_POP_1K_2011_V2_0_1.csv")
PATH_TO_GEOSTAT_2018_DS = os.path.join(
    BASE_PATH, "data/raw/GEOSTAT_POPULATION/JRC_GRID_2018/JRC_POPULATION_2018.shp")
PATH_TO_GEOSTAT_2021_DS = os.path.join(
    BASE_PATH, "data/raw/GEOSTAT_Population/Eurostat_Census-GRID_2021_V1-0/ESTAT_Census_2011_V1-0.gpkg")

PATH_TO_POPULATION_ALL_YEARS_VECTOR = os.path.join(
    BASE_PATH, "data/processed/population_data/population_data_all_years_vector/geostat_pop.shp")

PATH_TO_POP_2006_LAYER = os.path.join(
    BASE_PATH, "data/processed/population_data/population_2006_layer.tif")
PATH_TO_POP_2011_LAYER = os.path.join(
    BASE_PATH, "data/processed/population_data/population_2011_layer.tif")
PATH_TO_POP_2018_LAYER = os.path.join(
    BASE_PATH, "data/processed/population_data/population_2018_layer.tif")
PATH_TO_POP_2021_LAYER = os.path.join(
    BASE_PATH, "data/processed/population_data/population_2021_layer.tif")
