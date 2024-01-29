import os
import unittest
from config.config import BASE_PATH, PATH_TO_REF_RASTER
from src.gdal_wrapper import gdal_get_raster_info


"""
REF_RASTER_REF_SYSTEM = 'PROJCS["MGI / Austria Lambert",GEOGCS["MGI",DATUM["Militar-Geographische_Institut",SPHEROID["Bessel 1841",6377397.155,299.1528128,AUTHORITY["EPSG","7004"]],AUTHORITY["EPSG","6312"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4312"]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["latitude_of_origin",47.5],PARAMETER["central_meridian",13.3333333333333],PARAMETER["standard_parallel_1",49],PARAMETER["standard_parallel_2",46],PARAMETER["false_easting",400000],PARAMETER["false_northing",400000],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Northing",NORTH],AXIS["Easting",EAST],AUTHORITY["EPSG","31287"]]'
REF_RASTER_PIXEL_SIZE = (99.87212862652486, -99.75637585508993)
REF_RASTER_EXTENT = (20003.27933205018, 620076.3115490554,
                     720106.9010039894, 220053.2443701448)
REF_RASTER_SHAPE = (7010, 4010, 1)
"""

REF_RASTER_REF_SYSTEM, REF_RASTER_PIXEL_SIZE, REF_RASTER_EXTENT, REF_RASTER_SHAPE, REF_RASTER_DTYPE = gdal_get_raster_info(
    PATH_TO_REF_RASTER)

LAYERS_TO_TEST = {
    "elevation": (os.path.join(BASE_PATH, "data/processed/topographical_data/elevation_resampled_Average.tif"), "Float32"),
    "slope": (os.path.join(BASE_PATH, "data/processed/topographical_data/slope_resampled_Average.tif"), "Float32"),
    "aspect": (os.path.join(BASE_PATH, "data/processed/topographical_data/aspect_resampled_Average.tif"), "Float32"),
    "population_2006": (os.path.join(BASE_PATH, "data/processed/population_data/geostat_2006_resampled_Average.tif"), "Float32"),
    "population_2011": (os.path.join(BASE_PATH, "data/processed/population_data/geostat_2011_resampled_Average.tif"), "Float32"),
    "population_2018": (os.path.join(BASE_PATH, "data/processed/population_data/geostat_2018_resampled_Average.tif"), "Float32"),
    "population_2021": (os.path.join(BASE_PATH, "data/processed/population_data/geostat_2021_resampled_Average.tif"), "Float32"),
    "farmyard_density": (os.path.join(BASE_PATH, "data/processed/farmyard_density_layer/farmyard_density_layer_resampled_nearest neighbor.tif"), "Float32"),
    "railway_density": (os.path.join(BASE_PATH, "data/processed/road_density_layers/railway_density_layer_resampled_nearest neighbor.tif"), "Float32"),
    "forestroad_density": (os.path.join(BASE_PATH, "data/processed/road_density_layers/forestroad_density_layer_resampled_nearest neighbor.tif"), "Float32"),
    "hikingtrail_density": (os.path.join(BASE_PATH, "data/processed/road_density_layers/hikingtrail_density_layer_resampled_nearest neighbor.tif"), "Float32"),
    "forest_type": (os.path.join(BASE_PATH, "data/processed/forest_type/tree_type_resampled_nearest neighbor.tif"), "Float32")
}


def assert_layer_specifications(test_case, layer_path, dtype):
    spatial_ref, pixel_size, extent, shape, dtype = gdal_get_raster_info(
        layer_path)
    test_case.assertEqual(spatial_ref, REF_RASTER_REF_SYSTEM)
    test_case.assertEqual(pixel_size, REF_RASTER_PIXEL_SIZE)
    test_case.assertEqual(extent, REF_RASTER_EXTENT)
    test_case.assertEqual(shape, REF_RASTER_SHAPE)
    test_case.assertEqual(dtype, "Float32")


class TestFeatureLayersStatic(unittest.TestCase):

    def test_layer_specifications(self):
        for layer_name, (layer_path, dtype) in LAYERS_TO_TEST.items():
            with self.subTest(layer_name=layer_name):
                assert_layer_specifications(self, layer_path, dtype)


if __name__ == "__main__":
    unittest.main()
