"""Identify which DEM tiles (called 'DGMs' in the German sample dataset) overlap with the study area and return handles to serve as alternative basemap.

1m and 20m DEMs are available though the latter are preferred for performance reasons - therefore no high-level option implemented yet for showDEMs() to more easily choose between the two.
"""

import os
import csv
import itertools
import numpy as np
import rasterio as rio
import functools
import time

def timer(func):
    """Print runtime of decorated function courtesy of RealPython's Primer on Python Decorators: https://realpython.com/primer-on-python-decorators/"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter() #1
        value = func(*args, **kwargs)
        end_time = time.perf_counter() #2
        run_time = end_time - start_time #3
        print(f"\nFinished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer

# final_DGM1s = findDGM1s('01_data/02_DEM/', [412726.674, 418389.897, 5654188.856, 5657723.719])

@timer
def showDEMs(csvpath, data_dir, carto_extent, ax, crs):
    """Find all DEMs overlapping with GDF-derived plotting extent and return normalised Axes.imshow for each."""
    
    def findDGM1s(directory, extent):
        """Return list of tuples with ((filename), (bottom-left), (top-right)) for the 1m DGM1 rasters overlapping with the study area.
        
        Not utilised as too costly. 

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

    def findDGM20s(csvpath, extent):
        """Return .xyz filenames for 20m DGM20 rasters overlapping with the GDF-derived plotting extent.

        Parameters
        ----------
        path : str
            The absolute path to the single metadata CSV for DGM20 rasters.
        extent : list
            Cartopy set_extent list in format x0, x1, y0, y1.
        Returns
        ----------
        rast_list : list
            List of tuples with ((filename), (bottom-left), (top-right)) for the DGM1 rasters overlapping with the study area.
        """
        tilenum_bbox_all = []
        with open(csvpath, "r") as file_obj:
            data = csv.reader(file_obj, delimiter=";")
            next(data) # skip header
            for row in data:
                tile_num = row[0]
                bbox = list(map(int, row[1].split())) # str to ints
                tilenum_bbox_all.append((tile_num, bbox))

        tile_selection = []
        for tile in tilenum_bbox_all:
            bl = (tile[1][0], tile[1][1]) # bottom-left corner
            tr = (tile[1][2], tile[1][3]) # top-right corner
            if bl[0] >= extent[1] or extent[0] >= tr[0]:
                continue # TRUE = no left-right overlap
            if bl[1] >= extent[3] or extent[2] >= tr[1]:
                continue # TRUE = no top-bottom overlap
            else:
                tile_num = tile[0]
                filename = '33' + tile_num + '_dgm20.xyz'
                tile_selection.append((filename))
                
        return  tile_selection

    tile_selection = findDGM20s(csvpath, carto_extent)

    def getVMinMax(tile_selection):
        """Return vmin, vmax across tile selection to normalize cmap
        
            ***Any other way to avoid reading each selected tile twice?***
        """
        
        vmins = []
        vmaxs = []

        for tile in tile_selection:
            with rio.open(data_dir + tile) as dataset:
                img = dataset.read()
                img_vmin = np.amin(img)
                img_vmax = np.amax(img)
                vmins.append(img_vmin)
                vmaxs.append(img_vmax)
        
        _vmin = np.amin(vmins)
        _vmax = np.amin(vmaxs)
        return _vmin, _vmax
   
    _vmin, _vmax = getVMinMax(tile_selection)

    for tile in tile_selection:
        with rio.open(data_dir + tile) as dataset:
            img = dataset.read()
            img_extent = [dataset.bounds[0], dataset.bounds[2], dataset.bounds[1], dataset.bounds[3]]
            handle = ax.imshow(img[0], transform=crs, cmap='Greens', vmin=_vmin, vmax=_vmax, extent=img_extent)
    
    return handle, ax