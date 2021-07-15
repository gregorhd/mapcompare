#!/usr/bin/env python3

"""Plot figure using datashader's tf.shade() method. This, in effect rasterizses the vector data, creating a static image without axes, legend or projection.
"""
import numpy as np
from spatialpandas import GeoDataFrame
import datashader as ds
import datashader.transfer_functions as tf
import datashader.utils as utils
from mapcompare.cProfile_viz import to_cProfile
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password

viz_type = 'static/' # not adjustable
basemap = False # not adjustable

# INPUTS
db_name = 'dd'
savefig = False

def prepGDFs(buildings_in, buildings_out, rivers):
    """Prepare GeoDataFrames for use by datashader's transfer_functions.shade() method.

    This step is separated from actual rendering to not affect performance measurement. 
    """
    def getBBox(*gdfs):
        """Return combined bbox of all GDFs in format (x0, x1, y0, y1).
        """

        list_of_bounds = []
        for gdf in gdfs:
            gdf_bounds = gdf.total_bounds
            list_of_bounds.append(gdf_bounds)
            
        xmin = np.min([item[0] for item in list_of_bounds])
        xmax = np.max([item[2] for item in list_of_bounds])
        ymin = np.min([item[1] for item in list_of_bounds])
        ymax = np.max([item[3] for item in list_of_bounds])
        
        extent = [xmin, xmax, ymin, ymax]
        
        return extent

    extent = getBBox(buildings_in, buildings_out, rivers)

    buildings_in['category'] = 'Within_500m'
    buildings_out['category'] = 'Outside_500m'
    rivers['category'] = 'River/stream'
    

    # Merge GDFs and set category column 
    merged = buildings_in.append(buildings_out)
    merged = merged.append(rivers)
    merged['category'] = merged['category'].astype('category')
    
    spatialpdGDF = GeoDataFrame(merged)
    
    return spatialpdGDF, extent


@to_cProfile
def renderFigure(spatialpdGDF, extent, db_name=db_name, viz_type=viz_type, basemap=basemap, savefig=savefig):

    color_key = {'Within_500m': 'red', 'Outside_500m': 'grey', 'River/stream': 'lightblue'}

    canvas = ds.Canvas(plot_height=1000, plot_width=1000, x_range=(extent[0], extent[1]), y_range=(extent[2], extent[3]))
    agg = canvas.polygons(spatialpdGDF, 'geom', agg=ds.by('category', ds.any()))
    tf.shade(agg, color_key=color_key)

    if savefig:
        utils.export_image(tf.shade(agg, color_key=color_key), filename="mapcompare/outputs/" + viz_type + "datashader only" + " (" + db_name + ")")
    else:
        pass

if __name__ == "__main__":
    
    buildings_in, buildings_out, rivers = sql2gdf(db_name, password)

    spatialpdGDF, extent = prepGDFs(buildings_in, buildings_out, rivers)

    renderFigure(spatialpdGDF, extent)






