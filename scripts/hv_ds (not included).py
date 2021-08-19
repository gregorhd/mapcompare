#!/usr/bin/env python

"""Plot figure using HoloViews, datashader and Bokeh in conjunction. Following this example:
https://examples.pyviz.org/nyc_buildings/nyc_buildings.html

Creates a cProfile of the renderFigure() function encompassing the core plotting task.
The cProfile is dumped as a .prof in mapcompare/profiles/[viz_type]/[db_name]/) only if basemap=False. 
This is to avoid tile loading affecting performance measurement of the core plotting task.

Running this script as is, will produce a static rasterisation of the polygons not updated when zooming in.

To have datashader re-calculate the rasterized polygons dynamically with every zoom and pan, 
cd to apps/hv_ds/ via the command line and enter 'bokeh serve --show main.py'.
"""

import os
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


hv.extension('bokeh')

outputdir = 'mapcompare/outputs/'
viz_type = 'interactive/' # not adjustable

# INPUTS
db_name = 'dd'
basemap = False 
savefig = False


def prepGDFs(*gdfs):
    """Prepare GeoDataFrames for use by HoloViews' Polygons class.

    This step is separated from actual rendering to not affect performance measurement. 
    """

    # transform to webmercator to align with basemap, if added

    buildings_in, buildings_out, rivers = [gdf.to_crs(epsg=3857) for gdf in gdfs]

    buildings_in['category'] = 'Buildings within 500m of river/stream'
    buildings_out['category'] = 'Buildings outside 500m of river/stream'
    rivers['category'] = 'River/stream'


    # Merge GDFs and set category column 
    merged = buildings_in.append(buildings_out).append(rivers)
    merged['category'] = merged['category'].astype('category')
    
    # see else (i.e. not basemap) section below on need for aspect_ratio
    extent = merged.total_bounds
    aspect_ratio = (extent[2] - extent [0]) / (extent[3] - extent[1])

    spatialpdGDF = GeoDataFrame(merged)
    
    return spatialpdGDF, aspect_ratio


@to_cProfile
def renderFigure(spatialpdGDF, basemap=basemap, savefig=savefig, db_name=db_name, viz_type=viz_type):
    """Renders the figure reproducing the map template.

    Parameters
    ----------
    spatialpdGDF : SpatialPandas GeoDataFrame
        GeoDataFrame containing all three feature sets.
    basemap : Boolean
        Global scope variable determining whether or not to add an OSM basemap.
    savefig : Boolean
        Global scope variable determining whether or not to save the current figure to HTML in /mapcompare/outputs/[viz_type]/.
    db_name : {'dd', 'dd_subset'}
        Global scope variable indicating the source PostGIS database to be used, 'dd' being the complete dataset and 'dd_subset' the subset.
    viz_type : {'static/', 'interactive/'}
        Global scope variable indicating the visualisation type.
    
    Returns
    ----------
        A figure reproducing the map template.
    """

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
        if not os.path.exists(outputdir + viz_type):
            os.makedirs(outputdir + viz_type)
        
        hv.save(layout, outputdir + viz_type + "holoviews+datashader+bokeh" + " (" + db_name + ").html")
    else:
        pass
    

if __name__ == "__main__":

    buildings_in, buildings_out, rivers = sql2gdf(db_name, password)

    spatialpdGDF, aspect_ratio = prepGDFs(buildings_in, buildings_out, rivers)

    renderFigure(spatialpdGDF)

    








