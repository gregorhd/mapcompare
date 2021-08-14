#!/usr/bin/env python3

"""Plot figure using hvPlot.

Creates a cProfile of the renderFigure() function encompassing the core plottinh task.
The cProfile is dumped as a .prof in mapcompare/profiles/[viz_type]/[db_name]/) only if basemap=False. 
This is to avoid tile loading affecting performance measurement of the core plotting task.
"""

import os
import hvplot.pandas
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
from mapcompare.cProfile_viz import to_cProfile

outputdir = "mapcompare/outputs/"
viz_type = 'interactive/'

# INPUTS
db_name = 'dd_subset'
basemap = False
savefig = False

def prepGDFs(*gdfs):
    """Transforms gdfs to EPSG:4326 and renames the 'geom' column to 'geometry'. The latter is required pending a fix by GeoViews/HoloViews (see GeoViews issue #506).

    These steps are separated from actual rendering to not affect performance measurement.
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

@to_cProfile
def renderFigure(merged, basemap=basemap, savefig=savefig, db_name=db_name, viz_type=viz_type):
    
    if basemap:

        plot = (
        merged.hvplot(geo=True, cmap=['red', 'lightgrey', 'lightblue'], tiles='OSM', hover_cols=['Legend', 'Building use'], xaxis=None, yaxis=None, legend='top_right', height=500)
        )
        
        hvplot.show(plot)

    elif not basemap:

        plot = (
        merged.hvplot(geo=True, cmap=['red', 'lightgrey', 'lightblue'], hover_cols=['Legend', 'Building use'], xaxis=None, yaxis=None, legend='top_right', height=500)
        )
        
        hvplot.show(plot)

    if savefig:
        if not os.path.exists(outputdir + viz_type):
            os.makedirs(outputdir + viz_type)

        hvplot.save(plot, outputdir + viz_type + "hvPlot (" + db_name + ").html")

if __name__ == "__main__":

    buildings_in, buildings_out, rivers = sql2gdf(db_name, password)

    merged = prepGDFs(buildings_in, buildings_out, rivers)

    renderFigure(merged)