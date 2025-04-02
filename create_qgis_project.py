import geopandas as gpd
#import rasterio
import os
import yaml
from unidecode import unidecode
import pickle


from qgis.core import (
    QgsApplication,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsProject,
    QgsCoordinateReferenceSystem
)
import os

# Zoom to all layers extent
from qgis.core import QgsLayerTreeGroup
from qgis.gui import QgsMapCanvas



with open("configs/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


region_name = config['region_name'] #if country is studied, then use country name
region_name_clean = unidecode(region_name)
region_name_clean = region_name_clean.replace(" ", "")
region_name_clean = region_name_clean.replace(".", "")
region_name_clean = region_name_clean.replace("'", "") 
region_name = region_name_clean

region_folder_name = config['region_folder_name']
resampled = '_resampled' 

EPSG_custom = ''


dirname = os.getcwd() 
data_path = os.path.join(dirname, 'data', region_folder_name)
data_from_DEM = os.path.join(data_path, 'derived_from_DEM')

###
output_gpkg_path = os.path.join(data_path, "output_combined.gpkg")
###

# Load the json EPSG code for the country
with open(os.path.join(data_path, region_name+'_EPSG.pkl'), 'rb') as file:
        EPSG = pickle.load(file)
print(f'EPSG {EPSG}')

#path to file and check if it exists and save 1 or 0 for later
landcoverPath=os.path.join(data_path, f'landcover_{region_name}_EPSG{EPSG}.tif')
landcover=0 if not os.path.isfile(landcoverPath) and print('no landcover file') is None else 1
landcoverColoredPath=os.path.join(data_path, f'landcover_colored_{region_name}_EPSG{EPSG}.tif')
landcoverColored=0 if not os.path.isfile(landcoverColoredPath) and print('no landcover_colored file') is None else 1
demRasterPath = os.path.join(data_path, f'DEM_{region_name}_EPSG{EPSG}{resampled}.tif')
dem=0 if not os.path.isfile(demRasterPath) and print('no DEM file') is None else 1
regionPath =os.path.join(data_path, f'{region_name}_{EPSG}.geojson')
region = gpd.read_file(regionPath)

slope1RasterPath = os.path.join(data_from_DEM, f'slope_{region_name}_EPSG{EPSG}.tif')
slope1=0 if not os.path.isfile(slope1RasterPath) and print('no slope1 file') is None else 1
slopeRasterPath = os.path.join(data_from_DEM, f'slope_{region_name}_EPSG{EPSG}{resampled}.tif')
slope=0 if not os.path.isfile(slopeRasterPath) and print('no slope file') is None else 1
northfacingRasterPath = os.path.join(data_from_DEM, f'north_facing_{region_name}_EPSG{EPSG}{resampled}.tif')
nfacing=0 if not os.path.isfile(northfacingRasterPath) and print('no north facing pixels file') is None else 1
aspectRasterPath = os.path.join(data_from_DEM, f'aspect_{region_name}_EPSG{EPSG}{resampled}.tif')
aspect=0 if not os.path.isfile(aspectRasterPath) and print('no aspects file') is None else 1

coastlinesPath = os.path.join(data_path, f'goas_{region_name}_{EPSG}.gpkg')
coastlines=0 if not os.path.isfile(coastlinesPath) and print('no coastlines file') is None else 1
protectedAreasPath = os.path.join(data_path, f'protected_areas_{region_name}_{EPSG}.gpkg')
protectedAreas=0 if not os.path.isfile(protectedAreasPath) and print('no protected areas file') is None else 1
#OSM
roadsPath = os.path.join(data_path, f'OSM_roads_{region_name}_{EPSG}.gpkg')
roads=0 if not os.path.isfile(roadsPath) and print('no roads file') is None else 1
railwaysPath = os.path.join(data_path, f'OSM_railways_{region_name}_{EPSG}.gpkg')
railways=0 if not os.path.isfile(railwaysPath) and print('no railways file') is None else 1
airportsPath = os.path.join(data_path, f'OSM_airports_{region_name}_{EPSG}.gpkg')
airports=0 if not os.path.isfile(airportsPath) and print('no airports file') is None else 1
waterbodiesPath = os.path.join(data_path, f'OSM_waterbodies_{region_name}_{EPSG}.gpkg')
waterbodies=0 if not os.path.isfile(waterbodiesPath) and print('no waterbodies file') is None else 1

print('----------------------')

possible_filePaths = [
    regionPath, landcoverPath, landcoverColoredPath, demRasterPath,
    slope1RasterPath ,slopeRasterPath, northfacingRasterPath, aspectRasterPath,
    coastlinesPath, protectedAreasPath,
    roadsPath, airportsPath, waterbodiesPath, railwaysPath
    ]


# Initialize QGIS Application
QgsApplication.setPrefixPath(os.path.join("C:", "Program Files", "QGIS 3.36.3"), True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Define the QGIS project instance
project = QgsProject.instance()

# Specify the desired project CRS (example: EPSG:4326 - WGS 84)
project_crs = QgsCoordinateReferenceSystem(f"EPSG:{EPSG}")
project.setCrs(project_crs)

# List of file paths for vectors and rasters
file_paths = possible_filePaths

# Loop through the files and load them into QGIS
for file_path in file_paths:
    if os.path.isfile(file_path):
        layer_name = os.path.basename(file_path).split('.')[0]  # Extract layer name

        # Load vector files
        if file_path.endswith(('.geojson', '.gpkg', '.shp')):
            vector_layer = QgsVectorLayer(file_path, layer_name, "ogr")
            if vector_layer.isValid():
                project.addMapLayer(vector_layer)
                print(f"Loaded vector layer: {layer_name}")
            else:
                print(f"Failed to load vector layer: {file_path}")

        # Load raster files
        elif file_path.endswith(('.tif', '.img')):
            raster_layer = QgsRasterLayer(file_path, layer_name)
            if raster_layer.isValid():
                project.addMapLayer(raster_layer)
                print(f"Loaded raster layer: {layer_name}")
            else:
                print(f"Failed to load raster layer: {file_path}")


# Create a canvas and zoom to layers
canvas = QgsMapCanvas()
canvas.setLayers(project.mapLayers().values())  # Add all loaded layers to the canvas
canvas.zoomToFullExtent()  # Zoom to the extent of all layers

# Save the project (optional)
project.write(os.path.join(data_path,"all_files.qgz"))
print("QGIS project saved.")

# Exit QGIS
qgs.exitQgis()
