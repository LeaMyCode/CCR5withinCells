# -*- coding: utf-8 -*-
"""
Created on Thu Mar  6 07:11:07 2025

@author: leaga
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 07:25:58 2024

@author: leaga
"""



# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 08:43:08 2021

@author: leaga
"""

import numpy as np
from tkinter import filedialog
import math
import os
import csv
import pandas as pd
import statistics
from read_roi import read_roi_zip
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from skimage import io
from shapely.geometry import Polygon, MultiPolygon

####################################################################################################################################
#
# Please enter your resolution!
#
####################################################################################################################################

global resolution 
resolution = 0.0930159

####################################################################################################################################
#
# Please ensure the channel are correctly set
#
####################################################################################################################################

CCR5_channel = 2

####################################################################################################################################
#
# Functions
#
####################################################################################################################################

#get the header of your file names to identify connected data
def fileNameGetter(s):
    name = s.split('.czi')
    new_name = name[0]+ ".czi"
    new_name.rstrip()
    return new_name

# Read the coordintates for each ROI in your ROIs
def readRoi(roi_zip_path):
    # Create a list to store the result
    roi_list = []
    
    #open the rois
    rois = read_roi_zip(roi_zip_path)

    for key, value in rois.items():
        xy_pairs = [[float(x), float(y)] for x, y in zip(value['x'], value['y'])]
        roi_list.append(xy_pairs)
        
    
    return roi_list

# Helper function to extract pixel values inside a polygon
def get_intensity_values(polygon, intensity_image):
    # Create a mask for the polygon
    min_x, min_y, max_x, max_y = map(int, polygon.bounds)  # Get bounding box
    
    # Clip bounds to ensure they fit within the image dimensions
    min_x = max(min_x, 0)
    min_y = max(min_y, 0)
    max_x = min(max_x, intensity_image.shape[1] - 1)  # Limit to image width (columns)
    max_y = min(max_y, intensity_image.shape[0] - 1)  # Limit to image height (rows)

    mask = np.zeros_like(intensity_image, dtype=bool)

    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            if polygon.contains(Polygon([(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)])):
                mask[y, x] = True  # Flip to match numpy's row-col indexing (y first)

    return intensity_image[mask]

####################################################################################################################################
#
# MAIN
#
####################################################################################################################################


root_path = filedialog.askdirectory(title="Please select your folder with images to analyze")


for condition_folder in os.listdir(root_path):
    
    #create dir for your condition results
    results_path_condition = os.path.join(root_path,"Analysis")
    if not os.path.exists(results_path_condition):
        os.makedirs(results_path_condition)
        
    if condition_folder == "Analysis":
        continue
    
    condition_path = os.path.join(root_path,condition_folder)
    print("Condition folder : ", condition_folder)
    
    #initialize analysis factors and set to zero for each condition --> summarized data  
    data = {
            'file': [],
            'area_microglia': [],
            'total_CCR5_area' : [],
            'CCR5_area_microglia': [],
            'CCR5_puncta_microglia' : [],
            'CCR5_puncta_microglia_norm': [],
            'total_CCR5_puncta' : [],
            'total_CCR5_puncta_norm' : [],
            'total_mean_int' : [],
            'mean_int_microglia' : [],
            'total_IntDen' : [],
            'IntDen_microglia' : []
    
        }
    


    for round_folder in os.listdir(condition_path):
        
        if round_folder == "Analysis":
            continue

        cells_path = os.path.join(condition_path,round_folder)
            
  
        print("Round folder: ", round_folder)

        
        for files in os.listdir(cells_path):
            if files == "Analysis":
                continue
             
            # ensure to have each cell only once
            if not files.endswith("-CCR5_ROI.zip"):
                continue
            
            
            #get your files header to identify connected data
            file_header = fileNameGetter(files)
            print("file_header: ", file_header)
            
            # Load the 3-channel image to calculate the intensities of the staining
            #file_image = file_header.split(".tif")[0]
            image = io.imread(os.path.join(cells_path, str(file_header + ".tif")))
            CCR5_image = image[:,:,CCR5_channel]
            
            whole_img_intensity = np.mean(CCR5_image)
            
            area_img = CCR5_image.size 
            area_img *= (resolution * resolution)

            
            
            #load rois, structure: [[[x,y][x,y]],[[x,y][x,y]]]
            mg_rois = readRoi(os.path.join(cells_path, str(file_header + "-MG_ROI.zip")))
            print("Microglia rois: ", len(mg_rois))
            CCR5_rois = readRoi(os.path.join(cells_path, str(file_header + "-CCR5_ROI.zip")))
            print("CCR5 rois: ", len(CCR5_rois))
            
            #calculate the area of the microglia
            # Create individual polygons for each ROI
            mg_polygons = [Polygon(roi) for roi in mg_rois]   
            
            mg_area = 0
            for mg in mg_polygons:
                mg_area += mg.area * (resolution*resolution)
                   
            
            # Define the minimum and maximum area limits for CCR5 ROIs
            min_size = 2
            max_size = 200
            
            # Convert AT8 ROIs to polygons or points and filter by area
            filtered_CCR5_polygons = []
            for roi in CCR5_rois:
                # Create Polygon or Point based on the ROI structure
                CCR5_polygon = Polygon(roi) if len(roi) > 2 else Point(roi[0])
                
                # Calculate area if it's a polygon
                CCR5_area = CCR5_polygon.area if isinstance(CCR5_polygon, Polygon) else 0
                
                # Filter based on size limits
                if min_size <= CCR5_area <= max_size:
                    filtered_CCR5_polygons.append(CCR5_polygon)
            
            #Get the total amount of CCR5 count
            CCR5_count = len(filtered_CCR5_polygons)
            
            
            # Initialize counters and area accumulators
            CCR5_in_mg_count = 0
            CCR5_in_mg_area = 0
            
            
            
            # Calculate the total CCR5 area
            CCR5_total_area = sum(polygon.area for polygon in filtered_CCR5_polygons)
            
            mg_intensities_CCR5 = []
            
            # Check which CCR5 ROIs are inside the dendrites and accumulate the area
            for mg_polygon in mg_polygons:
                # Get intensity values inside the ROI
                roi_intensity_values = get_intensity_values(mg_polygon, CCR5_image)
                mg_intensities_CCR5.append(np.mean(roi_intensity_values))
                
                for CCR5 in filtered_CCR5_polygons:
                    try:
                        if mg_polygon.contains(CCR5):
                            CCR5_in_mg_count += 1
                            CCR5_in_mg_area += CCR5.area
                            
                    except:
                        print(f'In one of the mgs of {file_header} is no hyperphos punct.')
                        
            
            # Multiply areas by resolution if necessary (for scaling units)
            CCR5_in_mg_area *= (resolution * resolution)
            
            
            # fill the dicitionary for saving
            data['file'].append(file_header)
            data['area_microglia'].append(mg_area)
            data['CCR5_area_microglia'].append(CCR5_in_mg_area/mg_area)
            data['CCR5_puncta_microglia'].append(CCR5_in_mg_count)
            data['CCR5_puncta_microglia_norm'].append(CCR5_in_mg_count/mg_area)
            
            data['total_CCR5_puncta'].append(CCR5_count)
            data['total_CCR5_puncta_norm'].append(CCR5_count/area_img)
            data['total_CCR5_area'].append(CCR5_total_area/area_img)
            
            data['total_mean_int'].append(whole_img_intensity)
            data['mean_int_microglia'].append(np.mean(mg_intensities_CCR5))
            
            data['total_IntDen'].append(whole_img_intensity*area_img)
            data['IntDen_microglia'].append(np.mean(mg_intensities_CCR5)*mg_area)
            
            

        
    #write condition data to .csv --> summary of all data
    
    df_data = pd.DataFrame(data)
    df_data.to_csv(results_path_condition + fr'/CCR5_MG_data_{condition_folder}.csv', index=False)

    

   


  
            
            
            
   





    
    
    

 