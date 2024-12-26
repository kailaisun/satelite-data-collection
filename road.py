import math
import matplotlib.pyplot as plt
import osmnx as ox
import requests
from shapely.geometry import box
from PIL import Image
from io import BytesIO
from OSM_google_get import get_bounding_box
import geopandas as gpd
# 定义中心点和缩放级别
latitude = 1.3882613597360804
longitude = 103.97872924804688
zoom_level = 18  # 缩放级别
map_size = "512x512"  # Google Maps 静态图最大尺寸
api_key = ""  # 替换为您的 Google Maps API 密钥

# 可以注释掉: Step 1: 构建 Google Static Maps API URL
google_maps_url = f"https://maps.googleapis.com/maps/api/staticmap?center={latitude},{longitude}&zoom={zoom_level}&size={map_size}&maptype=satellite&key={api_key}"

# Step 2: 请求卫星图像
response = requests.get(google_maps_url)
if response.status_code == 200:
    satellite_image = Image.open(BytesIO(response.content))
else:
    raise Exception(f"Failed to fetch satellite image. Status code: {response.status_code}")

# Step 3: 获取道路网络
road_network = ox.graph_from_point((latitude, longitude), dist=400, network_type='all')  # 扩大范围
edges = ox.graph_to_gdfs(road_network, nodes=False)  # 获取道路边界



# Step 5: 裁剪道路数据
lon_min, lat_min,lon_max,  lat_max = get_bounding_box(latitude,longitude,zoom_level)
bounding_box = box(lon_min, lat_min, lon_max, lat_max)  # 创建地理范围
edges_clipped = edges[edges.intersects(bounding_box)]  # 仅保留与范围相交的道路



# Step 4: 绘制裁剪后的地图（仅保留红框内部内容）
fig, ax = plt.subplots(figsize=(5.12, 5.12))  # 图像尺寸对应 512x512 像素（dpi=100）

# 绘制裁剪后的道路（只绘制红框内的内容）
edges_clipped.plot(ax=ax, color='black', linewidth=1)

# 获取边界框的坐标
lon_min, lat_min, lon_max, lat_max = bounding_box.bounds
# 设置坐标范围，严格限制在红框内部
ax.set_xlim([lon_min, lon_max])
ax.set_ylim([lat_min, lat_max])

# 关闭坐标轴和红框
ax.axis("off")

# 保存图像为 512x512 像素，完全去掉红框边缘
cropped_image_path = './Singapore/'+str(zoom_level)+'_'+str(longitude)+'_'+str(latitude)+'_road_.png'
fig.savefig(
    cropped_image_path,
    dpi=100,                  # 确保输出为 512x512 像素
    bbox_inches="tight",      # 确保内容紧贴图像边缘
    pad_inches=0              # 去掉额外填充
)
plt.show()
# 关闭绘图窗口
plt.close(fig)

print(f"Clipped road network image saved to: {cropped_image_path}")
