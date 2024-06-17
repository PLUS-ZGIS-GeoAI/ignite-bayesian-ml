from osgeo import gdal
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from scipy import stats
import calendar
import random


def sample_points(
    raster_path: str, num_samples: int, random_seed: int
) -> gpd.GeoDataFrame:
    """
    Sample random points inside a raster where data is present.
    Returns a GeoDataFrame of sampled points with the same CRS as the raster.
    """
    ds = gdal.Open(raster_path)
    crs = ds.GetProjection()
    geotransform = ds.GetGeoTransform()
    x_origin, y_origin, pixel_width, pixel_height = (
        geotransform[0],
        geotransform[3],
        geotransform[1],
        geotransform[5],
    )

    band = ds.GetRasterBand(1)
    data = band.ReadAsArray()
    no_data_value = band.GetNoDataValue()

    non_no_data_indices = np.argwhere((data != 0) & (data != no_data_value))
    sample_indices = random.sample(non_no_data_indices.tolist(), num_samples)

    x_coords = [x_origin + i[1] * pixel_width for i in sample_indices]
    y_coords = [y_origin + i[0] * pixel_height for i in sample_indices]

    points = [Point(x, y) for x, y in zip(x_coords, y_coords)]

    gdf = gpd.GeoDataFrame(geometry=points, crs=crs)
    return gdf


def sample_categories(categories, probabilities, num_samples: int, random_seed: int):
    """
    Sample a given number of categories based on a discrete distribution specified by "probabilities"
    """
    cat_dist = stats.rv_discrete(values=(categories, probabilities), seed=random_seed)
    samples = cat_dist.rvs(size=num_samples)
    return samples


def sample_random_date_given_year_and_month(
    month: int, year: int, random_state: int
) -> str:
    """Generate a random date given a year and a month"""
    np.random.seed(random_state)
    num_days = calendar.monthrange(year, month)[1]
    day = np.random.randint(1, num_days)
    return f"{month:02}/{day:02}/{year}"
