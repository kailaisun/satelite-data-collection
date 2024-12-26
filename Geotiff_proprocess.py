
from pyproj import Transformer
from rasterio.transform import xy
from rasterio.transform import rowcol

def xy2lonlat(row, col, transform, crs):
    # 将像素坐标转换为投影坐标（以米为单位）
    x_proj, y_proj = xy(transform, row, col, offset='ul')
    # print(f"像素 ({row}, {col}) 的投影坐标: X={x_proj}, Y={y_proj}")
    # 使用 pyproj 将投影坐标转换为经纬度
    transformer = Transformer.from_crs(crs, 'EPSG:4326', always_xy=True)
    lon, lat = transformer.transform(x_proj, y_proj)
    print(f"像素 ({row}, {col}) 的经纬度: 经度={lon}, 纬度={lat}")
    return lon, lat

def lonlat2xy(lon, lat, transform, crs):
    # 使用 pyproj 将经纬度转换为投影坐标
    transformer = Transformer.from_crs('EPSG:4326', crs, always_xy=True)
    x_proj, y_proj = transformer.transform(lon, lat)
    # print(f"经纬度 ({lon}, {lat}) 的投影坐标: X={x_proj}, Y={y_proj}")
    # 使用 rasterio 将投影坐标转换为像素位置
    row, col = rowcol(transform, x_proj, y_proj)
    print(f"经纬度 ({lon}, {lat}) 的像素位置: 行={row}, 列={col}")
    return row, col
