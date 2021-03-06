#!/usr/bin/env python3

"""Plot figure using plotly.py's express.choropleth() (without basemap) or express.choropleth_mapbox() methods (with basemap).

Create a cProfile of the renderFigure() function encompassing the core plotting task.
The cProfile is dumped as a .prof in mapcompare/profiles/[viz_type]/[db_name]/) only if basemap=False and savefig=False. 
This is to avoid tile loading or writing to disk affecting performance measurement of the core plotting task.
"""

import os
import json
from typing import Tuple
from geopandas import GeoDataFrame
import numpy as np
import plotly.express as px
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
from mapcompare.cProfile_viz import to_cProfile

outputdir = 'mapcompare/outputs/'
viz_type = 'interactive/' # type non-adjustable

# INPUTS
db_name = 'dd_subset'
basemap = True
savefig = False


def prepGDFs(*gdfs: GeoDataFrame) -> Tuple[GeoDataFrame, int, np.float64, np.float64, str]:
    """Prepare GeoDataFrames for use by plotly.py's express.choropleth() or express.choropleth_mapbox() functions.

    This step is separated from actual rendering to not affect performance measurement. 
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

    buildings_in, buildings_out, rivers = [gdf.to_crs(epsg=4326) for gdf in gdfs]
    
    # Plotly does not seem to allow for adding multiple GDFs to the same figure successively (?)
    # Therefore, create Legend column in each GDF prior to GDF merge
    # This will serve as the discrete value against which to apply the symbology
    buildings_in['Legend'] = 'Building within 500m of river/stream'
    buildings_out['Legend'] = 'Building outside 500m of river/stream'
    rivers['Legend'] = 'River/stream'

    # Merge GDFs and rename column headers for hover-over tooltips
    merged = buildings_in.append(buildings_out).append(rivers)
    merged.rename(columns={"use": "Building use"}, inplace=True)

    # reset index, which plotly uses to select features to draw
    # merged.index could be used for the locations= kwarg of px.choropleth() or px.choropleth_matpbox()
    # However, then '_index' would show in the hover-over tooltips
    # In order to set the index visibility to False in the hover_data= kwarg, a separate 'id' column is created to which locations= is then pointed
    merged.reset_index(inplace=True)    
    merged['id'] = merged.index

    tempdir = "mapcompare/temp/" + viz_type

    if not os.path.exists(tempdir):
        os.makedirs(tempdir)

    merged.to_file(tempdir + "plotly_py (" + db_name + ").json", driver='GeoJSON')

    # Determine opimtal view vars for Mapbox base map, which is currently not automated
    extent = merged.total_bounds
    centerx, centery = (np.average(extent[0:3:2]), np.average(extent[1:4:2]))
    aspect_ratio = (extent[2] - extent [0]) / (extent[3] - extent[1])
    zoom = get_zoom_mercator(extent[0], extent[2], extent[1], extent[3], aspect_ratio)

    return merged, zoom, centerx, centery, tempdir


@to_cProfile
def renderFigure(merged: GeoDataFrame, zoom: int, centerx: np.float64, centery: np.float64, basemap: bool=basemap, savefig: bool=savefig, db_name: str=db_name, viz_type: str=viz_type) -> None:
    """Renders the figure reproducing the map template.

    Parameters
    ----------
    merged : GeoDataFrame
        GeoDataFrame containing all three feature sets.
    zoom : int
        Optimal zoom level, needed when adding a basemap.
    centerx, centery : float
        Coordinates setting the viewport's centre, needed when adding a basemap.
    basemap : Boolean
        Global scope variable determining whether or not to add an OSM basemap.
    savefig : Boolean
        Global scope variable determining whether or not to save the current figure to HTML in /mapcompare/outputs/[viz_type]/.
    db_name : {'dd', 'dd_subset'}
        Global scope variable indicating the source PostGIS database to be used, 'dd' being the complete dataset and 'dd_subset' the subset.
    viz_type : {'static/', 'interactive/'}
        Global scope variable indicating the visualisation type.
    
    Returns
    ----------
        A figure reproducing the map template.
    """
    
    title = 'Click on a legend entry to hide/unhide features'

    if basemap:

        # Plot with tile map using px.choropleth_mapbox()
        # This seems to always require a .json temp file

        with open(tempdir + "plotly_py (" + db_name + ").json") as f:
            geojson = json.load(f)

        fig = px.choropleth_mapbox(merged, geojson=geojson, locations=merged['id'], title=title, color=merged['Legend'], color_discrete_map={
        'Building within 500m of river/stream':'red',
        'Building outside 500m of river/stream':'lightgrey',
        'River/stream':'lightblue'}, hover_data={'id': False, 'Legend': False, 'Building use':True}, mapbox_style="open-street-map", center={'lat': centery, 'lon': centerx}, zoom=zoom, featureidkey='properties.id')
        
        fig.update_geos(projection_type="mercator")
        fig.update_layout(margin={"r":0,"t":20,"l":0,"b":0}, title_text=title, title_font_size=12)
    
    else:
        # Plot without tile map using px.choropleth() which does not require
        # a .json as a temp file, instead it reads straight from GDF

        fig = px.choropleth(merged, geojson=merged.geometry, locations=merged['id'], color=merged['Legend'], color_discrete_map={
            'Building within 500m of river/stream':'red',
            'Building outside 500m of river/stream':'lightgrey',
            'River/stream':'lightblue'}, hover_data={'id': False, 'Legend': False, 'Building use':True})

        fig.update_geos(fitbounds="locations", projection_type="mercator")
        fig.update_layout(margin={"r":0,"t":20,"l":0,"b":0}, title_text=title, title_font_size=12)
    
    fig.show()
    
    if savefig:
        if not os.path.exists(outputdir + viz_type):
            os.makedirs(outputdir + viz_type)

        fig.write_html(outputdir + viz_type + "plotly_py (" + db_name + ").html")
    
    else:
        pass
    
    
if __name__ == "__main__":
    
    buildings_in, buildings_out, rivers = sql2gdf(db_name, password)

    merged, zoom, centerx, centery, tempdir = prepGDFs(buildings_in, buildings_out, rivers)

    renderFigure(merged, zoom, centerx, centery)