import os
from config.config import BASE_PATH, PATH_TO_REF_RASTER
from src.gdal_wrapper import gdal_align_and_resample, gdal_rasterize_vector_layer


if __name__ == "__main__":

    years = [2006, 2011, 2018, 2021]
    resample_algorithm = "Average"

    path_to_pop_vector_layer = os.path.join(
        BASE_PATH, "data/processed/population_data/population_data_all_years_vector/geostat_pop.shp")

    for year in years:
        path_to_pop_raster_layer = os.path.join(
            BASE_PATH, f"data/processed/population_data/geostat_{year}.tif")
        path_to_pop_raster_layer_resampled = os.path.join(
            BASE_PATH, f"data/processed/population_data/geostat_{year}_resampled_{resample_algorithm}.tif")

        # TODO what to do with this extent? Store in config?
        gdal_rasterize_vector_layer(
            path_to_pop_vector_layer, path_to_pop_raster_layer,
            "geostat_pop", f"POP_{year}", "1000.0", None,  ("4287000.0", "2596000.0", "4853000.0", "2890000.0"), "Float32", pixel_mode=False
        )

        gdal_align_and_resample(path_to_pop_raster_layer,
                                path_to_pop_raster_layer_resampled, PATH_TO_REF_RASTER, resample_algorithm)
