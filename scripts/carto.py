#!/usr/bin/env python3

"""Plot figure using cartopy's GeoAxes.add_geometries() interface to matplotlib.

Create a cProfile of the renderFigure() function encompassing the core plotting task.
The cProfile is dumped as a .prof in mapcompare/profiles/[viz_type]/[db_name]/) only if basemap=False and savefig=False. 
This is to avoid tile loading or writing to disk affecting performance measurement of the core plotting task.
"""

import os
import sys
import importlib
import numpy as np
import contextily as ctx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from cartopy import crs as ccrs
from geopandas import GeoDataFrame
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
import requests
importlib.reload(sys.modules['mapcompare.cProfile_viz']) # no kernel/IDE restart needed after editing cProfile_viz.py
from mapcompare.cProfile_viz import to_cProfile

outputdir = 'mapcompare/outputs/'
viz_type = 'static/' # type non-adjustable

# INPUTS
db_name = 'dd_subset' 
basemap = True
savefig = False


def getExtent(*gdfs: GeoDataFrame) -> list:
    """Return combined bbox of all GDFs in cartopy set_extent format (x0, x1, y0, y1).

    This step is separated from actual rendering to not affect performance measurement.
    """

    list_of_bounds = [gdf.total_bounds for gdf in gdfs]
        
    xmin = np.min([item[0] for item in list_of_bounds])
    xmax = np.max([item[2] for item in list_of_bounds])
    ymin = np.min([item[1] for item in list_of_bounds])
    ymax = np.max([item[3] for item in list_of_bounds])
    
    extent = [xmin, xmax, ymin, ymax]
    
    return extent


@to_cProfile
def renderFigure(*gdfs: GeoDataFrame, basemap: bool=basemap, savefig: bool=savefig, db_name: str=db_name, viz_type: str=viz_type) -> None:
    """Renders the figure reproducing the map template.

    Parameters
    ----------
    buildings_in, buildings_out, rivers : GeoDataframes
        The three feature sets styled and added separately to the figure.
    basemap : Boolean
        Global scope variable determining whether or not to add an OSM basemap.
    savefig : Boolean
        Global scope variable determining whether or not to save the current figure to SVG in /mapcompare/outputs/[viz_type]
    db_name : {'dd', 'dd_subset'}
        Global scope variable indicating the source PostGIS database to be used, 'dd' being the complete dataset and 'dd_subset' the subset.
    viz_type : {'static/', 'interactive/'}
        Global scope variable indicating the visualisation type.
    
    Returns
    ----------
        A figure reproducing the map template.
    """
    
    crs = ccrs.UTM(33)

    fig, ax = plt.subplots(1, 1, subplot_kw={'projection': crs}, figsize=(20, 10))

    ax.set_extent(extent, crs=crs)
    ax.set_title("Matplotlib interface: cartopy's .add_geometries()" + "\n", fontsize=20)
    
    # Add features to Axes with cartopy add_geometries()
    
    ax.add_geometries(gdfs[0].geometry, crs, facecolor='red')
    ax.add_geometries(gdfs[1].geometry, crs, facecolor='lightgrey', edgecolor='black', linewidth=0.1)
    ax.add_geometries(gdfs[2].geometry, crs, facecolor='lightblue', edgecolor='blue', linewidth=0.25)

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
    labels = ['Buildings within 500m of river/stream', 'Buildings outside 500m of river/stream', 'Rivers or streams']

    ax.legend(handles, labels, title=None, title_fontsize=14, fontsize=18, loc='best', frameon=True, framealpha=1)

    fig.canvas.draw() # added since cartopy's rendering function is executed lazily and would otherwise not be included in the cProfile

    if savefig:
        if not os.path.exists(outputdir + viz_type):
            os.makedirs(outputdir + viz_type)

        plt.savefig(outputdir + viz_type + "cartopy (" + db_name + ").svg", format='svg', orientation='landscape')
    else:
        pass


if __name__ == "__main__":
    
    buildings_in, buildings_out, rivers = sql2gdf(db_name, password) 

    extent = getExtent(buildings_in, buildings_out, rivers)

    renderFigure(buildings_in, buildings_out, rivers)



