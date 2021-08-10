#!/usr/bin/env python

"""Reduced code sample plotting figure using HoloViews, datashader and Bokeh in conjunction. Following this example: https://examples.pyviz.org/nyc_buildings/nyc_buildings.html

Running this script as is, will produce a static rasterisation of the polygons, which will not be updated when zooming in.

To have datashader re-calculate the rasterized polygons with every zoom and pan, 
cd to apps/hv_ds/ via the command line and enter 'bokeh serve --show main.py'.
"""

import holoviews as hv
from spatialpandas import GeoDataFrame
import datashader as ds
from bokeh.plotting import show
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
from holoviews.operation.datashader import (
    datashade, inspect_polygons
)

hv.extension('bokeh')

# INPUTS
db_name = 'dd_subset'

def prepGDFs(*gdfs):
    """Prepare GeoDataFrames for use by HoloViews' Polygons class.
    """

    # transform to webmercator to align with basemap, if added

    gdf1, gdf2, gdf3 = [gdf.to_crs(epsg=3857) for gdf in gdfs]

    gdf1['category'] = 'Label1'
    gdf2['category'] = 'Label2'
    gdf3['category'] = 'Label3'


    # Merge GDFs and set category column 
    merged = gdf1.append(gdf2).append(gdf3)
    merged['category'] = merged['category'].astype('category')
    
    spatialpdGDF = GeoDataFrame(merged)
    
    return spatialpdGDF


if __name__ == "__main__":

    gdf1, gdf2, gdf3 = sql2gdf(db_name, password)

    spatialpdGDF = prepGDFs(gdf1, gdf2, gdf3)

    color_key = {'Label1': 'red', 'Label2': 'grey', 'Label3': 'lightblue'}

    legend    = hv.NdOverlay({k: hv.Points([0,0], label=str(k)).opts(
                                            color=v, apply_ranges=False) 
                            for k, v in color_key.items()}, 'category')

    polys = hv.Polygons(spatialpdGDF, vdims='category')

    shaded = datashade(polys, color_key=color_key, aggregator=ds.by('category', ds.any()))
    hover = inspect_polygons(shaded).opts(fill_color='purple', tools=['hover'])

    tiles = hv.element.tiles.OSM().opts(
    min_height=500, responsive=True, xaxis=None, yaxis=None)

    layout = tiles * shaded * hover * legend

    p = hv.render(layout)

    show(p)

    








