#!/usr/bin/env python3

"""Plot figure using geoplot's polyplot() interface to matplotlib.

Create cProfile of the plotting task only if no basemap is added.
    
Creates a cProfile of the renderFigure() function encompassing the core plottinh task.
The cProfile is dumped as a .prof in mapcompare/profiles/[viz_type]/[db_name]/) only if basemap=False. 
This is to avoid tile loading affecting performance measurement of the core plotting task.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geoplot as gplt
import geoplot.crs as gcrs
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
from mapcompare.cProfile_viz import to_cProfile

outputdir = 'mapcompare/outputs/'
viz_type = 'static/' # type non-adjustable

# INPUTS
db_name = 'dd' 
basemap = True
savefig = True


def toLatLon(*gdfs):
    """Convert GDFs to geographic coordinates as expected by geoplot
    """
    li = []
    for gdf in gdfs:
        gdf = gdf.to_crs(epsg=4326)
        li.append(gdf)

    return li


@to_cProfile
def renderFigure(buildings_in, buildings_out, rivers, basemap=basemap, savefig=savefig, db_name=db_name, viz_type=viz_type):
    
    def getBBox(*gdfs):
        """Return combined bbox of all GDFs in format x0, y0, x1, y1.
        """

        list_of_bounds = []
        for gdf in gdfs:
            gdf_bounds = gdf.total_bounds
            list_of_bounds.append(gdf_bounds)
            
        xmin = np.min([item[0] for item in list_of_bounds])
        xmax = np.max([item[2] for item in list_of_bounds])
        ymin = np.min([item[1] for item in list_of_bounds])
        ymax = np.max([item[3] for item in list_of_bounds])
        
        # geoplot order different from cartopy order
        extent = [xmin, ymin, xmax, ymax]
        
        return extent

     # Get number of features per GDF, to display in legend
    buildings_in_no = str(len(buildings_in.index))
    buildings_out_no = str(len(buildings_out.index))
    rivers_no = str(len(rivers.index))

    extent = getBBox(buildings_in, buildings_out, rivers)

    if basemap:
        ax = gplt.webmap(buildings_in, extent=extent, projection=gcrs.WebMercator(), figsize=(20, 10))
        gplt.polyplot(buildings_in, ax=ax, facecolor='red', zorder=3)
        gplt.polyplot(buildings_out, ax=ax, facecolor='lightgrey', edgecolor='black', linewidth=0.1, zorder=2)
        gplt.polyplot(rivers, ax=ax, facecolor='lightblue', edgecolor='blue', linewidth=0.25, zorder=1)
    else:
        ax = gplt.polyplot(buildings_in, extent=extent, projection=gcrs.Mercator(), facecolor='red', figsize=(20, 10))
        gplt.polyplot(buildings_out, ax=ax, facecolor='lightgrey', edgecolor='black', linewidth=0.1)
        gplt.polyplot(rivers, ax=ax, facecolor='lightblue', edgecolor='blue', linewidth=0.25)

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

        plt.savefig(outputdir + viz_type + "geoplot (" + db_name + ").svg", format="svg", orientation="landscape")
    else:
        pass

if __name__ == "__main__":

    buildings_in, buildings_out, rivers = sql2gdf(db_name, password) 

    buildings_in, buildings_out, rivers = toLatLon(buildings_in, buildings_out, rivers)
    
    renderFigure(buildings_in, buildings_out, rivers)
