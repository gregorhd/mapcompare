"""Plot figure using GeoPandas' GeoDataFrame.plot() interface to matplotlib.

Create a cProfile of the renderFigure() function, if decorator @to_cProfile is set.
"""

import os
import time
import functools
import cProfile
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geoplot as gplt
import geoplot.crs as gcrs
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password

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
        p.dump_stats("mapcompare/profiles/non-interactive/" + os.path.basename(__file__)[:-3] + ' ' + '(' + db_name + ')' + ".prof")
        
        print(f"\ncProfile created in mapcompare/profiles/non-interactive/ for {func.__name__!r} in module {os.path.basename(__file__)}")
        return value
    return wrapper

def toLatLon(*gdfs):
    """Convert GDFs to geographic coordinates as expected by geoplot
    """
    li = []
    for gdf in gdfs:
        gdf = gdf.to_crs(epsg=4326)
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
        
        # geoplot order different from cartopy order
        carto_extent = [xmin, ymin, xmax, ymax]
        
        return carto_extent

     # Get number of features per GDF, to display in legend
    buildings_in_no = str(len(buildings_in.index))
    buildings_out_no = str(len(buildings_out.index))
    rivers_no = str(len(rivers.index))

    carto_extent = getBBox(buildings_in, buildings_out, rivers)

    ax = gplt.polyplot(buildings_in, extent=carto_extent, projection=gcrs.Mercator(), facecolor='red', figsize=(20, 10))
    gplt.polyplot(buildings_out, ax=ax, projection=gcrs.Mercator(), facecolor='lightgrey', edgecolor='black', linewidth=0.1)
    gplt.polyplot(rivers, ax=ax, projection=gcrs.Mercator(), facecolor='lightblue', edgecolor='blue', linewidth=0.25)

    # Legend

    buildings_in_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='red')]
    buildings_out_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightgrey', edgecolor='black', linewidth=0.5)]
    rivers_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightblue',edgecolor='blue', linewidth=0.25)]

    handles = buildings_in_handle + buildings_out_handle + rivers_handle 
    labels = ['Buildings within 500m (n=' + buildings_in_no + ')', 'Buildings outside 500m (n=' + buildings_out_no + ')', 'Rivers or streams (n=' + rivers_no + ')']

    leg = ax.legend(handles, labels, title=None, title_fontsize=14, fontsize=18, loc='best', frameon=True, framealpha=1)

if __name__ == "__main__":

    db_name = 'dd_subset' # 'dd' is the complete dataset, 'dd_subset' is the subset for testing
    
    buildings_in, buildings_out, rivers = sql2gdf(db_name, password) # 1min 55 secs

    buildings_in, buildings_out, rivers = toLatLon(buildings_in, buildings_out, rivers)
    
    renderFigure(buildings_in, buildings_out, rivers)

    # plt.savefig('mapcompare/outputs/non-interactive/geoplot (' + db_name + ').svg', format='svg', orientation='landscape')
