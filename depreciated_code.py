'''
# TODO no data value is not working as expected (e.g. for FFMC layer creation)
def gdal_align_and_resample(input_raster: str, output_raster: str, reference_raster: str, resample_alg: str) -> None:
    """
    Aligns and resamples the input raster to match the specifications of the reference raster.
    """
    target_srs, (x_res, y_res), (xmin, ymin, xmax,
                                 ymax) = gdal_get_raster_info(reference_raster)

    input_ds = gdal.Open(input_raster)
    # Set data type
    gdal.Warp(output_raster, input_ds, dstSRS=target_srs, xRes=x_res, yRes=y_res,
              outputBounds=(xmin, ymin, xmax, ymax), resampleAlg=resample_alg, dstNodata=None, )
    input_ds = None
'''


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
