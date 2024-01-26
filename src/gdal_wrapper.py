from osgeo import gdal, osr
import subprocess
import numpy as np

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


def gdal_create_geotiff_from_arrays(data: np.array, lon: np.array, lat: np.array, path_to_output: str):

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
