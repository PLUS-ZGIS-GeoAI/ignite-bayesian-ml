import subprocess
import numpy as np
from typing import Optional
from osgeo import gdal, osr

# TODO add docstring to each function


def gdal_get_raster_info(raster_path: str) -> tuple:
    """
    Get information about the raster, including spatial reference, resolution, and extent, shape and datatype.
    """
    raster_ds = gdal.Open(raster_path)
    spatial_ref = raster_ds.GetProjection()
    geo_transform = raster_ds.GetGeoTransform()
    resolution = (geo_transform[1], geo_transform[5])
    extent = (geo_transform[0], geo_transform[3], geo_transform[0] + geo_transform[1] *
              raster_ds.RasterXSize, geo_transform[3] + geo_transform[5] * raster_ds.RasterYSize)
    num_bands = raster_ds.RasterCount
    shape = (raster_ds.RasterXSize, raster_ds.RasterYSize, num_bands)
    data_type = raster_ds.GetRasterBand(1).DataType

    raster_ds = None
    return spatial_ref, resolution, extent, shape, data_type


def gdal_align_and_resample(path_to_input_raster: str, path_to_output_raster: str, path_to_ref_raster: str, resample_alg: str, nodata_value: Optional[float] = None) -> None:
    """
    Aligns and resamples the input raster to match the specifications of the reference raster using gdal.Warp.
    """
    ref_ds = gdal.Open(path_to_ref_raster)
    spatial_ref = ref_ds.GetProjection()
    geo_transform = ref_ds.GetGeoTransform()
    shape = (ref_ds.RasterXSize, ref_ds.RasterYSize)

    warp_options = gdal.WarpOptions(
        format='GTiff',
        outputBounds=(geo_transform[0], geo_transform[3] + shape[1] * geo_transform[5],
                      geo_transform[0] + shape[0] * geo_transform[1], geo_transform[3]),
        xRes=geo_transform[1],
        yRes=abs(geo_transform[5]),
        resampleAlg=resample_alg,
        dstSRS=spatial_ref,
        dstNodata=nodata_value,
    )

    gdal.Warp(path_to_output_raster,
              path_to_input_raster, options=warp_options)
    
    ref_df = None


def gdal_rasterize_vector_layer(path_to_vector_file: str, path_to_output: str, path_to_ref_raster: str, layer_name: str, col_name: str) -> None:
    """
    Create a raster from a vector file using GDAL.
    """

    ref_ds = gdal.Open(path_to_ref_raster)
    geo_transform = ref_ds.GetGeoTransform()
    shape = (ref_ds.RasterXSize, ref_ds.RasterYSize)
    extent = (geo_transform[0], geo_transform[3] + shape[1] * geo_transform[5],
              geo_transform[0] + shape[0] * geo_transform[1], geo_transform[3])

    command = [
        "gdal_rasterize",
        "-l", layer_name,
        "-a", col_name,
        "-ts", str(shape[0]), str(shape[1]),
        "-te", str(extent[0]), str(extent[1]), str(extent[2]), str(extent[3]),
        "-of", "GTiff",
        path_to_vector_file,
        path_to_output
    ]

    subprocess.run(command)


def gdal_create_geotiff_from_nc(data: np.array, lon: np.array, lat: np.array, path_to_output: str) -> None:
    """
    Create geotiff from arrays (data, longitude and latitude) wich are extracted from netcdf
    """

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


def gdal_resample(path_to_input_raster: str, 
                  path_to_output_raster: str, 
                  target_resolution: float, 
                  resample_alg: str, 
                  nodata_value: Optional[float] = None) -> None:
    """
    Resamples a raster from the original resolution into the target resolution using GDAL.

    Args:
        path_to_input_raster (str): Path to the input raster file.
        path_to_output_raster (str): Path to save the output resampled raster.
        target_resolution (float): Target resolution in the same units as the input raster.
        resample_alg (str): Resampling algorithm to be used (e.g., 'nearest', 'bilinear', 'cubic', etc.).
        nodata_value (Optional[float]): Optional nodata value to be set in the output raster.

    Returns:
        None
    """

    # Open the input raster dataset
    input_ds = gdal.Open(path_to_input_raster)
    if input_ds is None:
        raise FileNotFoundError(f"Failed to open input raster: {path_to_input_raster}")

    # Get the input raster's geotransform, spatial reference, and shape
    geo_transform = input_ds.GetGeoTransform()
    spatial_ref = input_ds.GetProjectionRef()
    shape = (input_ds.RasterYSize, input_ds.RasterXSize)

    # Calculate the new geotransform based on the target resolution
    new_geo_transform = list(geo_transform)
    new_geo_transform[1] = target_resolution
    new_geo_transform[5] = -1 * target_resolution  # negative because of Y-axis inversion

    # Define warp options
    warp_options = gdal.WarpOptions(
        format='GTiff',
        xRes=target_resolution,
        yRes=target_resolution,
        resampleAlg=resample_alg,
        dstSRS=spatial_ref,
        dstNodata=nodata_value,
        outputBounds=(geo_transform[0], geo_transform[3] + shape[1] * geo_transform[5],
                      geo_transform[0] + shape[0] * geo_transform[1], geo_transform[3])
    )

    # Perform the resampling
    gdal.Warp(path_to_output_raster, input_ds, options=warp_options)

    # Close the input dataset
    input_ds = None


def set_zeros_to_nan(path_to_input_raster: str, path_to_output_raster: str) -> None:
    """
    Loads an image and sets all 0 values to NaN values.

    Args:
        path_to_input_raster (str): Path to the input raster file.
        path_to_output_raster (str): Path to save the output raster file.

    Returns:
        None
    """

    # Open the input raster dataset
    input_ds = gdal.Open(path_to_input_raster)
    if input_ds is None:
        raise FileNotFoundError(f"Failed to open input raster: {path_to_input_raster}")

    # Get the raster's geotransform, spatial reference, and shape
    geo_transform = input_ds.GetGeoTransform()
    spatial_ref = input_ds.GetProjectionRef()
    shape = (input_ds.RasterYSize, input_ds.RasterXSize)

    # Read the raster data
    band = input_ds.GetRasterBand(1)
    data = band.ReadAsArray()

    # Get the nodata value from the raster metadata
    nodata_value = band.GetNoDataValue()

    # Convert 0 values to NaN values from the raster's nodata value
    data[data == 0] = nodata_value

    # Create a new raster file with NaN values
    driver = gdal.GetDriverByName('GTiff')
    output_ds = driver.Create(path_to_output_raster, shape[1], shape[0], 1, band.DataType)
    output_ds.SetGeoTransform(geo_transform)
    output_ds.SetProjection(spatial_ref)
    output_band = output_ds.GetRasterBand(1)
    output_band.SetNoDataValue(nodata_value)  # Set nodata value for output raster
    output_band.WriteArray(data)

    # Close the datasets
    input_ds = None
    output_ds = None
