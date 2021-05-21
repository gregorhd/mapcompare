import os
import csv
import itertools
import numpy as np
import rasterio as rio

def findDGM1s(directory, extent):
    """Return list of tuples with ((filename), (bottom-left), (top-right)) for the DGM1 rasters overlapping with the study area.
        
    Overlap check similar to: https://stackoverflow.com/questions/65648225/how-to-find-overlapping-and-inner-bounding-boxes-from-a-outer-bounding-box

    Parameters
    ----------
    directory : str
        The directory the CSVs are in.
    extent : list
        Cartopy set_extent list in format x0, x1, y0, y1.
    Returns
    ----------
    rast_list : list
        List of tuples with ((filename), (bottom-left), (top-right)) for the DGM1 rasters overlapping with the study area.
    """
    def csv_reader(file_obj):
        """Parses the 2-line csv files for DGM1 rasters."""
        reader = csv.reader(file_obj, delimiter=";")
        string = itertools.islice(reader, 1, 2) # reads line 2
        for item in string:
            return item[1] # returns second element of line 2
        return bbox_strings

    bboxes_raw = dict() # dict incl {'filename': (minx, miny, maxx, maxy)}
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            with open(directory + filename, newline='') as file_obj:
                bbox_strings = csv_reader(file_obj)
                bbox = list(map(int, bbox_strings.split()))
                bboxes_raw[filename] = bbox
    
    bboxes = [] # list of tuples incl (filename, (minx, miny), (maxx, maxy))
    for kv in list(bboxes_raw.items()): 
        p0 = tuple((kv[1][0], kv[1][1])) # bottom left
        p1 = tuple((kv[1][2], kv[1][3])) # top right
        bboxes.append((kv[0], p0, p1))
    
    rast_list = []
    for bbox in bboxes:
        bl = bbox[1]
        tr = bbox[2]
        if bl[0] >= extent[1] or extent[0] >= tr[0]:
            continue
        if bl[1] >= extent[3] or extent[2] >= tr[1]:
            continue
        else:
            rast_list.append((bbox))
            
    return rast_list

def findDGM20s(path, extent):
    """Return list of tuples with ((filename), (bottom-left), (top-right)) for the DGM20 rasters overlapping with the study area.
        
    Overlap check similar to: https://stackoverflow.com/questions/65648225/how-to-find-overlapping-and-inner-bounding-boxes-from-a-outer-bounding-box

    Parameters
    ----------
    path : str
        The absolute path to the single CSV.
    extent : list
        Cartopy set_extent list in format x0, x1, y0, y1.
    Returns
    ----------
    rast_list : list
        List of tuples with ((filename), (bottom-left), (top-right)) for the DGM1 rasters overlapping with the study area.
    """
    bboxes_raw = dict() # dict incl {'filename': (minx, miny, maxx, maxy)}
    with open(path, "r") as file_obj:
        data = csv.reader(file_obj, delimiter=";")
        next(data) # skip header
        for row in data:
            bbox = list(map(int, row[1].split())) # str to ints
            bboxes_raw[row[0]] = bbox
    
    bboxes = [] # list of tuples incl (filename, (minx, miny), (maxx, maxy))
    for kv in list(bboxes_raw.items()): 
        p0 = tuple((kv[1][0], kv[1][1])) # bottom left
        p1 = tuple((kv[1][2], kv[1][3])) # top right
        bboxes.append((kv[0], p0, p1))
    
    rast_list = []
    for bbox in bboxes:
        bl = bbox[1]
        tr = bbox[2]
        if bl[0] >= extent[1] or extent[0] >= tr[0]:
            continue
        if bl[1] >= extent[3] or extent[2] >= tr[1]:
            continue
        else:
            rast_list.append((bbox))
            
    return rast_list

# final_DGM1s = findDGM1s('01_data/02_DEM/', [412726.674, 418389.897, 5654188.856, 5657723.719])

rast_list = findDGM20s(r'c:\Users\grego\OneDrive\01_GIS\11_MSc\00_Project\01_data\02_DEM\DGM20\dgm25_akt.csv', [412726.674, 418389.897, 5654188.856, 5657723.719])

file_list = []

for tile in rast_list:
    tile_num = tile[0]
    filename = '33' + tile_num + '_dgm20.xyz'
    file_list.append(filename)

directory = '01_data/02_DEM/DGM20/'

# find min max

def showDEMs(file_list, ax, crs):
    
    def getVMinMax(file_list):
        
        vmins = []
        vmaxs = []

        for file in file_list:
            with rio.open(directory + file) as dataset:
                img = dataset.read()
                img_vmin = np.amin(img)
                img_vmax = np.amax(img)
                vmins.append(img_vmin)
                vmaxs.append(img_vmax)
        
        _vmin = np.amin(vmins)
        _vmax = np.amin(vmaxs)
        return _vmin, _vmax
   
    _vmin, _vmax = getVMinMax(file_list)

    for file in file_list:
        with rio.open(directory + file) as dataset:
            img = dataset.read()
            img_extent = [dataset.bounds[0], dataset.bounds[2], dataset.bounds[1], dataset.bounds[3]]
            
            handle = ax.imshow(img[0], transform=crs, cmap='Greens_r', vmin=_vmin, vmax=_vmax, extent=img_extent)
    
    return handle, ax
        



