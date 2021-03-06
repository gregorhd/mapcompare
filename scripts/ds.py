#!/usr/bin/env python3

"""Plot figure using datashader's tf.shade() method. This, in effect rasterizses the vector data, creating a static image without axes, legend or projection.

Create a cProfile of the renderFigure() function encompassing the core plotting task.
The cProfile is dumped as a .prof in mapcompare/profiles/[viz_type]/[db_name]/) only if savefig=False. 
This is to avoid writing to disk affecting performance measurement of the core plotting task.
"""
import os
import sys
import importlib
import numpy as np
from spatialpandas import GeoDataFrame
import geopandas as gpd # for type hinting only
from typing import Tuple, List
import datashader as ds
import datashader.transfer_functions as tf
import datashader.utils as utils
from mapcompare.sql2gdf import sql2gdf, timer
from mapcompare.misc.pw import password
importlib.reload(sys.modules['mapcompare.cProfile_viz']) # no kernel/IDE restart needed after editing cProfile_viz.py
from mapcompare.cProfile_viz import to_cProfile


outputdir = 'mapcompare/outputs/'
viz_type = 'static/' # not adjustable
basemap = False # not adjustable

# INPUTS
db_name = 'dd_subset'
savefig = True

@timer
def prepGDFs(*gdfs: gpd.GeoDataFrame) -> Tuple[GeoDataFrame, List[np.float64]]:
    """Prepare GeoDataFrames for use by datashader's transfer_functions.shade() method.

    This step is separated from actual rendering to not affect performance measurement. 
    """
    def getBBox(*gdfs: gpd.GeoDataFrame):
        """Return combined bbox of all GDFs in format (x0, x1, y0, y1).
        """

        list_of_bounds = [gdf.total_bounds for gdf in gdfs]
            
        xmin = np.min([item[0] for item in list_of_bounds])
        xmax = np.max([item[2] for item in list_of_bounds])
        ymin = np.min([item[1] for item in list_of_bounds])
        ymax = np.max([item[3] for item in list_of_bounds])
        
        extent = [xmin, xmax, ymin, ymax]
        
        return extent

    extent = getBBox(*gdfs)

    gdfs[0]['category'] = 'Within_500m'
    gdfs[1]['category'] = 'Outside_500m'
    gdfs[2]['category'] = 'River/stream'
    

    # Merge GDFs and set category column 
    merged = gdfs[0].append(gdfs[1]).append(gdfs[2])
    merged['category'] = merged['category'].astype('category')
    
    spatialpdGDF = GeoDataFrame(merged)
    
    return spatialpdGDF, extent


@to_cProfile
def renderFigure(spatialpdGDF: GeoDataFrame, extent: List[np.float64], basemap: bool=basemap, savefig: bool=savefig, db_name: str=db_name, viz_type: str=viz_type) -> None:
    """Renders the figure reproducing the map template minus the basemap and legend.

    Parameters
    ----------
    spatialpdGDF : SpatialPandas GeoDataFrame
        GeoDataFrame containing all three feature sets.
    basemap : Boolean
        Global scope variable determining whether or not to add a basemap.
        Simply used for triggering the cProfile on inspect.
    savefig : Boolean
        Global scope variable determining whether or not to save the current figure to PNG.
    db_name : {'dd', 'dd_subset'}
        Global scope variable indicating the source PostGIS database to be used, 'dd' being the complete dataset and 'dd_subset' the subset.
    viz_type : {'static/', 'interactive/'}
        Global scope variable indicating the visualisation type.
    
    Returns
    ----------
        A figure reproducing the map template minus the basemap and legend.
    """

    color_key = {'Within_500m': 'red', 'Outside_500m': 'grey', 'River/stream': 'lightblue'}

    canvas = ds.Canvas(plot_height=1000, plot_width=1000, x_range=(extent[0], extent[1]), y_range=(extent[2], extent[3]))
    agg = canvas.polygons(spatialpdGDF, 'geom', agg=ds.by('category', ds.any()))
    tf.shade(agg, color_key=color_key)

    if savefig:
        if not os.path.exists(outputdir + viz_type):
            os.makedirs(outputdir + viz_type)

        utils.export_image(tf.shade(agg, color_key=color_key), filename=outputdir + viz_type + "datashader only" + " (" + db_name + ")")
    else:
        pass


if __name__ == "__main__":
    
    buildings_in, buildings_out, rivers = sql2gdf(db_name, password)

    spatialpdGDF, extent = prepGDFs(buildings_in, buildings_out, rivers)

    renderFigure(spatialpdGDF, extent)






