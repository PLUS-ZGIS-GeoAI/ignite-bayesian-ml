import os

BASE_PATH = "C:/Users/David/Documents/ZGIS/Nextcloud_MyFiles/Projects/IGNITE"
PATH_TO_REF_RASTER = os.path.join(
    BASE_PATH, "data/processed/reference_grid/INCA_ref_raster_since_2013_100m.tif")

PROJECT_EPSG = "EPSG:31287"
REF_RASTER_EXTENT = ("20003.2793", "220053.2444", "720106.901", "620076.3115")
REF_RASTER_SHAPE = (7010, 4010)

# Geosphere Data API INCA grid data
GEOSPHERE_INCA_GRID_URL = "https://dataset.api.hub.geosphere.at/v1/grid/historical/inca-v1-1h-1km"
