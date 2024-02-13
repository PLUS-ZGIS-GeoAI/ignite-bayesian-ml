import os
import numpy as np
import unittest
from config.config import PATH_TO_PATH_CONFIG_FILE, BASE_PATH
from src.utils import load_paths_from_yaml, replace_base_path
from src.gdal_wrapper import gdal_get_raster_info


paths = load_paths_from_yaml(PATH_TO_PATH_CONFIG_FILE)
paths = replace_base_path(paths, BASE_PATH)

print(os.path.exists(paths["reference_grid"]["raster"]))


REF_SPATIAL_REF, REF_PIXEL_SIZE, REF_EXTENT, REF_SHAPE, REF_DTYPE = gdal_get_raster_info(
    paths["reference_grid"]["raster"])


LAYERS_TO_TEST = {
    "pop_2006": paths["population_layers"]["2006"]["final"],
    "pop_2011": paths["population_layers"]["2011"]["final"],
    "pop_2018": paths["population_layers"]["2018"]["final"],
    "pop_2021": paths["population_layers"]["2021"]["final"],
    "farmyard_ds": paths["farmyard_density"]["final"],
    "hiking_ds": paths["roads"]["hikingtrails"]["final"],
    "forest_ds": paths["roads"]["forestroads"]["final"],
    "rail_dens": paths["railways"]["final"],
    "elevation": paths["topographical_layers"]["elevation"]["final"],
    "slope": paths["topographical_layers"]["slope"]["final"],
    "aspect": paths["topographical_layers"]["aspect"]["final"],
    "foresttype": paths["forest_type"]["final"]}


def assert_layer_specifications(test_case, layer_path):
    spatial_ref, pixel_size, extent, shape, dtype = gdal_get_raster_info(
        layer_path)

    pixel_size = (np.abs(pixel_size[0]), np.abs(pixel_size[1]))
    ref_pixel_size = (np.abs(REF_PIXEL_SIZE[0]), np.abs(REF_PIXEL_SIZE[1]))

    test_case.assertEqual(spatial_ref, REF_SPATIAL_REF)
    test_case.assertEqual(extent, REF_EXTENT)
    test_case.assertEqual(shape, REF_SHAPE)
    test_case.assertEqual(pixel_size, ref_pixel_size)


class TestFeatureLayersStatic(unittest.TestCase):

    def test_layer_specifications(self):
        for layer_name, layer_path in LAYERS_TO_TEST.items():
            with self.subTest(layer_name=layer_name):
                assert_layer_specifications(self, layer_path)

    def test_layer_values(self):
        # TODO implement tests to evaluate if values in feature layers are plausible
        pass


if __name__ == "__main__":
    unittest.main()
