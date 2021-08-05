#!/usr/bin/env python3

"""Plot figure using Altair's Chart class.

Create cProfile of the plotting task by default as there is currently no basemap functionality for Altair.

Savefig via Altair Saver still buggy on Windows 10. 
Altair outputs in mapcompare/outputs/ are simply 'Save image as...' directly from the browser.

Charts can currently also not be displayed in VSCode-Python's interactive interpreter
(this may be fixed with the August release of VSCode, see vscode-jupyter issue #4382),
hence to-be-uncommented call to chart.show() to open chart in browser instead.
Re-comment out chart.show() when performance benchmarking,
as Altair Saver blocks the interpreter between runs until the browser tab is closed.
"""

import os
import altair as alt
import altair_viewer
import json
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
from mapcompare.cProfile_viz import to_cProfile

outputdir = 'mapcompare/outputs/'

# as yet no discernible support for basemaps
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


# allgedly works in vscode with this renderer, though no luck yet
# https://altair-viz.github.io/user_guide/display_frontends.html#displaying-in-vscode
# alt.renderers.enable('mimetype')

alt.renderers.enable('notebook')

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
def renderFigure(json_features, viz_type=viz_type, db_name=db_name, basemap=basemap):

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

    altair_viewer.display(chart)

    if savefig:
        if not os.path.exists(outputdir + viz_type):
            os.makedirs(outputdir + viz_type)
        chart.save(outputdir + viz_type + "altair (" + db_name + ").png", webdriver='chrome')
    else:
        pass

if __name__ == "__main__":

    buildings_in, buildings_out, rivers = sql2gdf(db_name, password)

    json_features = prepGDFs(buildings_in, buildings_out, rivers)

    renderFigure(json_features)
    


