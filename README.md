# satelite-data-collection

Updating..

For a given lat and long, this code can product the aligned the Singapore landuse map (worldcover dataset), the road network map (OSM), building height/presence map (Openbuilding 2.5D), and the satellite image (Googlemap).

## Environment
- The code is tested on python 3.10.


## Install

rasterio
shapely
geopandas
pyproj
osmnx
  


## Usage

Get Satelite image and building depth image:
```
python geotiff-reader.py
```

![18_103 97872924804688_1 3882613597360804](https://github.com/user-attachments/assets/5290d712-64be-4888-bd45-35fe03fe539b) 
![18_103 97872924804688_1 3882613597360804_height_vis_](https://github.com/user-attachments/assets/899c3db4-2954-41ab-9151-ecd8da433473)

Get road network image:
```
python road.py
```
![18_103 97872924804688_1 3882613597360804_road_](https://github.com/user-attachments/assets/2ea298dd-c313-44ce-bb38-712412a8eade)

Get landuse image:
```
python landuse3.py
```
![image](https://github.com/user-attachments/assets/d5b6c139-254f-4ad5-9ffe-70005506d6ce)

ChatGPT4 Prompt: The image depicts a semi-urban environment with distinct elements: buildings with orange roofs are dispersed across the area, mostly surrounded by dense vegetation concentrated in the center and upper-right. Roads curve through the scene, connecting the buildings and forming a network, primarily visible in the lower-left and middle sections. A large open space, likely a field or plaza, is located near the center-left, bordered by trees and structures. The spatial layout integrates built areas within a predominantly green landscape, where vegetation acts as natural boundaries separating roads, buildings, and open spaces.






