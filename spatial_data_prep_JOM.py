# -*- coding: utf-8 -*-
"""
created August 2024

@author: Jonas Meier


This script prepares raw spatial data for land exclusion in GLAES or ATLITE.
The raw inputs should be downloaded to /Raw_Spatial_Data before execution. Alternatively, the openEO API can be used to download data automatically.
The outputs are saved in /data.

compare boundaries between different data sources: https://www.geoboundaries.org/visualize.html?country=DEU&mainSource=OSM-Boundaries&comparisonSource=geoBoundaries+%28Open%29&mainLevel=2&comparisonLevel=2
This script uses administrative boundries from GADM.org via pygadm
"""

import time
import os
import geopandas as gpd
import json
import pickle
import yaml
import rasterio
import numpy as np
import pygadm
import openeo
from rasterio.mask import mask
from shapely.geometry import mapping
from unidecode import unidecode
from rasterio.warp import calculate_default_transform, reproject, Resampling
import richdem
from utils.data_preprocessing import *

#https://www.earthenv.org/topography


#-------data config------- 
landcover_dem_source = 'file'   #'file' or 'openeo'
consider_railways = 0
consider_roads = 0
consider_airports = 0
consider_waterbodies = 0 
EPSG_manual = ''  #if None use empty string
#----------------------------
############### Define study region ############### use geopackage from gadm.org to inspect in QGIS
region_name='Elbe-Elster' #always needed (if country is studied, then use country name)

OSM_folder_name = 'BerlinBrandenburg' #usually same as country_code, only needed if OSM is to be considered

#use GADM boundary
country_code='DEU' #    #PRT  #Städteregion Aachen in level 2 #Porto in level 1 #Elbe-Elster in level 2 #Zell am See in level 2
gadm_level=2
#or use custom region
custom_polygon_filename = '' #if None use empty string           'Aceh_single.geojson'
##################################################


# Record the starting time
start_time = time.time()

# Get paths to data files or folders
dirname = os.path.dirname(__file__)
data_path = os.path.join(dirname, 'Raw_Spatial_Data')
landcoverRasterPath = os.path.join(data_path, "PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326.tif")
demRasterPath = os.path.join(data_path, 'DEM','gebco_cutout.tif')
if consider_railways == 1 or consider_roads == 1 or consider_airports == 1 or consider_waterbodies == 1:
    OSM_country_path = os.path.join(data_path, 'OSM', OSM_folder_name) 


# Get region name without accents, spaces, apostrophes, or periods for saving files
region_name_clean = unidecode(region_name)
region_name_clean = region_name_clean.replace(" ", "")
region_name_clean = region_name_clean.replace(".", "")
region_name_clean = region_name_clean.replace("'", "")


# Define output directories
glaes_output_dir = os.path.join(dirname, 'data', f'{region_name_clean}')
os.makedirs(glaes_output_dir, exist_ok=True)


print("Prepping " + region_name + "...")


#get region boundary
if custom_polygon_filename:
    custom_polygon_filepath = os.path.join('Raw_Spatial_Data','custom_polygon', custom_polygon_filename)
    region = gpd.read_file(custom_polygon_filepath)
elif gadm_level==0:
    gadm_data = pygadm.Items(admin=country_code)
    region = gadm_data
    region.set_crs('epsg:4326', inplace=True) #pygadm lib extracts information from the GADM dataset as GeoPandas GeoDataFrame. GADM.org provides files in coordinate reference system is longitude/latitude and the WGS84 datum.
else:
    gadm_data = pygadm.Items(admin=country_code, content_level=gadm_level)
    region = gadm_data.loc[gadm_data[f'NAME_{gadm_level}']==region_name]
    region.set_crs('epsg:4326', inplace=True) #pygadm lib extracts information from the GADM dataset as GeoPandas GeoDataFrame. GADM.org provides files in coordinate reference system is longitude/latitude and the WGS84 datum.
print(f'region geojson loaded CRS: {region.crs}')
region.to_file(os.path.join(glaes_output_dir, f'{region_name_clean}_4326.geojson'), driver='GeoJSON', encoding='utf-8')


# calculate UTM zone based on representative point of country 
representative_point = region.representative_point().iloc[0]
latitude, longitude = representative_point.y, representative_point.x
EPSG = int(32700 - round((45 + latitude) / 90, 0) * 100 + round((183 + longitude) / 6, 0))
#if EPSG was set manual in the beginning then use that one
if EPSG_manual:
    EPSG=int(EPSG_manual)

print(f'CRS to be used: {EPSG}')
with open(os.path.join(glaes_output_dir, f'{region_name_clean}_EPSG.pkl'), 'wb') as file:
    pickle.dump(EPSG, file)

# reproject country to defined projected CRS
region.to_crs(epsg=EPSG, inplace=True) 
print(f'region projected to defined CRS: {region.crs}')
region.to_file(os.path.join(glaes_output_dir, f'{region_name_clean}_{EPSG}.geojson'), driver='GeoJSON', encoding='utf-8')

# #calculate bounding box with 1000m buffer (region needs to be in projected CRS so meters are the unit)
# region_copy = region
# region_copy['buffered']=region_copy.buffer(1000)
# # Convert buffered region back to EPSC 4326 to get bounding box latitude and longitude 
# region_buffered_4326 = region_copy.set_geometry('buffered').to_crs(epsg=4326)
# bounding_box = region_buffered_4326['buffered'].total_bounds 
# print(f"Bounding box: \nminx: {bounding_box[0]}, miny: {bounding_box[1]}, maxx: {bounding_box[2]}, maxy: {bounding_box[3]}")

# Convert region back to EPSC 4326 to trim raster files
region.to_crs(epsg=4326, inplace=True)


if consider_railways == 1:
    print('processing railways')
    OSM_file = gpd.read_file(os.path.join(OSM_country_path, f'gis_osm_railways_free_1.shp'))
    OSM_railways = OSM_clip_reproject(OSM_file, region, EPSG)
    # Check if OSM_airports is not empty before saving
    if not OSM_railways.empty:
        OSM_railways.to_file(os.path.join(glaes_output_dir, f'OSM_railways_{region_name_clean}_{EPSG}.geojson'), driver='GeoJSON', encoding='utf-8')
    else:
        print("No railways found in the region. File not saved.")

if consider_roads == 1:
    print('processing roads')
    OSM_file = gpd.read_file(os.path.join(OSM_country_path, f'gis_osm_roads_free_1.shp'))
    OSM_roads = OSM_clip_reproject(OSM_file, region, EPSG)
    #filter roads. see https://www.geofabrik.de/data/geofabrik-osm-gis-standard-0.7.pdf page19
    OSM_roads_filtered = OSM_roads[OSM_roads['code'].isin([5111, 5112, 5113, 5114, 5115, 5121, 5122, 5125, 5131, 5132, 5133, 5134, 5135])]
    #OSM_roads_clipped_filtered = OSM_roads_clipped[~OSM_roads_clipped['code'].isin([5141])] #keep all roads except with code listed (eg 5141)
    #reset index for clean, zero-based index of filtered data
    OSM_roads_filtered.reset_index(drop=True, inplace=True)
    #save file
    OSM_roads_filtered.to_file(os.path.join(glaes_output_dir, f'OSM_roads_{region_name_clean}_{EPSG}.geojson'), driver='GeoJSON', encoding='utf-8')

if consider_airports == 1:
    print('processing airports')
    OSM_file = gpd.read_file(os.path.join(OSM_country_path, f'gis_osm_transport_a_free_1.shp'))
    OSM_transport = OSM_clip_reproject(OSM_file, region, EPSG) #all transport fclasses from the OSM file 
    OSM_airports = OSM_transport[OSM_transport['code'].isin([5651, 5652])] #5651: large airport, 5652: small airport or airfield
    # Check if OSM_airports is not empty before saving
    if not OSM_airports.empty:
        OSM_airports.to_file(os.path.join(glaes_output_dir, f'OSM_airports_{region_name_clean}_{EPSG}.geojson'), driver='GeoJSON', encoding='utf-8')
    else:
        print("No airports found in the region. File not saved.")

if consider_waterbodies == 1:
    print('processing waterbodies')
    OSM_file = gpd.read_file(os.path.join(OSM_country_path, f'gis_osm_water_a_free_1.shp'))
    OSM_waterbodies = OSM_clip_reproject(OSM_file, region, EPSG) #all transport fclasses from the OSM file 
    OSM_waterbodies_filtered = OSM_waterbodies[OSM_waterbodies['code'].isin([8200, 8201, 8202])] #8200: unspecified waterbodies like lakes, 8201: reservoir, 8202: river
    # Check if OSM_waterbodies_filtered is not empty before saving
    if not OSM_waterbodies_filtered.empty:
        OSM_waterbodies_filtered.to_file(os.path.join(glaes_output_dir, f'OSM_waterbodies_{region_name_clean}_{EPSG}.geojson'), driver='GeoJSON', encoding='utf-8')
    else:
        print("No waterbodies found in the region. File not saved.")

    


print('landcover')
if landcover_dem_source == 'openeo':
    connection = openeo.connect(url="openeo.dataspace.copernicus.eu").authenticate_oidc()

    output_path = os.path.join(glaes_output_dir, f'landcover_{region_name_clean}_EPSG{EPSG}.tif')

    with open(os.path.join(glaes_output_dir, f'{region_name_clean}_4326.geojson'), 'r') as file: #use region file in EPSG 4326 because openeo default file is in 4326
        aoi = json.load(file)

    datacube_landcover = connection.load_collection("ESA_WORLDCOVER_10M_2021_V2")
    #clip landcover directly to area of interest 
    masked_datacube = datacube_landcover.mask_polygon(aoi)
    #reproject landcover to EPSG 32633 and dont change resolution thereby
    landcover = masked_datacube.resample_spatial(projection=EPSG, resolution=0) #resolution=0 does not change resolution
    #download
    landcover.download(output_path)

if landcover_dem_source == 'file':
    clip_reproject_raster(landcoverRasterPath, region_name_clean, region, 'landcover', EPSG, 'nearest', glaes_output_dir)


print('DEM') #block comment: SHIFT+ALT+A, multiple line comment: STRG+#
try:
    # test to use DEM data via openeo, only works when land cover is also fetched from openEO because DEM is co-registered on the back-end to the landcover 
    # (current implementation: use GEBCO DTM file)
    # if landcover_dem_source == 'openeo':
    #     connection = openeo.connect(url="openeo.dataspace.copernicus.eu").authenticate_oidc()

    #     output_path = os.path.join(glaes_output_dir, f'DEM_{region_name_clean}_EPSG{EPSG}_resampled.tif')

    #     with open(os.path.join(glaes_output_dir, f'{region_name_clean}_4326.geojson'), 'r') as file: #use region file in EPSG 4326 because openeo default file is in 4326
    #         aoi = json.load(file)

    #     datacube_dem = connection.load_collection("COPERNICUS_30")
    #     #clip dem directly to area of interest 
    #     masked_datacube = datacube_dem.mask_polygon(aoi)
    #     #co-register dem with landcover (same projection, same resolution, same origin)
    #     dem_registered = masked_datacube.resample_cube_spatial(landcover, method = 'bilinear')
    #     #download
    #     dem_registered.download(output_path)
    
    # if landcover_dem_source == 'file':

    clip_reproject_raster(demRasterPath, region_name_clean, region, 'DEM', EPSG, 'bilinear', glaes_output_dir)

    #reproject and match resolution of DEM to landcover data
    infile=os.path.join(glaes_output_dir, f'DEM_{region_name_clean}_EPSG{EPSG}.tif')
    match=os.path.join(glaes_output_dir, f'landcover_{region_name_clean}_EPSG{EPSG}.tif')
    outfile=os.path.join(glaes_output_dir, f'DEM_{region_name_clean}_EPSG{EPSG}_resampled.tif')
    reproj_match(infile, match, 'bilinear', outfile)


    #create slope map (https://www.earthdatascience.org/tutorials/get-slope-aspect-from-digital-elevation-model/)
    dem_file = richdem.LoadGDAL(os.path.join(glaes_output_dir, f'DEM_{region_name_clean}_EPSG{EPSG}_resampled.tif'))
    slope = richdem.TerrainAttribute(dem_file, attrib='slope_degrees')
    richdem.SaveGDAL(os.path.join(glaes_output_dir, f'slope_{region_name_clean}_EPSG{EPSG}_resampled.tif'), slope)

    #create aspect map (https://www.earthdatascience.org/tutorials/get-slope-aspect-from-digital-elevation-model/)
    dem_file = richdem.LoadGDAL(os.path.join(glaes_output_dir, f'DEM_{region_name_clean}_EPSG{EPSG}_resampled.tif'))
    aspect = richdem.TerrainAttribute(dem_file, attrib='aspect')
    richdem.SaveGDAL(os.path.join(glaes_output_dir, f'aspect_{region_name_clean}_EPSG{EPSG}_resampled.tif'), aspect)

    #create map showing pixels with slope bigger X and aspect between Y and Z (north facing with slope where you would not build PV)
    condition = (slope > 10) & ((aspect >= 310) | (aspect <= 50))
    result = np.where(condition, 1, 0) # Create a new raster with the filtered results
    with rasterio.open(os.path.join(glaes_output_dir, f'slope_{region_name_clean}_EPSG{EPSG}_resampled.tif')) as src:
        slope = src.read(1)
        profile = src.profile
    profile.update(dtype=rasterio.float32, count=1, nodata=0) # Update the profile for the output raster
    
    if result.sum() > 0:
        # Write the result to a new raster file
        with rasterio.open(os.path.join(glaes_output_dir, f'north_facing_{region_name_clean}_EPSG{EPSG}_resampled.tif'), 'w', **profile) as dst:
            dst.write(result.astype(rasterio.float32), 1)
    if result.sum() == 0:
        print('no north-facing pixel exceeding threshold slope')

except Exception as e:
    print(e)
    print('Something went wrong with DEM')


#save all files also into one geopackage



print("Done!")

