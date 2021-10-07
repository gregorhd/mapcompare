"""Fetch three GDFs from PostGIS database containing the city of Dresden's real estate cadastre, returning:
    - all buildings within 500m of a river/stream, and their building use (simplified schema in English)
    - all buildings outside 500m of a river/stream, and their building use (simplified schema in English)
    - all rivers, streams and canals
"""
import numpy as np
import geopandas as gpd
from sqlalchemy import create_engine
import time
import functools
from mapcompare.misc.pw import password

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

@timer
def sql2gdf(db_name, password):
    """Return GeoDataFrames from PostGIS database.
    """

    db_connection_url = "postgresql://postgres:" + password + "@localhost:5432/" + db_name

    con = create_engine(db_connection_url)

    # Find buildings within 500 meters of rivers
    # FYI: 500m buffer:  101,697 rows, 5.6sec, 300m buffer: 65,870 rows, 8.9 secs
    sql1 = """WITH buffer as (
        SELECT ST_Union(ST_Buffer(f.wkb_geometry, 500)) as geom 
        FROM public.ax_fliessgewaesser as f) 
        
        SELECT g.use, g.wkb_geometry as geom 
        FROM public.ax_gebaeude as g 
        JOIN buffer ON ST_Within(g.wkb_geometry, buffer.geom) 
        OR ST_Intersects(g.wkb_geometry, buffer.geom);"""

    buildings_in = gpd.GeoDataFrame.from_postgis(sql1, con, crs='epsg:25833')

    # Find all other buildings
    # FYI: 500m buffer: 41,878 rows, 1min29secs, 300m buffer: 77,705 rows, 4min29secs
    sql2 = """WITH buffer as (
        SELECT ST_Union(ST_Buffer(f.wkb_geometry, 500)) as geom 
        FROM public.ax_fliessgewaesser as f) 
        
        SELECT g.use, g.wkb_geometry as geom 
        FROM public.ax_gebaeude as g 
        JOIN buffer ON ST_Disjoint(buffer.geom, g.wkb_geometry) 
        WHERE g.gml_id NOT IN (
            WITH buffer as (
                SELECT ST_Union(ST_Buffer(f.wkb_geometry, 500)) as geom 
                FROM public.ax_fliessgewaesser as f) 
                
                SELECT g.gml_id 
                FROM public.ax_gebaeude as g 
                JOIN buffer ON ST_Within(g.wkb_geometry, buffer.geom) OR ST_Intersects(g.wkb_geometry, buffer.geom));"""

    buildings_out = gpd.GeoDataFrame.from_postgis(sql2, con, crs='epsg:25833')

    # Query 3: Find all rivers
    sql3 = """SELECT wkb_geometry as geom 
    FROM public.ax_fliessgewaesser;"""

    rivers = gpd.GeoDataFrame.from_postgis(sql3, con, crs='epsg:25833')

    return buildings_in, buildings_out, rivers
