#!/usr/bin/env python3

"""Plot figure using GeoPandas' GeoDataFrame.plot() interface to matplotlib.

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
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
import requests
importlib.reload(sys.modules['mapcompare.cProfile_viz']) # no kernel/IDE restart needed after editing cProfile_viz.py
from mapcompare.cProfile_viz import to_cProfile

outputdir = 'mapcompare/outputs/'
viz_type = 'static/' # non-adjustable

# INPUTS
db_name = 'dd_subset' 
basemap = False
savefig = False


def getExtent(*gdfs):
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
def renderFigure(buildings_in, buildings_out, rivers, basemap=basemap, savefig=savefig, db_name=db_name, viz_type=viz_type):
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
    
    # Get number of features per GDF, to display in legend
    buildings_in_no = str(len(buildings_in.index))
    buildings_out_no = str(len(buildings_out.index))
    rivers_no = str(len(rivers.index))

    crs = ccrs.UTM(33)

    fig, ax = plt.subplots(1, 1, subplot_kw={'projection': crs}, figsize=(20, 10))

    ax.set_extent(extent, crs=crs)
    ax.set_title("Matplotlib interface: GeoPandas' .plot()" + "\n", fontsize=20)
    
    # Add features to Axes
    """GeoPandas' native approach offers less control but is less verbose:

    # Create a column containing the categories to map against and merge.
    buildings_in['cat'] = 'Building within 500m of river/stream'
    buildings_out['cat'] = 'Building outside 500m of river/stream'
    rivers['cat'] = 'River/stream'

    merged = buildings_in.append(buildings_out).append(rivers)
    
    # Then create a custom color map
    color_mapping = {'Building within 500m of river/stream': 'red', 'Building outside 500m of river/stream': 'grey', 'River/stream': 'lightblue'}

    merged.plot(ax=ax, color=merged["cat"].map(color_mapping))

    # This currently does not offer automatic legend creation via legend=True.
    # See: https://github.com/geopandas/geopandas/issues/1269.
    """
    
    buildings_in.plot(ax=ax, facecolor='red')
    buildings_out.plot(ax=ax, facecolor='lightgrey', edgecolor='black', linewidth=0.1)
    rivers.plot(ax=ax, facecolor='lightblue', edgecolor='blue', linewidth=0.25)
   
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

    ax.legend(handles, labels, title=None, title_fontsize=14, fontsize=18, loc='best', frameon=True, framealpha=1)

    # draw added simply pro-forma to align with other mpl interfaces
    # has no impact on results
    fig.canvas.draw()

    if savefig:
        if not os.path.exists(outputdir + viz_type):
            os.makedirs(outputdir + viz_type)

        plt.savefig(outputdir + viz_type + "geopandas (" + db_name + ').svg', format='svg', orientation='landscape')
    else:
        pass


if __name__ == "__main__":

    buildings_in, buildings_out, rivers = sql2gdf(db_name, password)

    extent = getExtent(buildings_in, buildings_out, rivers)
    
    renderFigure(buildings_in, buildings_out, rivers)



