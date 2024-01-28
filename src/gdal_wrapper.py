from osgeo import gdal, osr
import subprocess
import numpy as np
from typing import List

# TODO add docstring to each function


def gdal_get_raster_info(raster_path: str) -> tuple:
    """
    Get information about the raster, including spatial reference, resolution, and extent.
    """
    raster_ds = gdal.Open(raster_path)
    spatial_ref = raster_ds.GetProjection()
    geo_transform = raster_ds.GetGeoTransform()
    resolution = (geo_transform[1], geo_transform[5])
    extent = (geo_transform[0], geo_transform[3], geo_transform[0] + geo_transform[1] *
              raster_ds.RasterXSize, geo_transform[3] + geo_transform[5] * raster_ds.RasterYSize)
    raster_ds = None
    return spatial_ref, resolution, extent


# TODO no data value is not working as expected (e.g. for FFMC layer creation)
def gdal_align_and_resample(input_raster: str, output_raster: str, reference_raster: str, resample_alg: str) -> None:
    """
    Aligns and resamples the input raster to match the specifications of the reference raster.
    """
    target_srs, (x_res, y_res), (xmin, ymin, xmax,
                                 ymax) = gdal_get_raster_info(reference_raster)

    input_ds = gdal.Open(input_raster)
    gdal.Warp(output_raster, input_ds, dstSRS=target_srs, xRes=x_res, yRes=y_res,
              outputBounds=(xmin, ymin, xmax, ymax), resampleAlg=resample_alg, dstNodata=None)
    input_ds = None


def gdal_rasterize(input_path: str, output_path: str, layer_name: str, col_name: str, resolution: str, shape: tuple, no_data_value: str, extent: tuple, value_type: str, pixel_mode: bool = False):
    """
    Create a raster from a vector file using GDAL.
    """
    command = [
        "gdal_rasterize",
        "-l", layer_name,
        "-a", col_name,
    ]

    if pixel_mode:
        command.extend([
            "-ts", str(shape[0]), str(shape[1]),
        ])
    else:
        command.extend([
            "-tr", resolution, resolution,
        ])

    command.extend([
        "-a_nodata", no_data_value,
        "-te", str(extent[0]), str(extent[1]), str(extent[2]), str(extent[3]),
        "-ot", value_type,
        "-of", "GTiff",
        input_path,
        output_path
    ])

    subprocess.run(command)


def gdal_create_geotiff_from_coords(data: np.array, lon: np.array, lat: np.array, path_to_output: str):

    driver = gdal.GetDriverByName("GTiff")
    out_dataset = driver.Create(
        path_to_output, data.shape[1], data.shape[0], 1, gdal.GDT_Float32)

    width = lon[0][1] - lon[0][0]
    height = lat[:, 0][1] - lat[:, 0][0]

    out_dataset.SetGeoTransform((lon.min(), width, 0, lat.min(), 0, height))
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    out_dataset.SetProjection(srs.ExportToWkt())

    out_band = out_dataset.GetRasterBand(1)
    out_band.WriteArray(data)

    out_band.FlushCache()
    out_dataset.FlushCache()


def gdal_create_geotiff_from_ref_raster(data: np.array, lon: np.array, lat: np.array, str, path_to_output: str):

    driver = gdal.GetDriverByName("GTiff")
    out_dataset = driver.Create(
        path_to_output, data.shape[1], data.shape[0], 1, gdal.GDT_Float32)

    width = lon[0][1] - lon[0][0]
    height = lat[:, 0][1] - lat[:, 0][0]

    out_dataset.SetGeoTransform((lon.min(), width, 0, lat.min(), 0, height))
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    out_dataset.SetProjection(srs.ExportToWkt())

    out_band = out_dataset.GetRasterBand(1)
    out_band.WriteArray(data)

    out_band.FlushCache()
    out_dataset.FlushCache()


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


# TODO was only need for testing purposes. If really not needed anymore, delete code
'''
def gdal_create_geotiff_from_ref_raster(data: np.array, path_to_ref_raster: str, path_to_output: str):
    # Read the reference raster
    ref_dataset = gdal.Open(path_to_ref_raster)

    # Get the reference raster's geotransform
    geotransform = ref_dataset.GetGeoTransform()

    # Create a new GeoTIFF dataset
    driver = gdal.GetDriverByName("GTiff")
    rows, cols = data.shape
    output_dataset = driver.Create(
        path_to_output, cols, rows, 1, gdal.GDT_Float32)

    # Set the geotransform for the new dataset
    output_dataset.SetGeoTransform(geotransform)

    # Set the spatial reference information
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ref_dataset.GetProjection())
    output_dataset.SetProjection(srs.ExportToWkt())

    # Write the array data to the new GeoTIFF
    output_band = output_dataset.GetRasterBand(1)
    output_band.WriteArray(data)

    # Close the datasets to flush the changes
    output_band.FlushCache()
    output_dataset.FlushCache()
    ref_dataset = None
    output_dataset = None
'''
