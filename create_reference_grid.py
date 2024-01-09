import rasterio
from rasterio.transform import from_origin
import pyproj


def create_raster(target_projection: str, ne_corner_wgs84: tuple, sw_corner_wgs84: tuple, num_grid_points_x: int, num_grid_points_y: int, output_path: str):
    """
    Function creates raster (tif) based on the specifications of given by parameters. Corner coordinates must be given in wgs84 projection. Coorner coordinates and number of x and y grid points specifies resolution. Resolution is returned and tif saved to path.  
    """

    # Create a pyproj Transformer to convert between WGS84 and EPSG:31287
    transformer = pyproj.Transformer.from_crs(
        'EPSG:4326', target_projection, always_xy=True)

    # Reproject the corner points to EPSG:31287
    ne_corner = transformer.transform(ne_corner_wgs84[0], ne_corner_wgs84[1])
    sw_corner = transformer.transform(sw_corner_wgs84[0], sw_corner_wgs84[1])

    # Calculate the pixel size
    pixel_size_x = (ne_corner[0] - sw_corner[0]) / num_grid_points_x
    pixel_size_y = (ne_corner[1] - sw_corner[1]) / num_grid_points_y

    # Create the transformation matrix
    transform = from_origin(
        sw_corner[0], ne_corner[1], pixel_size_x, pixel_size_y)

    # Create an empty raster
    raster = rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        dtype=rasterio.float32,
        count=1,
        width=num_grid_points_x,
        height=num_grid_points_y,
        crs=target_projection,
        transform=transform
    )

    # Close the raster file
    raster.close()

    return pixel_size_x, pixel_size_y


if __name__ == "__main__":

    # create INCA reference raster since 2013
    x_res, y_res = create_raster(target_projection='EPSG:31287',
                                 ne_corner_wgs84=(17.7438, 49.3973),
                                 sw_corner_wgs84=(8.4445, 45.7727),
                                 num_grid_points_x=701,
                                 num_grid_points_y=401,
                                 output_path="INCA_ref_raster_since_2013")

    # create INCA reference raster before 2013
    x_res, y_res = create_raster(target_projection='EPSG:31287',
                                 ne_corner_wgs84=(9.2126, 49.2276),
                                 sw_corner_wgs84=(17.2142, 46.0828),
                                 num_grid_points_x=601,
                                 num_grid_points_y=351,
                                 output_path="INCA_ref_raster_before_2013")
