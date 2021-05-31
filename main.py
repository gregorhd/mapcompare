import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from cartopy import crs as ccrs
from sqlalchemy import create_engine
import time
import functools
import demload
from datetime import datetime
from misc.pw import password

def timer(func):
    """Print runtime of decorated function courtesy of RealPython's Primer on Python Decorators: https://realpython.com/primer-on-python-decorators/"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter() 
        run_time = end_time - start_time
        print(f"\nFinished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer

# Connection with SQLAlchemy

@timer
def alchemyConnect(db_name, password):
    """
    """

    db_connection_url = "postgresql://postgres:" + password + "@localhost:5432/" + db_name

    con = create_engine(db_connection_url)

    # Find buildings within 500 meters of rivers
    # 96msec on msc_test, 5.6sec on msc
    # 101,697 rows
    sql1 = "WITH buffer as (SELECT ST_Union(ST_Buffer(f.wkb_geometry, 300)) as geom FROM public.ax_fliessgewaesser as f) SELECT g.gebaeudefunktion, g.wkb_geometry as geom FROM public.ax_gebaeude as g JOIN buffer ON ST_Within(g.wkb_geometry, buffer.geom) OR ST_Intersects(g.wkb_geometry, buffer.geom);"

    buildings_in = gpd.GeoDataFrame.from_postgis(sql1, con, crs='epsg:25833')

    # Find all other buildings - is there a more efficient way?
    # 220msec on msc_test, 1min29msc on msc
    # 41,878 rows
    sql2 = "WITH buffer as (SELECT ST_Union(ST_Buffer(f.wkb_geometry, 300)) as geom FROM public.ax_fliessgewaesser as f) SELECT g.gebaeudefunktion, g.wkb_geometry as geom FROM public.ax_gebaeude as g JOIN buffer ON ST_Disjoint(buffer.geom, g.wkb_geometry) WHERE g.gml_id NOT IN (WITH buffer as (SELECT ST_Union(ST_Buffer(f.wkb_geometry, 300)) as geom FROM public.ax_fliessgewaesser as f) SELECT g.gml_id FROM public.ax_gebaeude as g JOIN buffer ON ST_Within(g.wkb_geometry, buffer.geom) OR ST_Intersects(g.wkb_geometry, buffer.geom));" 

    buildings_out = gpd.GeoDataFrame.from_postgis(sql2, con, crs='epsg:25833')

    # Query 3: Find all rivers
    # 70-90msec on msc_test and msc
    # 1,152 rows
    sql3 = "SELECT wkb_geometry as geom FROM public.ax_fliessgewaesser;"

    rivers = gpd.GeoDataFrame.from_postgis(sql3, con, crs='epsg:25833')

    return buildings_in, buildings_out, rivers

@timer
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
    
    carto_extent = [xmin, xmax, ymin, ymax]
    
    return carto_extent

if __name__ == "__main__":
    db_name = 'msc_test'
    
    buildings_in, buildings_out, rivers = alchemyConnect(db_name, password) # timeit: 214 ms ± 52.5 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)

    crs = ccrs.epsg('25833')

    fig, ax = plt.subplots(1, 1, subplot_kw={'projection': crs}, figsize=(10, 10))

    carto_extent = getBBox(buildings_in, buildings_out, rivers)

    ax.set_extent(carto_extent, crs=crs)

    csvpath = r'c:\Users\grego\OneDrive\01_GIS\11_MSc\00_Project\01_data\02_DEM\DGM20\dgm25_akt.csv'

    data_dir = '01_data/02_DEM/DGM20/'

    handles, ax = demload.showDEMs(csvpath, data_dir, carto_extent, ax, crs)

    ax.add_geometries(buildings_in.geometry, crs=crs, facecolor='red')

    ax.add_geometries(buildings_out.geometry, crs=crs, facecolor='white', edgecolor='black', linewidth=0.2)

    ax.add_geometries(rivers.geometry, crs=crs, facecolor='lightblue', edgecolor=None)

    plt.savefig('02_outputs/01_matplotlib/' + datetime.today().strftime('%Y-%m-%d') + ' ' + db_name + '.svg', format='svg', orientation='landscape')





