#!/usr/bin/env python3

"""Reduce code sample plotting figure using GeoViews' Polygons class and utilizing  the Bokehbackend.
"""
import geoviews as gv
from bokeh.plotting import show
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password

gv.extension('bokeh')

# INPUTS
db_name = 'dd_subset'

def prepGDFs(*gdfs):
    """Transforms gdfs to EPSG:4326 and renames the 'geom' column to 'geometry'. The latter is required pending a bug fix by GeoViews.
    """
    
    gdfs = [gdf.to_crs(epsg=4326).rename(columns={'geom': 'geometry'}) for gdf in gdfs]
    
    return gdfs

if __name__ == "__main__":

    gdf1, gdf2, gdf3 = sql2gdf(db_name, password)

    gdf1, gdf2, gdf3 = prepGDFs(gdf1, gdf2, gdf3)

    tiles = gv.tile_sources.OSM()

    # color_index=None makes GeoViews ignore the automatically identified 'use' values dimension according to which
    # a color scheme would otherwise be applied
    gdf1 = gv.Polygons(gdf1).opts(tools=['hover'], color_index=None, color='red', xaxis=None, yaxis=None)
    gdf2 = gv.Polygons(gdf2).opts(tools=['hover'], color_index=None, color='lightgrey')
    gdf3 = gv.Polygons(gdf3).opts(color='lightblue')

    features = gdf1 * gdf2 * gdf3 * tiles

    # Similar to matplotlib legend artists have to be declared separately
    
    popts = dict(show_legend=True, apply_ranges=False)
    bldg_in_leg = gv.Polygons(gdf1, label="Label1").opts(color_index=None, color='red', **popts)
    bldg_out_leg = gv.Polygons(gdf2, label="Label2").opts(color_index=None, color='lightgrey', **popts)
    rivers_leg = gv.Polygons(gdf3, label="Label3").opts(color_index=None, color='lightblue', **popts)

    legend = bldg_in_leg * bldg_out_leg * rivers_leg

    title = "Bokeh's hide/mute legend click policy yet to be exposed in GeoViews"

    layout = (features * legend).opts(width=700, height=500, title=title)

    # gv.Element() does not show in VS Code interpreter, hence this workaround with
    # gv.render and bokeh.plotting.show,
    # otherwise use (gv.Overlay(features * legend).opts())
    show(gv.render(layout))