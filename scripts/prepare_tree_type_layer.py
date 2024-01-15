from ..src.utils import align_and_resample


if __name__ == "__main__":

    resample_alg = "mode"

    # Example usage
    path_to_ref_raster = r"C:\Users\David\Documents\ZGIS\Nextcloud_MyFiles\Projects\IGNITE\data\raw\GEOSPHERE_INCA_GRID\INCA_ref_raster_before_2013.tif"
    path_to_input_raster = r"C:\Users\David\Documents\ZGIS\Nextcloud_MyFiles\Projects\IGNITE\data\raw\BWF_forest_type\forest_type_merged.tif"
    path_to_output_raster = fr"C:\Users\David\Documents\ZGIS\Nextcloud_MyFiles\Projects\IGNITE\data\processed\tree_type\tree_type_resampled_{resample_alg}.tif"

    align_and_resample(path_to_input_raster,
                       path_to_output_raster, path_to_ref_raster, resample_alg)
