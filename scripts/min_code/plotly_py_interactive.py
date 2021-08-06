#!/usr/bin/env python3

"""Reduced code sample plotting figure using plotly.py's express.choropleth_mapbox() method.
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
    """Prepare GeoDataFrames for use by plotly.py's express.choropleth() or express.choropleth_mapbox() methods.
    """

    def get_zoom_mercator(minlon, maxlon, minlat, maxlat, width_to_height):
        """Return optimal zoom level for mapbox maps in Mercator projection.

        If using mapbox tiles as a basemap, the correct zoom and centre are currently not computed automatically by plotly (see: https://github.com/plotly/plotly.js/issues/3434)
        
        This workaround is from https://github.com/richieVil/rv_packages/blob/master/rv_geojson.py#L84
        though here with margin = 2, instead of 1.2.
    
        """
        # longitudinal range by zoom level (20 to 1)
        # in degrees, if centered at equator
        lon_zoom_range = np.array([
            0.0007, 0.0014, 0.003, 0.006, 0.012, 0.024, 0.048, 0.096,
            0.192, 0.3712, 0.768, 1.536, 3.072, 6.144, 11.8784, 23.7568,
            47.5136, 98.304, 190.0544, 360.0
        ])
        margin = 2
        height = (maxlat - minlat) * margin * width_to_height
        width = (maxlon - minlon) * margin
        lon_zoom = np.interp(width , lon_zoom_range, range(20, 0, -1))
        lat_zoom = np.interp(height, lon_zoom_range, range(20, 0, -1))

        return round(min(lon_zoom, lat_zoom))

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
    aspect_ratio = (extent[2] - extent [0]) / (extent[3] - extent[1])
    zoom = get_zoom_mercator(extent[0], extent[2], extent[1], extent[3], aspect_ratio)

    return merged, zoom, centerx, centery, tempdir

    
if __name__ == "__main__":
    
    gdf1, gdf2, gdf3 = sql2gdf(db_name, password)

    merged, zoom, centerx, centery, tempdir = prepGDFs(gdf1, gdf2, gdf3)

    title = 'Click on a legend entry to hide/unhide features'

    # Plot with tile map using px.choropleth_mapbox()
    # This seems to always require a .json temp file

    with open(tempdir + "plotly_py (" + db_name + ").json") as f:
        geojson = json.load(f)

    fig = px.choropleth_mapbox(merged, geojson=geojson, locations=merged['id'], title=title, color=merged['Legend'], color_discrete_map={
    'Label1':'red',
    'Label2':'lightgrey',
    'Label3':'lightblue'}, hover_data={'id': False, 'Legend': False, 'Building use':True}, mapbox_style="open-street-map", center={'lat': centery, 'lon': centerx}, zoom=zoom, featureidkey='properties.id')
    
    fig.update_geos(projection_type="mercator")
    fig.update_layout(margin={"r":0,"t":20,"l":0,"b":0}, title_text=title, title_font_size=12)

    fig.show()
