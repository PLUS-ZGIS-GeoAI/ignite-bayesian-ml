import numpy as np
import rasterio


def write_array_to_geotiff(array: np.array, raster_meta: dict, output_path: str) -> None:
    """Converts numpy array to GeoTIFF.

    Args:
        array (np.array): Array storing raster values.
        raster_meta (dict): Specifications of the raster.
        output_path (str): Directory and name of the output GeoTIFF.
    """
    raster_meta.update(nodata=np.nan)
    with rasterio.open(output_path, "w", **raster_meta) as dst:
        dst.write_band(1, array)
