#!/usr/bin/env python3

"""Reduced code sample to plot figure using GeoPandas' GeoDataFrame.plot() interface to matplotlib.
"""

import numpy as np
import contextily as ctx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from cartopy import crs as ccrs
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password


# INPUTS
db_name = 'dd_subset' 

def getExtent(*gdfs):
    """Return combined bbox of all GDFs in cartopy set_extent format (x0, x1, y0, y1).
    """

    list_of_bounds = [gdf.total_bounds for gdf in gdfs]
        
    xmin = np.min([item[0] for item in list_of_bounds])
    xmax = np.max([item[2] for item in list_of_bounds])
    ymin = np.min([item[1] for item in list_of_bounds])
    ymax = np.max([item[3] for item in list_of_bounds])
    
    extent = [xmin, xmax, ymin, ymax]
    
    return extent

if __name__ == "__main__":

    gdf1, gdf2, gdf3 = sql2gdf(db_name, password)

    extent = getExtent(gdf1, gdf2, gdf3)

    crs = ccrs.UTM(33)

    fig, ax = plt.subplots(1, 1, subplot_kw={'projection': crs}, figsize=(20, 10))

    ax.set_extent(extent, crs=crs)
    ax.set_title("Matplotlib interface: GeoPandas' .plot()" + "\n", fontsize=20)
    
    # Add features to Axes
    
    gdf1.plot(ax=ax, facecolor='red')
    gdf2.plot(ax=ax, facecolor='lightgrey', edgecolor='black', linewidth=0.1)
    gdf3.plot(ax=ax, facecolor='lightblue', edgecolor='blue', linewidth=0.25)
   
    ctx.add_basemap(ax, crs=gdf3.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
    
    # Legend

    gdf1_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='red')]
    gdf2_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightgrey', edgecolor='black', linewidth=0.5)]
    gdf3_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightblue', edgecolor='blue', linewidth=0.25)]

    handles = gdf1_handle + gdf2_handle + gdf3_handle 
    labels = ['Label1', 'Label2', 'Label3']

    ax.legend(handles, labels, title=None, title_fontsize=14, fontsize=18, loc='best', frameon=True, framealpha=1)
    



