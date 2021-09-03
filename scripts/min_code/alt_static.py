#!/usr/bin/env python3

"""Reduced code sample to plot figure using Altair's Chart class.
"""

import altair as alt
from IPython.display import display
import json
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password


# INPUTS
db_name = 'dd_subset'

alt.renderers.enable('notebook')

def prepGDFs(*gdfs):
    """Prepare GeoDataFrames for use by Altair's alt.Data() class.
    """

    gdf1, gdf2, gdf3 = [gdf.to_crs(epsg=4326) for gdf in gdfs]
    
    gdf1['category'] = 'Label1'
    gdf2['category'] = 'Label2'
    gdf3['category'] = 'Label3'

    merged = gdf1.append(gdf2).append(gdf3)

    merged_json = merged.to_json()

    json_features = json.loads(merged_json)

    return json_features

if __name__ == "__main__":

    gdf1, gdf2, gdf3 = sql2gdf(db_name, password)

    json_features = prepGDFs(gdf1, gdf2, gdf3)

    features = alt.Data(values=json_features['features'])

    domain = ['Label1', 'Label2', 'Label3']
    range_ = ['red', 'grey', 'cornflowerblue']

    # plot map, where variables ares nested within `properties`, 
    chart = alt.Chart(features).mark_geoshape().properties(
        projection={'type': 'mercator'},
        width=700,
        height=400
    ).encode(
        color=alt.Color("properties.category:N", scale=alt.Scale(domain=domain, range=range_), legend=alt.Legend(title='Legend', orient='top-right'))
    )

    display(chart)

    


