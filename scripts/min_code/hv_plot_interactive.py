#!/usr/bin/env python3

"""Reduced code version plotting figure using hvPlot.
"""

import hvplot.pandas 
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password

# INPUTS
db_name = 'dd'

def prepGDFs(*gdfs):
    """Transforms gdfs to EPSG:4326 and renames the 'geom' column to 'geometry'. The latter is required pending a bug fix by GeoViews/HoloViews (see GeoViews issue #506).
    """
    buildings_in, buildings_out, rivers = [gdf.to_crs(epsg=4326).rename(columns={'geom': 'geometry', 'use' : 'Building use'}) for gdf in gdfs]
    
    # Create Legend column in each GDF prior to GDF merge
    # This will serve as the discrete value against which to apply the symbology
    buildings_in['Legend'] = 'Building within 500m of river/stream'
    buildings_out['Legend'] = 'Building outside 500m of river/stream'
    rivers['Legend'] = 'River/stream'

    # Merge GDFs and fill the river features' empty 'Building use' column, otherwise an error is thrown
    merged = buildings_in.append(buildings_out).append(rivers).fillna(value='Not applicable') 

    return merged


if __name__ == "__main__":

    buildings_in, buildings_out, rivers = sql2gdf(db_name, password)

    merged = prepGDFs(buildings_in, buildings_out, rivers)

    plot = (
        merged.hvplot(geo=True, cmap=['red', 'lightgrey', 'lightblue'], tiles='OSM', hover_cols=['Legend', 'Building use'], xaxis=None, yaxis=None, legend='top_right', height=500)
        )
        
    hvplot.show(plot)