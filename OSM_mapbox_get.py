import os
import geopandas as gpd
import requests
from PIL import Image
from io import BytesIO
import math

ACCESS_TOKEN = ''



# Mapbox access token
tileset_id = 'mapbox.satellite'
nigeria_boundary = gpd.read_file("MasterPlan2019PlanningAreaBoundaryNoSea.geojson").to_crs('EPSG:4326')  # Replace with your file path
# Get the bounding box
minx, miny, maxx, maxy = nigeria_boundary.total_bounds
print(minx, miny, maxx, maxy)
# Define the bounding box coordinates (min_lon, min_lat, max_lon, max_lat)
bounding_box = (103.98, 1.38469870063221, 104.02483065163,1.39077483208609)# (minx, miny, maxx, maxy)
# bounding_box = (-122.45, 37.74, -122.35, 37.84)  # Example for a region in San Francisco
# bounding_box = (-87.952, 41.634, -87.519, 42.086) # Chicago
# bounding_box = (-74.2631, 40.4778, -73.6997, 40.9217) # NewYork

# Calculate bounding box size in meters
nigeria_boundary_projected = nigeria_boundary.to_crs(epsg=3395)  # Convert to Mercator for meter-based calculations
projected_bounds = nigeria_boundary_projected.total_bounds
bbox_width = projected_bounds[2] - projected_bounds[0]  # maxx - minx
bbox_height = projected_bounds[3] - projected_bounds[1]  # maxy - miny

# Output bounding box size
print(f"Bounding Box Size: {bbox_width:.2f} meters (width) x {bbox_height:.2f} meters (height)")
# Define zoom level
zoom_level = 17


# Calculate tile range for the given bounding box and zoom level
def deg_to_tile(lat_deg, lon_deg, zoom):
    lat_rad = lat_deg * (math.pi / 180.0)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - (lat_rad - math.atan(math.sinh(math.pi))) / math.pi) / 2.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad)), math.e) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def tile_top_left_to_deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = lat_rad * (180.0 / math.pi)
    return (lat_deg, lon_deg)

def tile_bottom_right_to_deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = (xtile + 1) / n * 360.0 - 180.0
    lat_rad = math.pi * (1 - 2 * (ytile + 1) / n)
    lat_deg = math.degrees(math.atan(math.sinh(lat_rad)))
    return (lat_deg, lon_deg)
min_lon, min_lat, max_lon, max_lat = bounding_box
min_tile = deg_to_tile(min_lat, min_lon, zoom_level)
max_tile = deg_to_tile(max_lat, max_lon, zoom_level)
print(min_tile, max_tile)


tile_num = abs((max_tile[0] - min_tile[0]) * (max_tile[1] - min_tile[1]))

print(tile_num)


def tile_top_left_to_deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.pi * (1 - 2 * ytile / n)
    lat_deg = math.degrees(math.atan(math.sinh(lat_rad)))
    return (lat_deg, lon_deg)


from shapely.geometry import box, Polygon

# Function to convert tile numbers to bounding box in lat/lon
def tile_to_bbox(x, y, zoom):
    n = 2.0 ** zoom
    lon_min = x / n * 360.0 - 180.0
    lon_max = (x + 1) / n * 360.0 - 180.0
    lat_min = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    lat_max = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))

    # Create bounding box in lat/lon
    bbox = box(lon_min, lat_min, lon_max, lat_max)

    # Convert to GeoDataFrame for CRS transformation
    gdf = gpd.GeoDataFrame({"geometry": [bbox]}, crs="EPSG:4326")
    gdf = gdf.to_crs(epsg=3395)  # Reproject to Mercator for meter-based calculations

    # Calculate size in meters
    projected_bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    width_meters = projected_bounds[2] - projected_bounds[0]
    height_meters = projected_bounds[3] - projected_bounds[1]

    return {
        "bbox": bbox,
        "width_meters": width_meters,
        "height_meters": height_meters
    }


# Download tiles within the specified range
# 也就是说
tileset_id = 'mapbox.satellite'
def download_tile(x, y, zoom):
    url = f"https://api.mapbox.com/v4/{tileset_id}/{zoom}/{x}/{y}@2x.png?access_token={ACCESS_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        print(f"Downloading tile {x}, {y} at zoom level {zoom}.")
        return img
    else:
        print(f"Failed to download tile {x}, {y} at zoom level {zoom}. Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        return None

# Save tiles
output_dir = "./Sinagpore/"
os.makedirs(output_dir, exist_ok=True)

for x in range(min_tile[0], max_tile[0] + 1):
    for y in range(max_tile[1], min_tile[1] + 1):
        tile_img = download_tile(x, y, zoom_level)
        if tile_img:
            lat,lon=tile_top_left_to_deg(x,y,zoom_level)
            lat_right,lon_right=tile_bottom_right_to_deg(x,y,zoom_level)
            print(lat,lon)
            print(lat_right,lon_right)
            from PIL import Image, ImageDraw, ImageFont
            draw = ImageDraw.Draw(tile_img)
            text = str(lat)+"_,_"+str(lon)

            # 定义字体和大小（可选，如果没有特定字体可直接用默认字体）
            try:
                font = ImageFont.truetype("arial.ttf", 20)  # 确保系统有这个字体
            except IOError:
                font = ImageFont.load_default()

            # 在左上角绘制文字
            draw.text((10, 10), text, font=font, fill="red")  # 位置 (10, 10), 字体颜色为红色
            tile_img.save(os.path.join(output_dir, f"{zoom_level}_{x}_{y}.png"))

print("Tiles downloaded successfully.")
