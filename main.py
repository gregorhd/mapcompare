import numpy as np
import geopandas as gpd
import rasterio as rio
from cartopy import crs as ccrs
from cartopy.feature import ShapelyFeature
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import timeit
import time
import functools
from dem_load import findDGM20s, showDEMs
from datetime import datetime
from misc.pw import password


def timer(func):
    """Print runtime of decorated function courtesy of RealPython's Primer on Python Decorators: https://realpython.com/primer-on-python-decorators/"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter() #1
        value = func(*args, **kwargs)
        end_time = time.perf_counter() #2
        run_time = end_time - start_time #3
        print(f"\nFinished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer

# Connection with SQLAlchemy

def alchemyConnect(password):
    """
    """

    db_connection_url = "postgresql://postgres:" + password + "@localhost:5432/msc_test"

    con = create_engine(db_connection_url)  

    sql1 = "SELECT DISTINCT g.gml_id, g.gebaeudefunktion, g.wkb_geometry as geom FROM public.ax_gebaeude as g JOIN public.ax_fliessgewaesser as f ON ST_DWithin(g.wkb_geometry, f.wkb_geometry, 500)";

    buildings_in = gpd.GeoDataFrame.from_postgis(sql1, con, crs='epsg:25833')

    sql2 = "SELECT gml_id, gebaeudefunktion, wkb_geometry as geom FROM public.ax_gebaeude WHERE gml_id NOT IN (SELECT DISTINCT g.gml_id FROM public.ax_gebaeude as g JOIN public.ax_fliessgewaesser as f ON ST_DWithin(g.wkb_geometry, f.wkb_geometry, 500));"

    buildings_out = gpd.GeoDataFrame.from_postgis(sql2, con, crs='epsg:25833')

    sql3 = "SELECT gml_id, wkb_geometry as geom FROM public.ax_fliessgewaesser;"

    rivers = gpd.GeoDataFrame.from_postgis(sql3, con, crs='epsg:25833')

    return buildings_in, buildings_out, rivers

def getBBox(*gdfs):
    """Return a list object for cartopy set_extent (x0, x1, y0, y1).
    """

    list_of_bounds = []
    for gdf in gdfs:
        gdf_bounds = gdf.total_bounds
        list_of_bounds.append(gdf_bounds)
        
    xmin = np.min([item[0] for item in list_of_bounds])
    xmax = np.max([item[2] for item in list_of_bounds])
    ymin = np.min([item[1] for item in list_of_bounds])
    ymax = np.max([item[3] for item in list_of_bounds])
    
    carto_extent = [xmin, xmax, ymin, ymax]
    
    return carto_extent

if __name__ == "__main__":
    buildings_in, buildings_out, rivers = alchemyConnect(password) # timeit: 214 ms ± 52.5 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)

    crs = ccrs.epsg('25833')

    fig, ax = plt.subplots(1, 1, subplot_kw={'projection': crs}, figsize=(10, 10))

    carto_extent = getBBox(buildings_in, buildings_out, rivers)

    ax.set_extent(carto_extent, crs=crs)

    # to clean up...

    rast_list = findDGM20s(r'c:\Users\grego\OneDrive\01_GIS\11_MSc\00_Project\01_data\02_DEM\DGM20\dgm25_akt.csv', carto_extent)

    file_list = []

    for tile in rast_list:
        tile_num = tile[0]
        filename = '33' + tile_num + '_dgm20.xyz'
        file_list.append(filename)

    # cont...

    handles, ax = showDEMs(file_list, ax, crs)

    ax.add_geometries(buildings_in.geometry, crs=crs, facecolor='red', edgecolor='red')

    ax.add_geometries(buildings_out.geometry, crs=crs, facecolor='white', edgecolor='grey', alpha=0.5)

    ax.add_geometries(rivers.geometry, crs=crs, facecolor='lightblue', edgecolor='blue')

    # plt.savefig('02_outputs/01_matplotlib/' + datetime.today().strftime('%Y-%m-%d') + '.jpg', format='jpg', dpi=600.0, orientation='landscape')





