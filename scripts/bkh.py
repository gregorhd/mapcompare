#!/usr/bin/env python3

"""Plot figure using Bokeh's figure.patches method.

Create cProfile of the plotting task only if no basemap is added.
    
This is to avoid tile loading affecting performance measurement of the core rendering functionality.
"""

import os
import numpy as np
from bokeh.models.ranges import Range1d
from bokeh.io import output_file, show
from bokeh.models import GeoJSONDataSource, Range1d
from bokeh.plotting import figure
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
from mapcompare.cProfile_viz import to_cProfile
from bokeh.tile_providers import OSM, get_provider

outputdir = 'mapcompare/outputs/'
viz_type = 'interactive/' # type non-adjustable

# INPUTS
db_name = 'dd_subset'
basemap = True
savefig = False


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

@to_cProfile
def renderFigure(buildings_in, buildings_out, rivers, basemap=basemap, savefig=savefig, db_name=db_name, viz_type=viz_type):
    """Renders polygons using Bokeh's plotting.figure.patches() function.
    """
    
    if basemap:
        
        p = figure(title="Click on a legend entry to hide/unhide features",
            aspect_ratio=aspect_ratio,
            plot_height=600, 
            background_fill_color="white",
            tooltips=[('Building use', '@use')],
            x_range=Range1d(extent[0], extent[1]),
            y_range=Range1d(extent[2], extent[3]),
        )
        
        p.add_tile(get_provider(OSM))
    
    else:
        
        p = figure(title="Click on a legend entry to hide/unhide features",
            aspect_ratio=aspect_ratio,
            plot_height=600, 
            background_fill_color="white",
            tooltips=[('Building use', '@use')],
            x_range=Range1d(extent[0], extent[1]),
            y_range=Range1d(extent[2], extent[3]),
        )
    
    p.xaxis.visible = False
    p.yaxis.visible = False
        
    # Add features
    p.patches('xs', 'ys', legend_label="Buildings within 500m of river/stream", color='red', source=GeoJSONDataSource(geojson=buildings_in.to_json()))
    p.patches('xs', 'ys', legend_label="Buildings outside 500m of river/stream", color='lightgrey', line_color='black', line_width=0.5, source=GeoJSONDataSource(geojson=buildings_out.to_json()))
    p.patches('xs', 'ys', legend_label="River/stream", color='lightblue', line_color='blue', line_width=0.25, source=GeoJSONDataSource(geojson=rivers.to_json()))

        
    p.legend.location = "top_right"
    p.legend.label_text_font_size = "8pt"
    p.legend.click_policy="hide"

    if savefig:
        if not os.path.exists(outputdir + viz_type):
            os.makedirs(outputdir + viz_type)

        output_file(filename=outputdir + viz_type + "bokeh" + " (" + db_name + ").html")
    else:
        pass

    show(p)

if __name__ == "__main__":

    buildings_in, buildings_out, rivers = sql2gdf(db_name, password)

    ((buildings_in, buildings_out, rivers), extent, aspect_ratio) = prepGDFs(buildings_in, buildings_out, rivers)

    renderFigure(buildings_in, buildings_out, rivers)

