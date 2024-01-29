import os
import numpy as np
import unittest
from config.config import BASE_PATH, PATH_TO_REF_RASTER
from src.gdal_wrapper import gdal_get_raster_info


REF_RASTER_REF_SYSTEM, REF_RASTER_PIXEL_SIZE, REF_RASTER_EXTENT, REF_RASTER_SHAPE, REF_RASTER_DTYPE = gdal_get_raster_info(
    PATH_TO_REF_RASTER)

LAYERS_TO_TEST = {
    "elevation": os.path.join(BASE_PATH, "data/processed/topographical_data/elevation_resampled_Average.tif"),
    "slope": os.path.join(BASE_PATH, "data/processed/topographical_data/slope_resampled_Average.tif"),
    "aspect": os.path.join(BASE_PATH, "data/processed/topographical_data/aspect_resampled_Average.tif"),
    "population_2006": os.path.join(BASE_PATH, "data/processed/population_data/geostat_2006_resampled_Average.tif"),
    "population_2011": os.path.join(BASE_PATH, "data/processed/population_data/geostat_2011_resampled_Average.tif"),
    "population_2018": os.path.join(BASE_PATH, "data/processed/population_data/geostat_2018_resampled_Average.tif"),
    "population_2021": os.path.join(BASE_PATH, "data/processed/population_data/geostat_2021_resampled_Average.tif"),
    "farmyard_density": os.path.join(BASE_PATH, "data/processed/farmyard_density_layer/farmyard_density_layer_resampled_nearest neighbor.tif"),
    "railway_density": os.path.join(BASE_PATH, "data/processed/road_density_layers/railway_density_layer_resampled_nearest neighbor.tif"),
    "forestroad_density": os.path.join(BASE_PATH, "data/processed/road_density_layers/forestroad_density_layer_resampled_nearest neighbor.tif"),
    "hikingtrail_density": os.path.join(BASE_PATH, "data/processed/road_density_layers/hikingtrail_density_layer_resampled_nearest neighbor.tif"),
    "forest_type": os.path.join(BASE_PATH, "data/processed/forest_type/tree_type_resampled_nearest neighbor.tif")
}


def assert_layer_specifications(test_case, layer_path):
    spatial_ref, pixel_size, extent, shape, dtype = gdal_get_raster_info(
        layer_path)
    test_case.assertEqual(spatial_ref, REF_RASTER_REF_SYSTEM)

    pixel_size = (np.abs(pixel_size[0]), np.abs(pixel_size[1]))
    test_case.assertEqual(extent, REF_RASTER_EXTENT)
    test_case.assertEqual(shape, REF_RASTER_SHAPE)


class TestFeatureLayersStatic(unittest.TestCase):

    def test_layer_specifications(self):
        for layer_name, layer_path in LAYERS_TO_TEST.items():
            with self.subTest(layer_name=layer_name):
                assert_layer_specifications(self, layer_path)


if __name__ == "__main__":
    unittest.main()
