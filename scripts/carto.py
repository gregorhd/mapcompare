#!/usr/bin/env python3

"""Plot figure using cartopy's GeoAxes.add_geometries() interface to matplotlib.

Creates a cProfile of the renderFigure() function encompassing the core plottinh task.
The cProfile is dumped as a .prof in mapcompare/profiles/[viz_type]/[db_name]/) only if basemap=False. 
This is to avoid tile loading affecting performance measurement of the core plotting task.
"""

import os
import numpy as np
import contextily as ctx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from cartopy import crs as ccrs
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
from mapcompare.cProfile_viz import to_cProfile
import requests

outputdir = 'mapcompare/outputs/'
viz_type = 'static/' # type non-adjustable

# INPUTS
db_name = 'dd_subset' 
basemap = False
savefig = False


@to_cProfile
def renderFigure(buildings_in, buildings_out, rivers, basemap=basemap, savefig=savefig, db_name=db_name, viz_type=viz_type):

    def getBBox(*gdfs):
        """Return combined bbox of all GDFs in cartopy set_extent format (x0, x1, y0, y1).
        """

        list_of_bounds = []
        for gdf in gdfs:
            gdf_bounds = gdf.total_bounds
            list_of_bounds.append(gdf_bounds)
            
        xmin = np.min([item[0] for item in list_of_bounds])
        xmax = np.max([item[2] for item in list_of_bounds])
        ymin = np.min([item[1] for item in list_of_bounds])
        ymax = np.max([item[3] for item in list_of_bounds])
        
        carto_extent = [xmin, xmax, ymin, ymax]
        
        return carto_extent
    
    # Get number of features per GDF, to display in legend
    buildings_in_no = str(len(buildings_in.index))
    buildings_out_no = str(len(buildings_out.index))
    rivers_no = str(len(rivers.index))

    crs = ccrs.UTM(33)

    carto_extent = getBBox(buildings_in, buildings_out, rivers) # 8 secs

    fig, ax = plt.subplots(1, 1, subplot_kw={'projection': crs}, figsize=(20, 10))

    ax.set_extent(carto_extent, crs=crs)
    ax.set_title("Matplotlib interface: cartopy's .add_geometries()" + "\n", fontsize=20)
    
    # Add features to Axes with cartopy add_geometries()
    
    ax.add_geometries(buildings_in.geometry, crs, facecolor='red')
    ax.add_geometries(buildings_out.geometry, crs, facecolor='lightgrey', edgecolor='black', linewidth=0.1)
    ax.add_geometries(rivers.geometry, crs, facecolor='lightblue', edgecolor='blue', linewidth=0.25)

    if basemap:
        try:
            ctx.add_basemap(ax, crs=rivers.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
        except requests.HTTPError:
            print("Contextily: No tiles found. Zoom level likely too high. Setting zoom level to 13.")
            ctx.add_basemap(ax, zoom=13, crs=rivers.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
    else:
        pass
    
    # Legend

    buildings_in_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='red')]
    buildings_out_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightgrey', edgecolor='black', linewidth=0.5)]
    rivers_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightblue',edgecolor='blue', linewidth=0.25)]

    handles = buildings_in_handle + buildings_out_handle + rivers_handle 
    labels = ['Buildings within 500m (n=' + buildings_in_no + ')', 'Buildings outside 500m (n=' + buildings_out_no + ')', 'Rivers or streams (n=' + rivers_no + ')']

    leg = ax.legend(handles, labels, title=None, title_fontsize=14, fontsize=18, loc='best', frameon=True, framealpha=1)

    if savefig:
        if not os.path.exists(outputdir + viz_type):
            os.makedirs(outputdir + viz_type)

        plt.savefig(outputdir + viz_type + "cartopy (" + db_name + ").svg", format='svg', orientation='landscape')
    else:
        pass

if __name__ == "__main__":
    
    buildings_in, buildings_out, rivers = sql2gdf(db_name, password) 

    renderFigure(buildings_in, buildings_out, rivers)



