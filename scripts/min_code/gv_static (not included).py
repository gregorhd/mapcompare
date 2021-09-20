#!/usr/bin/env python3

"""Reduced code sample to plot figure using GeoViews' Polygons class and utilizing the matplotlib backend.
"""

import numpy as np
import geoviews as gv
from geoviews import opts
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
from cartopy import crs as ccrs

gv.extension('matplotlib')

# INPUTS

db_name = 'dd_subset'


def prepGDFs(*gdfs):
    """Transforms gdfs to EPSG:4326 and renames the 'geom' column to 'geometry'. The latter is required pending a bug fix by GeoViews.

    # Also calculates an appropriate zoom level if a tiled basemap is added while using the Matplotlib backend.
    """
    def getBBox(*gdfs):
        """Return combined bbox of all GDFs in cartopy set_extent format (x0, x1, y0, y1).
        """

        list_of_bounds = [gdf.total_bounds for gdf in gdfs]
            
        xmin = np.min([item[0] for item in list_of_bounds])
        xmax = np.max([item[2] for item in list_of_bounds])
        ymin = np.min([item[1] for item in list_of_bounds])
        ymax = np.max([item[3] for item in list_of_bounds])
        
        extent = [xmin, xmax, ymin, ymax]
        
        return extent
    
    def get_zoom_mercator(minlon, maxlon, minlat, maxlat, width_to_height):
        """Return optimal zoom level for opts.WMTS(zoom=zoom) for when using the maptlotlib backend.

        This workaround is from https://github.com/richieVil/rv_packages/blob/master/rv_geojson.py#L84
        
        used also in script plotly_py.py to address plotly.js issue #3434.
    
        """
        # longitudinal range by zoom level (20 to 1)
        # in degrees, if centered at equator
        lon_zoom_range = np.array([
            0.0007, 0.0014, 0.003, 0.006, 0.012, 0.024, 0.048, 0.096,
            0.192, 0.3712, 0.768, 1.536, 3.072, 6.144, 11.8784, 23.7568,
            47.5136, 98.304, 190.0544, 360.0
        ])
        margin = 1.2
        height = (maxlat - minlat) * margin * width_to_height
        width = (maxlon - minlon) * margin
        lon_zoom = np.interp(width , lon_zoom_range, range(20, 0, -1))
        lat_zoom = np.interp(height, lon_zoom_range, range(20, 0, -1))

        return round(min(lon_zoom, lat_zoom))

    gdfs = [gdf.to_crs(epsg=4326).rename(columns={'geom': 'geometry'}) for gdf in gdfs]

    extent = getBBox(*gdfs)

    aspect_ratio = (extent[1] - extent [0]) / (extent[3] - extent[2])

    zoom = get_zoom_mercator(extent[0], extent[1], extent[2], extent[3], aspect_ratio) 
        
    return (gdfs, zoom)

if __name__ == "__main__":

    gdf1, gdf2, gdf3 = sql2gdf(db_name, password)

    ((gdf1, gdf2, gdf3), zoom) = prepGDFs(gdf1, gdf2, gdf3)

    tiles = gv.tile_sources.OSM()

    layout = tiles * gv.Polygons(gdf1, group="gdf1") * gv.Polygons(gdf2, group="gdf2") * gv.Polygons(gdf3, group="gdf3").opts(projection=ccrs.Mercator())

    layout.opts(
        opts.Polygons('gdf1', cmap=['red'], edgecolor='black', linewidth=0.5),
        opts.Polygons('gdf2', cmap=['lightgrey'], edgecolor='black', linewidth=0.5),
        opts.Polygons('gdf3'),
        opts.WMTS(zoom=zoom)    
    )
    
    gv.output(layout, size=500, fig='svg')


