#!/usr/bin/env python3

"""Reduced code sample to plot figure using Bokeh's figure.patches method.
"""

import numpy as np
from bokeh.models.ranges import Range1d
from bokeh.io import show
from bokeh.models import GeoJSONDataSource, Range1d
from bokeh.plotting import figure
from bokeh.io.output import output_notebook
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
from bokeh.tile_providers import OSM, get_provider

output_notebook()

# INPUTS
db_name = 'dd_subset'

def prepGDFs(*gdfs):
    """Convertes GDFs to Web Mercator to line up with tiled basemaps fetched by Bokeh. Returns combined bounding box (extent) and aspect_ratio.
    """
    gdfs = [gdf.to_crs(epsg=3857) for gdf in gdfs]

    list_of_bounds = [gdf.total_bounds for gdf in gdfs]
        
    xmin = np.min([item[0] for item in list_of_bounds])
    xmax = np.max([item[2] for item in list_of_bounds])
    ymin = np.min([item[1] for item in list_of_bounds])
    ymax = np.max([item[3] for item in list_of_bounds])
    
    extent = [xmin, xmax, ymin, ymax]

    aspect_ratio = (extent[1] - extent [0]) / (extent[3] - extent[2])

    return (gdfs, extent, aspect_ratio)  

if __name__ == "__main__":

    gdf1, gdf2, gdf3 = sql2gdf(db_name, password)

    ((gdf1, gdf2, gdf3), extent, aspect_ratio) = prepGDFs(gdf1, gdf2, gdf3)

    p = figure(title="Click on a legend entry to hide/unhide features",  aspect_ratio=aspect_ratio, plot_height=600, background_fill_color="white", tooltips=[('Building use', '@use')], x_range=Range1d(extent[0], extent[1]), y_range=Range1d(extent[2], extent[3]))
        
    p.add_tile(get_provider(OSM))

    p.xaxis.visible = False
    p.yaxis.visible = False
        
    # Add features
    p.patches('xs', 'ys', legend_label="Label1", color='red', source=GeoJSONDataSource(geojson=gdf1.to_json()))
    p.patches('xs', 'ys', legend_label="Label2", color='lightgrey', line_color='black', line_width=0.5, source=GeoJSONDataSource(geojson=gdf2.to_json()))
    p.patches('xs', 'ys', legend_label="Label3", color='lightblue', line_color='blue', line_width=0.25, source=GeoJSONDataSource(geojson=gdf3.to_json()))

        
    p.legend.location = "top_right"
    p.legend.label_text_font_size = "8pt"
    p.legend.click_policy="hide"

    show(p)


