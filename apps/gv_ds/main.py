#!/usr/bin/env python

"""Plot figure using GeoViews, datashader and Bokeh Server in conjunction.

The only difference between this app and HoloViews+datashader+Bokeh Server
is the declaration of a Cartopy CRS object in line 65: polys = gv.Polygons(spatialpdGDF, crs=ccrs.GOOGLE_MERCATOR, vdims='category'), and a slight
difference in the location of the tiles module in line 72:  tiles = gv.tile_sources.OSM().opts(...)

To run the live app and have datashader re-calculate the rasterized polygons with every zoom and pan, 
cd to the containing folder via the command line
and enter 'bokeh serve --show main.py'.

"""
import sys; sys.path.insert(0, '../..')
import geoviews as gv
from spatialpandas import GeoDataFrame
import datashader as ds
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
from holoviews.operation.datashader import (
    datashade, inspect_polygons
)
from cartopy import crs as ccrs


gv.extension('bokeh')


# INPUTS
db_name = 'dd_subset'

def prepGDFs(*gdfs):
    """Prepare GeoDataFrames for use by Holoviews' Polygons class.
    """

    # transform to webmercator to align with basemap
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
    
    return spatialpdGDF


def renderFigure(spatialpdGDF, db_name=db_name):

    color_key = {'Buildings within 500m of river/stream': 'red', 'Buildings outside 500m of river/stream': 'grey', 'River/stream': 'lightblue'}

    legend    = gv.NdOverlay({k: gv.Points([0,0], label=str(k)).opts(
                                            color=v, apply_ranges=False) 
                            for k, v in color_key.items()}, 'category')

    polys = gv.Polygons(spatialpdGDF, crs=ccrs.GOOGLE_MERCATOR, vdims='category')

    shaded = datashade(polys, color_key=color_key, aggregator=ds.by('category', ds.any()))
    hover = inspect_polygons(shaded).opts(fill_color='purple', tools=['hover'])

    tiles = gv.tile_sources.OSM().opts(
    min_height=500, responsive=True, xaxis=None, yaxis=None)

    layout = tiles * shaded * hover * legend

    return layout


buildings_in, buildings_out, rivers = sql2gdf(db_name, password)

spatialpdGDF = prepGDFs(buildings_in, buildings_out, rivers)

layout = renderFigure(spatialpdGDF)

doc = gv.renderer('bokeh').server_doc(layout)
doc.title = 'GeoViews + Datashader + Bokeh App'

    








