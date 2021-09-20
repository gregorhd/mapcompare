#!/usr/bin/env python3

"""Reduced code sample plotting figure using plotly.py's express.choropleth_mapbox() method, with the appropriate zoon level having to be input manually.
"""
import os
import json
import numpy as np
import plotly.express as px
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password

viz_type = 'interactive/'

# INPUTS
db_name = 'dd_subset' 

def prepGDFs(*gdfs):
    """Prepare GeoDataFrames for use by plotly.py's express.choropleth_mapbox() method, without determining an appropriate zoom level.
    """
    gdf1, gdf2, gdf3 = [gdf.to_crs(epsg=4326) for gdf in gdfs]
    
    # Plotly does not seem to allow for adding multiple GDFs to the same figure successively (?)
    # Therefore, create Legend column in each GDF prior to GDF merge
    # This will serve as the discrete value against which to apply the symbology
    gdf1['Legend'] = 'Label1'
    gdf2['Legend'] = 'Label2'
    gdf3['Legend'] = 'Label3'

    # Merge GDFs and rename column headers for hover-over tooltips
    merged = gdf1.append(gdf2).append(gdf3)
    merged.rename(columns={"use": "Building use"}, inplace=True)

    # reset index, which plotly uses to select features to draw
    # merged.index could be used for the locations= kwarg of px.choropleth() or px.choropleth_matpbox()
    # However, then '_index' would show in the hover-over tooltips
    # In order to set the index visibility to False in the hover_data= kwarg, a separate 'id' column is created to which locations= is then pointed
    merged.reset_index(inplace=True)    
    merged['id'] = merged.index

    tempdir = "../../mapcompare/temp/" + viz_type

    if not os.path.exists(tempdir):
        os.makedirs(tempdir)

    merged.to_file(tempdir + "plotly_py (" + db_name + ").json", driver='GeoJSON')

    # Determine opimtal view vars for Mapbox base map, which is currently not automated
    extent = merged.total_bounds
    centerx, centery = (np.average(extent[0:3:2]), np.average(extent[1:4:2]))
    
    return merged, centerx, centery, tempdir

    
if __name__ == "__main__":
    
    gdf1, gdf2, gdf3 = sql2gdf(db_name, password)

    merged, centerx, centery, tempdir = prepGDFs(gdf1, gdf2, gdf3)

    # Plot with tile map using px.choropleth_mapbox()
    # This seems to always require a .json temp file

    with open(tempdir + "plotly_py (" + db_name + ").json") as f:
        geojson = json.load(f)

    # manually input appropriate zoom level here
    fig = px.choropleth_mapbox(merged, geojson=geojson, locations=merged['id'], title=title, color=merged['Legend'], color_discrete_map={'Label1':'red', 'Label2':'lightgrey', 'Label3':'lightblue'}, hover_data={'id': False, 'Legend': False, 'Building use':True}, mapbox_style="open-street-map", center={'lat': centery, 'lon': centerx}, zoom=13, featureidkey='properties.id')
    
    fig.update_geos(projection_type="mercator")
    fig.update_layout(margin={"r":0,"t":20,"l":0,"b":0}, title_text='Click on a legend entry to hide/unhide features', title_font_size=12)

    fig.show()
