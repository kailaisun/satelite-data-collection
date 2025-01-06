import rasterio
import matplotlib.pyplot as plt
from rasterio.plot import show
from shapely.geometry import box
import geopandas as gpd
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from OSM_google_get import get_bounding_box
import requests
# 定义文件路径
raster_path = "/Users/wangzhuoyulucas/Library/Mobile Documents/com~apple~CloudDocs/SMART/images/landuse-singapore.tif"  # 替换为您的 ESA WorldCover 数据文件路径

# 定义感兴趣区域 (Bounding Box)
latitude = 35.453505 
longitude = -97.542685
zoom_level = 18


# # Step 1: 构建 Google Static Maps API URL
# google_maps_url = f"https://maps.googleapis.com/maps/api/staticmap?center={latitude},{longitude}&zoom={zoom_level}&size={map_size}&maptype=satellite&key={api_key}"

# # Step 2: 请求卫星图像
# response = requests.get(google_maps_url)
# if response.status_code == 200:
#     satellite_image = Image.open(BytesIO(response.content))
# else:
#     raise Exception(f"Failed to fetch satellite image. Status code: {response.status_code}")


# 计算边界框
lon_min, lat_min,lon_max,  lat_max = get_bounding_box(latitude,longitude,zoom_level)
bounding_box = box(lon_min, lat_min, lon_max, lat_max)

# 打开 ESA WorldCover 数据
with rasterio.open(raster_path) as src:
    # 裁剪到感兴趣区域
    bbox_gdf = gpd.GeoDataFrame({"geometry": [bounding_box]}, crs="EPSG:4326")
    bbox_gdf = bbox_gdf.to_crs(src.crs)  # 转换坐标系
    bbox_bounds = bbox_gdf.total_bounds  # 获取边界框
    window = rasterio.windows.from_bounds(*bbox_bounds, transform=src.transform)
    clipped_data = src.read(1, window=window)
    clipped_transform = src.window_transform(window)

# 可视化裁剪后的数据

# 定义地物类别和对应的颜色 (根据 ESA WorldCover 数据的定义)
landuse_labels = {
    10: "Trees",
    20: "Shrubs",
    30: "Grassland",
    40: "Cropland",
    50: "Built-up",
    60: "Bare/Sparse Vegetation",
    70: "Snow/Ice",
    80: "Open Water",
    90: "Herbaceous Wetland",
    100: "Mangroves",
    110: "Moss/Lichen",
}
# 创建颜色映射
landuse_colors = [
    "#006400",  # Trees (dark green)
    "#ffbb22",  # Shrubs
    "#ffff4c",  # Grassland
    "#f096ff",  # Cropland
    "#fa0000",  # Built-up (red)
    "#b4b4b4",  # Bare/Sparse Vegetation
    "#f0f0f0",  # Snow/Ice
    "#0064c8",  # Open Water (blue)
    "#0096a0",  # Herbaceous Wetland
    "#00cf75",  # Mangroves
    "#fae6a0",  # Moss/Lichen
]
cmap = ListedColormap(landuse_colors)

# 创建图例内容
legend_patches = [
    plt.Line2D([0], [0], color=color, marker='o', markersize=10, linestyle='None', label=label)
    for color, label in zip(landuse_colors, landuse_labels.values())
]

# 绘制裁剪后的 ESA WorldCover 数据
fig, ax = plt.subplots(figsize=(10, 10))
im = ax.imshow(clipped_data, cmap=cmap)
ax.set_title("ESA WorldCover (10m Resolution)")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

# 添加图例
ax.legend(handles=legend_patches, loc='upper right', title="Land Use Types")

# 显示图像
plt.show()
