import os
import time
import functools
import cProfile
import json
from bokeh.models.ranges import Range1d
import numpy as np
import geopandas as gpd
from bokeh.io import output_file, show
from bokeh.models import GeoJSONDataSource, Range1d
from bokeh.plotting import figure
from bokeh.sampledata.sample_geojson import geojson
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password

# Add if adding basemap: from bokeh.tile_providers import STAMEN_TERRAIN, get_provider

def timer(func):
    """Print runtime of decorated function. Quick option as alternative to cProfile."""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter() 
        run_time = end_time - start_time
        print(f"\nFinished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer

def to_cProfile(func):
    """Create cProfile of wrapped function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        p = cProfile.Profile()
        p.enable()

        value = func(*args, **kwargs)

        p.disable()
        p.dump_stats("mapcompare/profiles/interactive/" + os.path.basename(__file__)[:-3] + ' ' + '(' + db_name + ')' + ".prof")
        
        print(f"\ncProfile created in mapcompare/profiles/interactive/ for {func.__name__!r} in module {os.path.basename(__file__)}")
        return value
    return wrapper

def gdf2webmercator(*gdfs):
    """Convert GDFs to Web Mercator (required only if adding basemap)
    """

    li = []
    for gdf in gdfs:
        gdf = gdf.to_crs(epsg=3857)
        li.append(gdf)
    
    return li

def renderFigure(buildings_in, buildings_out, rivers):

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
    
    extent = getBBox(buildings_in, buildings_out, rivers)

    aspect_ratio = (extent[1] - extent [0]) / (extent[3] - extent[2])
    
    p = figure(
        aspect_ratio=aspect_ratio,
        background_fill_color="white",
        tooltips=[('Building use', '@gebaeudefunktion')],
        x_range=Range1d(extent[0], extent[1]),
        y_range=Range1d(extent[2], extent[3]),
    )
    p.xaxis.visible = False
    p.yaxis.visible = False

    # Optional Add basemap
    # p.add_tile(get_provider(STAMEN_TERRAIN))

    # Add features
    p.patches('xs', 'ys', color='red', source=GeoJSONDataSource(geojson=buildings_in.to_json()))
    p.patches('xs', 'ys', color='lightgrey', line_color='black', line_width=0.5, source=GeoJSONDataSource(geojson=buildings_out.to_json()))
    p.patches('xs', 'ys', color='lightblue', line_color='blue', line_width=0.25, source=GeoJSONDataSource(geojson=rivers.to_json()))

    show(p)

if __name__ == "__main__":

    db_name = 'dd_subset'

    buildings_in, buildings_out, rivers = sql2gdf(db_name, password)

    buildings_in, buildings_out, rivers = gdf2webmercator(buildings_in, buildings_out, rivers)
    
    # output_file(filename="mapcompare/outputs/interactive/bokeh" + " (" + db_name + ").html")

    renderFigure(buildings_in, buildings_out, rivers)

