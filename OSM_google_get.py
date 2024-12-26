import requests
from PIL import Image
from io import BytesIO
import time
import pandas as pd

def download_and_crop_static_map(api_key, lat, lon, zoom, output_file, timeout=10, max_retries=3):
    """
    Downloads satellite imagery from Google Static Maps API, then crops it to 512x512 pixels.

    Args:
        api_key (str): Google Maps API key.
        lat (float): Latitude of the center.
        lon (float): Longitude of the center.
        zoom (int): Zoom level (1–20).
        output_file (str): Path to save the cropped image.
        timeout (int): Timeout for the request in seconds (default 10).
        max_retries (int): Maximum number of retries for failed downloads.

    Returns:
        bool: True if the download succeeds, False otherwise.
    """
    # Image size for download (550x550)
    download_size = (512, 512)
    crop_size = (512, 512)

    # Construct the API request URL
    base_url = "https://maps.googleapis.com/maps/api/staticmap"
    params = {
        "center": f"{lat},{lon}",
        "zoom": zoom,
        "size": f"{download_size[0]}x{download_size[1]}",
        "maptype": "satellite",
        "key": api_key,
    }

    for attempt in range(max_retries):
        try:
            # Request the image with a timeout
            response = requests.get(base_url, params=params, timeout=timeout)

            if response.status_code == 200:
                # Open the image
                image = Image.open(BytesIO(response.content))

                # Calculate cropping coordinates to center the image
                left = (download_size[0] - crop_size[0]) // 2
                upper = (download_size[1] - crop_size[1]) // 2
                right = left + crop_size[0]
                lower = upper + crop_size[1]

                # Crop the image to 512x512
                cropped_image = image.crop((left, upper, right, lower))

                # Save the cropped image
                cropped_image.save(output_file)
                print(f"Cropped satellite image saved to {output_file}")
                return True
            else:
                print(f"Error downloading image: {response.status_code}, {response.text}")
                return False

        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1} for {output_file}")
        except Exception as e:
            print(f"Error: {e} on attempt {attempt + 1} for {output_file}")

        # Wait a short time before retrying
        time.sleep(2)

    print(f"Failed to download after {max_retries} attempts: {output_file}")
    return False

def get_bounding_box(lat, lon, zoom, size=512):
    """
    Calculate bounding box from latitude, longitude, zoom level, and image size.

    Args:
        lat (float): Latitude of the center.
        lon (float): Longitude of the center.
        zoom (int): Zoom level (e.g., 15).
        size (int): Pixel size of the image (default 512).

    Returns:
        tuple: (min_lon, min_lat, max_lon, max_lat) for the bounding box.
    """
    import math

    # Earth radius in meters
    EARTH_RADIUS = 6378137.0
    INITIAL_RESOLUTION = 2 * math.pi * EARTH_RADIUS / 256.0  # Resolution at zoom 0
    origin_shift = 2 * math.pi * EARTH_RADIUS / 2.0

    # Calculate resolution at given zoom level
    resolution = INITIAL_RESOLUTION / (2 ** zoom)

    # Convert center lat/lon to meters
    mx = lon * origin_shift / 180.0
    my = math.log(math.tan((90 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
    my = my * origin_shift / 180.0

    # Calculate bounding box in meters
    half_size = (size / 2.0) * resolution
    minx = mx - half_size
    maxx = mx + half_size
    miny = my - half_size
    maxy = my + half_size

    # Convert bounding box back to lat/lon
    def meters_to_latlon(mx, my):
        lon = (mx / origin_shift) * 180.0
        lat = (my / origin_shift) * 180.0
        lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180.0)) - math.pi / 2.0)
        return lat, lon

    min_lat, min_lon = meters_to_latlon(minx, miny)
    max_lat, max_lon = meters_to_latlon(maxx, maxy)

    return (min_lon, min_lat, max_lon, max_lat)

# import os

# API_KEY = 'AIzaSyAOdeNFb516oUkoICOEOqjSOp0sbD3cdhU'#'AIzaSyDYA7azvJSSesYlCx7HuvAnVvaYPDz2D1I' # 'AIzaSyBECl9PSOPQsyNqKR9mpjaFwLQw6pDBQtg'
#
# download_and_crop_static_map(API_KEY, 1.3882613597360804,103.97872924804688,18,'./Sinagpore/18_103.97735595703125_1.3896342476555235.png')
#
#
# print(get_bounding_box(1.3882613597360804,103.97872924804688,18))
