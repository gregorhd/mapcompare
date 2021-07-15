#!/usr/bin/env python

"""Plot figure using HoloViews, datashader and Bokeh in conjunction. Following this example: https://examples.pyviz.org/nyc_buildings/nyc_buildings.html

To have datashader re-calculate the rasterized polygons with every zoom and pan, 
run this script as part of a live Bokeh server by entering in the command line 'bokeh serve --show hv_ds.py'.
"""
import numpy as np
import holoviews as hv
from spatialpandas import GeoDataFrame
import datashader as ds
from bokeh.plotting import show
from mapcompare.cProfile_viz import to_cProfile
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
from holoviews.operation.datashader import (
    datashade, inspect_polygons
)
from collections import OrderedDict as ODict

hv.extension('bokeh')

viz_type = 'interactive/' # not adjustable

# INPUTS
db_name = 'dd_subset'
basemap = True 
savefig = False

def prepGDFs(*gdfs):
    """Prepare GeoDataFrames for use by datashader's transfer_functions.shade() method.

    This step is separated from actual rendering to not affect performance measurement. 
    """
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
        
        extent = [xmin, xmax, ymin, ymax]
        
        return extent
    
    extent = getBBox(*gdfs)

    aspect_ratio = (extent[1] - extent [0]) / (extent[3] - extent[2])
    
    # transform to webmercator to align with basemap, if added
    li = []
    for gdf in gdfs:
        gdf = gdf.to_crs(epsg=3857)
        li.append(gdf)

    buildings_in, buildings_out, rivers = li

    buildings_in['category'] = 'Buildings within 500m of river/stream'
    buildings_out['category'] = 'Buildings outside 500m of river/stream'
    rivers['category'] = 'River/stream'


    # Merge GDFs and set category column 
    merged = buildings_in.append(buildings_out)
    merged = merged.append(rivers)
    merged['category'] = merged['category'].astype('category')
    
    spatialpdGDF = GeoDataFrame(merged)
    
    return spatialpdGDF, aspect_ratio

@to_cProfile
def renderFigure(spatialpdGDF, db_name=db_name, viz_type=viz_type, basemap=basemap, savefig=savefig):

    color_key = {'Buildings within 500m of river/stream': 'red', 'Buildings outside 500m of river/stream': 'grey', 'River/stream': 'lightblue'}

    legend    = hv.NdOverlay({k: hv.Points([0,0], label=str(k)).opts(
                                            color=v, apply_ranges=False) 
                            for k, v in color_key.items()}, 'category')

    polys = hv.Polygons(spatialpdGDF, vdims='category')

    shaded = datashade(polys, color_key=color_key, aggregator=ds.by('category', ds.any()))
    hover = inspect_polygons(shaded).opts(fill_color='purple', tools=['hover'])

    if basemap:

        tiles = hv.element.tiles.OSM().opts(
        min_height=500, responsive=True, xaxis=None, yaxis=None)

        layout = tiles * shaded * hover * legend

        p = hv.render(layout)

    else:
        
        layout = shaded * hover * legend

        layout.opts(width=700)

        p = hv.render(layout)
        
        # without basemap, aspect ratio seems to be skewed slightly,
        # hence accessing the Bokeh Figure aspect_ratio attribute directly here
        p.aspect_ratio = aspect_ratio
    
    show(p)

    if savefig:
        hv.save(layout, "mapcompare/outputs/" + viz_type + "holoviews+datashader+bokeh" + " (" + db_name + ").html")
    else:
        pass
    
    doc = hv.renderer('bokeh').server_doc(layout)
    doc.title = 'HoloViews + Datashader + Bokeh App'

if __name__ == "__main__":

    buildings_in, buildings_out, rivers = sql2gdf(db_name, password)

    spatialpdGDF, aspect_ratio = prepGDFs(buildings_in, buildings_out, rivers)

    renderFigure(spatialpdGDF)

    








