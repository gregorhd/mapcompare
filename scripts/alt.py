#!/usr/bin/env python3

"""Plot figure using Altair's Chart class.

Create cProfile of the plotting task by default as there is currently no basemap functionality for Altair.

Savefig via Altair Saver still buggy on Windows 10. 
Altair outputs in mapcompare/outputs/ are simply 'Save image as...' directly from the browser.

"""

import os
import sys
import importlib
import altair as alt
import json
from IPython.display import display
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
importlib.reload(sys.modules['mapcompare.cProfile_viz']) # no kernel/IDE restart needed after editing cProfile_viz.py
from mapcompare.cProfile_viz import to_cProfile

outputdir = 'mapcompare/outputs/'

# as yet no support for basemaps
basemap = False

# chart.save() seems to have a number of issues on Windows
# see https://github.com/altair-viz/altair_saver/issues/72 and 
# https://github.com/altair-viz/altair_saver/issues/95 - no luck yet with these solutions
savefig = False


# mark_geoshape currently does not support interactive mode
# see https://github.com/altair-viz/altair/issues/679
viz_type = 'static/' 


# INPUTS
db_name = 'dd'


# VSCode can natively display the charts in the interpreter
# https://altair-viz.github.io/user_guide/display_frontends.html#displaying-in-vscode

alt.renderers.enable('mimetype')


def prepGDFs(*gdfs):
    """Prepare GeoDataFrames for use by Altair's alt.Data() class.

    This step is separated from actual rendering to not affect performance measurement. 
    """

    buildings_in, buildings_out, rivers = [gdf.to_crs(epsg=4326) for gdf in gdfs]
    
    buildings_in['Legend'] = 'Building within 500m of river/stream'
    buildings_out['Legend'] = 'Building outside 500m of river/stream'
    rivers['Legend'] = 'River/stream'

    merged = buildings_in.append(buildings_out).append(rivers)

    merged_json = merged.to_json()

    json_features = json.loads(merged_json)

    return json_features


@to_cProfile
def renderFigure(json_features, basemap=basemap, db_name=db_name, viz_type=viz_type):
    """Renders the figure reproducing the map template.

    Parameters
    ----------
    json_features : dict
        Python object deserialised from JSON containing all three feature sets.
    basemap : Boolean
        Global scope variable determining whether or not to add a basemap.
        Simply used for triggering the cProfile on inspect.
    savefig : Boolean
        Global scope variable determining whether or not to save the current figure to SVG. At present, not working on Windows - see
        https://github.com/altair-viz/altair_saver/issues/97
    db_name : {'dd', 'dd_subset'}
        Global scope variable indicating the source PostGIS database to be used, 'dd' being the complete dataset and 'dd_subset' the subset.
    viz_type : {'static/', 'interactive/'}
        Global scope variable indicating the visualisation type.
    
    Returns
    ----------
        A figure reproducing the map template minus the basemap.
    """

    features = alt.Data(values=json_features['features'])

    domain = ['Building within 500m of river/stream', 'Building outside 500m of river/stream', 'River/stream']
    range_ = ['red', 'grey', 'cornflowerblue']

    # plot map, where variables ares nested within `properties`, 
    chart = alt.Chart(features).mark_geoshape().properties(
        projection={'type': 'mercator'},
        width=700,
        height=400
    ).encode(
        color=alt.Color("properties.Legend:N", scale=alt.Scale(domain=domain, range=range_), legend=alt.Legend(title='Legend', orient='top-right'))
    )

    # altair_viewer.display(chart)

    display(chart)
    
    if savefig:
        if not os.path.exists(outputdir + viz_type):
            os.makedirs(outputdir + viz_type)
        chart.save(outputdir + viz_type + "altair (" + db_name + ").svg", webdriver='firefox')
    else:
        pass


if __name__ == "__main__":

    buildings_in, buildings_out, rivers = sql2gdf(db_name, password)

    json_features = prepGDFs(buildings_in, buildings_out, rivers)

    renderFigure(json_features)
    


