import os
from config.config import base_path, path_to_ref_raster
from src.gdal_wrapper import gdal_align_and_resample, gdal_rasterize


if __name__ == "__main__":

    years = [2006, 2011, 2018, 2021]
    resample_algorithm = "Average"

    rel_path_to_pop_vector_layer = "data/processed/population_data/population_data_all_years_vector/geostat_pop.shp"
    path_to_pop_vector_layer = os.path.join(
        base_path, rel_path_to_pop_vector_layer)

    for year in years:
        rel_path_to_pop_raster_layer = f"data/processed/population_data/geostat_{year}.tif"
        rel_path_to_pop_raster_layer_resampled = f"data/processed/population_data/geostat_{year}_resampled_{resample_algorithm}.tif"
        path_to_pop_raster_layer = os.path.join(
            base_path, rel_path_to_pop_raster_layer)
        path_to_pop_raster_layer_resampled = os.path.join(
            base_path, rel_path_to_pop_raster_layer_resampled)

        gdal_rasterize(path_to_pop_vector_layer, path_to_pop_raster_layer,
                       "geostat_pop", f"POP_{year}", "1000.0", "-1.0", ("4287000.0", "2596000.0", "4853000.0", "2890000.0"), "Float32")

        gdal_align_and_resample(path_to_pop_raster_layer,
                                path_to_pop_raster_layer_resampled, path_to_ref_raster, resample_algorithm)
