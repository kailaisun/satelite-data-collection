import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from pyproj import CRS
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Transformer
from rasterio.transform import xy
from rasterio.transform import rowcol
from OSM_google_get import download_and_crop_static_map, get_bounding_box
from Geotiff_proprocess import lonlat2xy,xy2lonlat
from rasterio.warp import transform_bounds


Google_API_KEY = ''

lon=103.97872924804688
lat=1.3882613597360804
zoom_level=18
download_and_crop_static_map(Google_API_KEY, lat,lon,zoom_level,'./Singapore/'+str(zoom_level)+'_'+str(lon)+'_'+str(lat)+'.png')


min_lon, min_lat, max_lon, max_lat=get_bounding_box(lat,lon,18)

# 打开 GeoTIFF 文件
import os
import glob


import rasterio
from rasterio.warp import transform_bounds
from pathlib import Path

# 遍历文件夹找到所有 .tif 文件
def find_tif_files(root_dir):
    root_path = Path(root_dir)
    return list(root_path.rglob("*.tif"))

# 检查点是否在边界框内
def is_point_in_bounds(lon, lat, bounds):
    min_lon, min_lat, max_lon, max_lat = bounds
    return min_lon <= lon <= max_lon and min_lat <= lat <= max_lat
# 主逻辑
def find_image_containing_point(root_directory, lon, lat):
    tif_files = find_tif_files(root_directory)
    if not tif_files:
        print("没有找到任何 .tif 文件，请检查目录路径！")
        return None
    for file_path in tif_files:
        with rasterio.open(file_path) as dataset:
            # 获取图像边界并转换为经纬度坐标
            bounds = dataset.bounds
            if dataset.crs != 'EPSG:4326':
                bounds_wgs84 = transform_bounds(dataset.crs, 'EPSG:4326', bounds.left, bounds.bottom, bounds.right, bounds.top)
            else:
                bounds_wgs84 = (bounds.left, bounds.bottom, bounds.right, bounds.top)
            # 检查点是否在当前文件的范围内
            if is_point_in_bounds(lon, lat, bounds_wgs84):
                return file_path  # 返回包含该点的图像路径
    return None  # 如果没有找到，则返回 None

# 使用示例
root_directory = './building_height_Singapore'


result = find_image_containing_point(root_directory, lon, lat)
if result:
    print(f"经纬度 ({lon}, {lat}) 位于文件: {result}")
else:
    print(f"经纬度 ({lon}, {lat}) 不在任何图像范围内。")


# file_path = 'tile_apJi7uxJccw.tif'
with rasterio.open(result) as dataset:
    # 打印基本信息
    print(f"图像size: {dataset.width},{dataset.height}")
    # print(f"坐标参考系: {dataset.crs}")

    # 获取边界框（minx, miny, maxx, maxy）
    bounds = dataset.bounds
    # print(f"图像边界 (原始坐标系): {bounds}")

    # 如果需要将边界转换为 WGS84 坐标系 (经纬度)
    if dataset.crs != 'EPSG:4326':
        bounds_wgs84 = transform_bounds(dataset.crs, 'EPSG:4326', bounds.left, bounds.bottom, bounds.right, bounds.top)
        print(f"图像边界 (经纬度): {bounds_wgs84}")
    else:
        print(f"图像边界已经是经纬度 (WGS84): {bounds}")
    # exit(0)

    # 获取图像的地理变换参数和坐标参考系
    transform = dataset.transform
    crs = dataset.crs
    x,y=lonlat2xy(min_lon, max_lat, transform, crs)
    x_right,y_right=lonlat2xy(max_lon, min_lat, transform, crs)
    # x_center,y_center=lonlat2xy(lon,lat,transform, crs)
    # 指定的经纬度坐标（1000,1000)：经度=103.99701756588681, 纬度 = 1.3887628946852373
    # print(x_center,y_center)
    print(y, x, y_right,x_right,y_right-y, x_right-x)
    num_bands = dataset.count


    wave=2
    # 获取第 2 波段的基本信息
    if num_bands >= wave:  # 确保文件中至少有 2 个波段
        band2 = dataset.read(wave)  # 读取第 2 波段的数据
        print(f"波段的数据类型: {band2.dtype}")
        # print(f"波段 2 的数据形状: {band2.shape}")
    else:
        print("该图像没有该波段")

    # # 计算第 2 波段的统计信息
    # band2_min = np.min(band2)
    # band2_max = np.max(band2)
    # band2_mean = np.mean(band2)
    # band2_std = np.std(band2)
    # print(f"第 2 波段的最小值: {band2_min}")
    # print(f"第 2 波段的最大值: {band2_max}")
    # print(f"第 2 波段的均值: {band2_mean}")
    # print(f"第 2 波段的标准差: {band2_std}")
    max_value = np.max(band2)
    max_position = np.unravel_index(np.argmax(band2), band2.shape)  # 获取行列索引

    print(f" 波段的最大值: {max_value}")
    # print(f"最大值所在的像素位置: 行 {max_position[0]}, 列 {max_position[1]}")

    # 读取 512x512 的像素窗口
    # window = rasterio.windows.Window(y_center-600/2,x_center-600/2, 600,600)
    window = rasterio.windows.Window(y, x, y_right-y, x_right-x)
    band2 = dataset.read(wave, window=window)  # 读取第wave个波段的数据

    # 替换无效值 (-99.0) 为 NaN 或其他 nodata 值
    band2_cleaned = np.where(band2 == -99.0, np.nan, band2)
    band2_clipped = np.clip(band2_cleaned, 0, 72.5)
    # 计算第 2 波段的统计信息
    band2_min = np.min(band2_clipped)
    band2_max = np.max(band2_clipped)
    print(f"crop的最小值: {band2_min}")
    print(f"crop的最大值: {band2_max}")

    # band2_normalized = (band2_clipped - np.nanmin(band2_clipped)) / (
    #         np.nanmax(band2_clipped) - np.nanmin(band2_clipped)
    # )
    plt.imsave('./Singapore/'+str(zoom_level)+'_'+str(lon)+'_'+str(lat)+'_height_vis_.png', band2_clipped, cmap='gray')

    gray_data = band2_clipped.astype(np.uint8)
    from PIL import Image
    # 使用 Pillow 保存为单通道灰度图像
    Image.fromarray(gray_data).save('./Singapore/'+str(zoom_level)+'_'+str(lon)+'_'+str(lat)+'_height_.png')
# 可视化提取的图像
# plt.figure(figsize=(8, 8))
# plt.imshow(band2_normalized, cmap='gray')
# plt.colorbar(label='Pixel Intensity')
# plt.title("Central  Pixel Region")
# plt.xlabel("Columns")
# plt.ylabel("Rows")
# plt.show()




