from typing import List
import numpy as np
from osgeo import gdal

from config.config import PATH_TO_REF_RASTER

# TODO not tested; take care - actually not the ref raster should be used for this, but one of the feature rasters


def gdal_get_bool_mask_from_coords(coords: List[tuple], path_to_ref_raster: str) -> np.array:
    """creates a boolean mask with the same shape of the reference raster. Cells containing a coordinate pair are True, others are False

    Args:
        coords (List[tuple]): List containing the coordinate pairs as tuples
        path_to_ref_raster (str): path to reference raster 

    Returns:
        np.array: boolean mask 
    """

    ref_raster = gdal.Open(path_to_ref_raster)

    # Get raster dimensions
    raster_cols = ref_raster.RasterXSize
    raster_rows = ref_raster.RasterYSize

    # Get raster geotransformation information
    geotransform = ref_raster.GetGeoTransform()
    x_origin, pixel_width, _, y_origin, _, pixel_height = geotransform

    # Transform coordinates to pixel indices
    x_indices = ((np.array(coords)[:, 0] - x_origin) / pixel_width).astype(int)
    y_indices = ((np.array(coords)[:, 1] -
                 y_origin) / pixel_height).astype(int)

    # Create a boolean mask with False
    boolean_mask = np.zeros((raster_rows, raster_cols), dtype=bool)

    # Clip indices to valid range
    x_indices = np.clip(x_indices, 0, raster_cols - 1)
    y_indices = np.clip(y_indices, 0, raster_rows - 1)

    # Set corresponding cells to True
    boolean_mask[y_indices, x_indices] = True

    return boolean_mask


if __name__ == "__main__":
    pass
