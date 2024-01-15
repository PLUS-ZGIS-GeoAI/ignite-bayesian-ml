from osgeo import gdal
import numpy as np
import geopandas as gpd
import random
from shapely.geometry import Point
from scipy import stats
import calendar


def sample_points(raster_path: str, num_samples: int, random_seed: int) -> gpd.GeoDataFrame:
    """
    Sample random points inside of raster. Only from locations where raster has data points are sampled.
    The function returns geodataframe of sampled points with same crs as raster
    """

    # Open the raster using GDAL
    ds = gdal.Open(raster_path)

    # Get the rasters reference system
    crs = ds.GetProjection()

    # Get the raster's geotransform information
    geotransform = ds.GetGeoTransform()
    x_origin = geotransform[0]
    y_origin = geotransform[3]
    pixel_width = geotransform[1]
    pixel_height = geotransform[5]

    # Read the raster data into a numpy array
    band = ds.GetRasterBand(1)
    data = band.ReadAsArray()

    # Get the NoData value
    no_data_value = band.GetNoDataValue()

    # Find the indices of the non-zero and non-NoData elements in the array
    non_no_data_indices = np.argwhere((data != 0) & (data != no_data_value))

    # Choose `num_samples` random indices from the non-zero and non-NoData indices
    random.seed(random_seed)
    sample_indices = random.sample(list(non_no_data_indices), num_samples)

    # Convert the sample indices to x, y coordinates
    x_coords = [x_origin + i[1] * pixel_width for i in sample_indices]
    y_coords = [y_origin + i[0] * pixel_height for i in sample_indices]

    # Create a list of Point objects from the x, y coordinates
    points = [Point(x, y) for x, y in zip(x_coords, y_coords)]

    # Create a GeoPandas dataframe from the list of Point objects
    gdf = gpd.GeoDataFrame(geometry=points, crs=crs)

    return gdf


def sample_categories(categories, probabilities, num_samples: int, random_seed: int):
    """
    Sample a given number of categories based on a discrete distribution specified by "probabilities"
    """

    # Create a categorical distribution using the categories and their corresponding probabilities
    cat_dist = stats.rv_discrete(
        values=(categories, probabilities), seed=random_seed)

    # Use the categorical distribution to sample `num_samples` categories
    samples = cat_dist.rvs(size=num_samples)
    return samples


def sample_random_date_given_year_and_month(month: int, year: int, random_state: int) -> str:
    """generate a random date given a year and a month"""

    # set the random state
    np.random.seed(random_state)

    # get the number of days a specific month has
    num_days = calendar.monthrange(year, month)[1]

    # randomly choose one of the days
    day = np.random.randint(1, num_days)

    # return a formatted date
    return f"{month:02}/{day:02}/{year}"
