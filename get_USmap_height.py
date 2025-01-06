
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from shapely.geometry import shape
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from OSM_google_get import download_and_crop_static_map, get_bounding_box
import numpy as np
import math


# Function to query ArcGIS data
def query_arcgis_data(bbox, where_clause="1=1"):
    """
    Query ArcGIS FeatureServer for building footprints within a bounding box.
    :param bbox: (xmin, ymin, xmax, ymax) in WGS84 (lat/lon).
    :param where_clause: SQL-like WHERE clause for filtering features.
    :return: A list of (Shapely geometry, height value) tuples.
    """
    base_url = (
        "https://services.arcgis.com/P3ePLMYs2RVChkJx/"
        "ArcGIS/rest/services/MS_Buildings_Training_Data_with_Heights/"
        "FeatureServer/0/query"
    )

    xmin, ymin, xmax, ymax = bbox
    params = {
        "where": where_clause,
        "outFields": "*",
        "geometry": f"{xmin},{ymin},{xmax},{ymax}",
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "returnGeometry": "true",
        "f": "geojson"
    }

    print("[INFO] Querying ArcGIS FeatureServer...")
    response = requests.get(base_url, params=params)
    response.raise_for_status()

    data = response.json()
    features = data.get("features", [])
    print(f"[INFO] Retrieved {len(features)} building footprints.")

    if not features:
        return []

    shapes = []
    for feat in features:
        geom_json = feat.get("geometry")
        props = feat.get("properties", {})
        if geom_json:
            geom = shape(geom_json)
            height_val = props.get("Height", 0.0)
            shapes.append((geom, height_val))
    return shapes

# 
def create_raster_from_geometries_with_height(geometries_with_heights, bbox, pixel_size):
    """
    Create a raster where pixel values represent height intensities.

    :param geometries_with_heights: List of tuples (geometry, height_value).
    :param bbox: Bounding box (xmin, ymin, xmax, ymax).
    :param pixel_size: Resolution of each pixel (in the same units as bbox).
    :return: Rasterized data array with height_value as pixel intensities.
    """
    xmin, ymin, xmax, ymax = bbox
    raster_width = int((xmax - xmin) / pixel_size)  # Number of pixels in x-direction
    raster_height = int((ymax - ymin) / pixel_size)  # Number of pixels in y-direction

    # Transform maps bounding box to raster grid
    transform = from_bounds(xmin, ymin, xmax, ymax, raster_width, raster_height)

    # Rasterize using height_value as the intensity for each geometry
    raster_data = rasterize(
        [(geometry, height_value) for geometry, height_value in geometries_with_heights],
        out_shape=(raster_height, raster_width),
        transform=transform,
        fill=0,  # Default value for areas without data
        all_touched=True,  # Ensure all touched pixels are filled
        dtype=np.float32
    )
    return raster_data

def plot_overlay(lat, lon, zoom, api_key, output_file):
    """
    Plot the overlay of Google Static Map and ArcGIS building heights with height-based intensity.

    :param lat: Latitude of the center point.
    :param lon: Longitude of the center point.
    :param zoom: Zoom level for the map.
    :param api_key: Google API key for Static Maps.
    :param output_file: Path to save the downloaded map image.
    """
    bbox = get_bounding_box(lat, lon, zoom)
    print(f"Bounding Box: {bbox}")

    # Download Google Static Map
    success = download_and_crop_static_map(api_key, lat, lon, zoom, output_file)
    if not success:
        return

    # Query ArcGIS data for building footprints and height values
    arcgis_data = query_arcgis_data(bbox)
    if not arcgis_data:
        print("[INFO] No ArcGIS data found.")
        return

    # Create raster with height_value-based intensity
    raster_data = create_raster_from_geometries_with_height(arcgis_data, bbox, pixel_size=0.00001)

    # Open Google Static Map
    google_map = Image.open(output_file)

    # Set up the plot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot Google Static Map
    xmin, ymin, xmax, ymax = bbox
    ax.imshow(google_map, extent=(xmin, xmax, ymin, ymax), zorder=1)

    # Overlay rasterized ArcGIS data with height_value-based grayscale intensity
    ax.imshow(
        raster_data,
        extent=(xmin, xmax, ymin, ymax),
        origin="upper",
        cmap="gray",  # Grayscale colormap
        alpha=0.6,    # Transparency
        zorder=2
    )

    # Add a marker for the center point
    #ax.plot(lon, lat, 'ro', markersize=5, label="Center Point")  # Red marker for center
    ax.legend(loc="upper right")

    # Set axis titles
    ax.set_title("ArcGIS Building Heights Overlaid on Google Static Map")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    # Set axis ticks
    ax.set_xticks(np.linspace(xmin, xmax, 5))  # Longitude ticks
    ax.set_yticks(np.linspace(ymin, ymax, 5))  # Latitude ticks

    # Set tick labels to show real lat/lon values
    ax.tick_params(axis='both', which='major', labelsize=10)

    # Add a grid for better readability
    ax.grid(visible=True, linestyle="--", alpha=0.5)

    # Save the combined image
    combined_image_file = "/Users/wangzhuoyulucas/Library/Mobile Documents/com~apple~CloudDocs/SMART/images/US/combined_overlay_image_OK.png"
    plt.savefig(combined_image_file, dpi=300, bbox_inches="tight")
    print(f"Combined image saved to {combined_image_file}")

    # Save the grayscale raster image
    grayscale_raster_file = "/Users/wangzhuoyulucas/Library/Mobile Documents/com~apple~CloudDocs/SMART/images/US/arcgis_raster_grayscale_OK.png"
    plt.imsave(grayscale_raster_file, raster_data, cmap="gray", origin="upper")
    print(f"Grayscale raster image saved to {grayscale_raster_file}")

    # Show the plot
    plt.show()

lat, lon = 35.453505, -97.542685 # Example coordinates
zoom = 17
api_key = #"AIzaSyAOdeNFb516oUkoICOEOqjSOp0sbD3cdhU"  # Replace with your API key
output_file = "/Users/wangzhuoyulucas/Library/Mobile Documents/com~apple~CloudDocs/SMART/images/US/google_map_image_OK.png"

plot_overlay(lat, lon, zoom, api_key, output_file)

