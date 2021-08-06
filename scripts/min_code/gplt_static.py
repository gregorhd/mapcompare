#!/usr/bin/env python3

"""Reduced code sample to plot figure using geoplot's polyplot() interface to matplotlib.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geoplot as gplt
import geoplot.crs as gcrs
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password

# INPUTS
db_name = 'dd_subset' 


def prepGDFs(*gdfs):
    """Convert GDFs to geographic coordinates as expected by geoplot and calculates the combined bounding box (extent) of all GDFs.
    """
    gdfs = [gdf.to_crs(epsg=4326) for gdf in gdfs]

    list_of_bounds = [gdf.total_bounds for gdf in gdfs]
                
    xmin = np.min([item[0] for item in list_of_bounds])
    xmax = np.max([item[2] for item in list_of_bounds])
    ymin = np.min([item[1] for item in list_of_bounds])
    ymax = np.max([item[3] for item in list_of_bounds])
        
    # geoplot order different from cartopy order
    extent = [xmin, ymin, xmax, ymax]

    return (gdfs, extent)

if __name__ == "__main__":

    buildings_in, buildings_out, rivers = sql2gdf(db_name, password) 

    ((buildings_in, buildings_out, rivers), extent) = prepGDFs(buildings_in, buildings_out, rivers)
    
    ax = gplt.webmap(buildings_in, extent=extent, projection=gcrs.WebMercator(), figsize=(20, 10))
    gplt.polyplot(buildings_in, ax=ax, facecolor='red', zorder=3)
    gplt.polyplot(buildings_out, ax=ax, facecolor='lightgrey', edgecolor='black', linewidth=0.1, zorder=2)
    gplt.polyplot(rivers, ax=ax, facecolor='lightblue', edgecolor='blue', linewidth=0.25, zorder=1)

    gdf1_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='red')]
    gdf2_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightgrey', edgecolor='black', linewidth=0.5)]
    gdf3_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightblue',edgecolor='blue', linewidth=0.25)]

    handles = gdf1_handle + gdf2_handle + gdf3_handle 
    labels = ['Label1', 'Label2', 'Label3']

    ax.legend(handles, labels, title=None, title_fontsize=14, fontsize=18, loc='best', frameon=True, framealpha=1)
