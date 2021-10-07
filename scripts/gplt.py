#!/usr/bin/env python3

"""Plot figure using geoplot's polyplot() interface to matplotlib.

Create cProfile of the plotting task only if no basemap is added.
    
Create a cProfile of the renderFigure() function encompassing the core plotting task.
The cProfile is dumped as a .prof in mapcompare/profiles/[viz_type]/[db_name]/) only if basemap=False and savefig=False. 
This is to avoid tile loading or writing to disk affecting performance measurement of the core plotting task.
"""

import os
import sys
import importlib
from typing import Tuple, List
from geopandas.geodataframe import GeoDataFrame
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geoplot as gplt
import geoplot.crs as gcrs
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
importlib.reload(sys.modules['mapcompare.cProfile_viz']) # no kernel/IDE restart needed after editing cProfile_viz.py
from mapcompare.cProfile_viz import to_cProfile

outputdir = 'mapcompare/outputs/'
viz_type = 'static/' # type non-adjustable

# INPUTS
db_name = 'dd_subset' 
basemap = True
savefig = False


def prepGDFs(*gdfs: GeoDataFrame) -> Tuple[Tuple[GeoDataFrame], List[np.float64]]:
    """Convert GDFs to geographic coordinates as expected by geoplot and calculates the combined bounding box (extent) of all GDFs.

    This step is separated from actual rendering to not affect performance measurement.
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


@to_cProfile
def renderFigure(*gdfs, basemap: bool=basemap, savefig: bool=savefig, db_name: str=db_name, viz_type: str=viz_type):
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
    buildings_in_no = str(len(gdfs[0].index))
    buildings_out_no = str(len(gdfs[1].index))
    rivers_no = str(len(gdfs[2].index))

    if basemap:
        ax = gplt.webmap(gdfs[0], extent=extent, projection=gcrs.WebMercator(), figsize=(20, 10))
        gplt.polyplot(gdfs[0], ax=ax, facecolor='red', zorder=3)
        gplt.polyplot(gdfs[1], ax=ax, facecolor='lightgrey', edgecolor='black', linewidth=0.1, zorder=2)
        gplt.polyplot(gdfs[2], ax=ax, facecolor='lightblue', edgecolor='blue', linewidth=0.25, zorder=1)
    else:
        ax = gplt.polyplot(gdfs[0], extent=extent, projection=gcrs.Mercator(), facecolor='red', figsize=(20, 10))
        gplt.polyplot(gdfs[1], ax=ax, facecolor='lightgrey', edgecolor='black', linewidth=0.1)
        gplt.polyplot(gdfs[2], ax=ax, facecolor='lightblue', edgecolor='blue', linewidth=0.25)

    # Legend

    buildings_in_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='red')]
    buildings_out_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightgrey', edgecolor='black', linewidth=0.5)]
    rivers_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightblue',edgecolor='blue', linewidth=0.25)]

    handles = buildings_in_handle + buildings_out_handle + rivers_handle 
    labels = ['Buildings within 500m (n=' + buildings_in_no + ')', 'Buildings outside 500m (n=' + buildings_out_no + ')', 'Rivers or streams (n=' + rivers_no + ')']

    ax.legend(handles, labels, title=None, title_fontsize=14, fontsize=18, loc='best', frameon=True, framealpha=1)

    # draw() added to account for significant delay between cProfile completeion
    # and figure finally rendering in the interpreter,
    # without the draw() geoplot runtime is 30% below Cartopy's and 40% below GeoPandas' which seems odd...
    # Final inclusion of the draw() pending confirmation with developers
    plt.gcf()

    if savefig:
        if not os.path.exists(outputdir + viz_type):
            os.makedirs(outputdir + viz_type)

        plt.savefig(outputdir + viz_type + "geoplot (" + db_name + ").svg", format="svg", orientation="landscape")
    else:
        pass
    

if __name__ == "__main__":

    buildings_in, buildings_out, rivers = sql2gdf(db_name, password) 

    ((buildings_in, buildings_out, rivers), extent) = prepGDFs(buildings_in, buildings_out, rivers)
    
    renderFigure(buildings_in, buildings_out, rivers)
