from src.utils import align_and_resample


if __name__ == "__main__":

    resample_alg = "nearest neighbor"

    # Example usage
    path_to_ref_raster = r"C:\Users\David\Documents\ZGIS\Nextcloud_MyFiles\Projects\IGNITE\data\processed\reference_grid\INCA_ref_raster_since_2013_100m.tif"
    path_to_input_raster = r"C:\Users\David\Documents\ZGIS\Nextcloud_MyFiles\Projects\IGNITE\data\raw\BWF_forest_type\forest_type_merged.tif"
    path_to_output_raster = fr"C:\Users\David\Documents\ZGIS\Nextcloud_MyFiles\Projects\IGNITE\data\processed\forest_type\tree_type_resampled_{resample_alg}.tif"

    align_and_resample(path_to_input_raster,
                       path_to_output_raster, path_to_ref_raster, resample_alg)
