#!/usr/bin/env python3

"""Plot figure using GeoViews' Polygons class and utilizing either the Bokeh or matplotlib backend.

Creates a cProfile of the renderFigure() function encompassing the core plottinh task.
The cProfile is dumped as a .prof in mapcompare/profiles/[viz_type]/[db_name]/) only if basemap=False. 
This is to avoid tile loading affecting performance measurement of the core plotting task.
"""

# TODO Optimise performance (the slowest library thus far).
# TODO Add legend and basemap for static viz_type

import os
import numpy as np
import geoviews as gv
from geoviews import opts
from bokeh.plotting import show
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password
from mapcompare.cProfile_viz import to_cProfile
# from cartopy import crs as ccrs

outputdir = 'mapcompare/outputs/'
gv.extension('bokeh', 'matplotlib')

# INPUTS
viz_type = 'static/'
db_name = 'dd'
basemap = False
savefig = True

def prepGDFs(*gdfs):
    """Transforms gdfs to EPSG:4326 and renames the 'geom' column to 'geometry'. The latter is required pending a bug fix by GeoViews.

    This step is separated from actual rendering to not affect performance measurement. 
    """
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
        
        extent = [xmin, xmax, ymin, ymax]
        
        return extent
    
    extent = getBBox(buildings_in, buildings_out, rivers)

    aspect_ratio = (extent[1] - extent [0]) / (extent[3] - extent[2])

    li = []

    for gdf in gdfs:
        gdf = gdf.to_crs(epsg=4326).rename(columns={'geom': 'geometry'}, errors="raise")
        li.append(gdf)
        
    return (li, aspect_ratio)


@to_cProfile
def renderFigure(buildings_in, buildings_out, rivers, basemap=basemap, savefig=savefig, db_name=db_name, viz_type=viz_type):
    
    if basemap and viz_type == 'interactive/':

        # color_index=None makes GeoViews ignore the automatically identified 'use' values dimension according to which
        # a color scheme would otherwise be applied
        buildings_in = gv.Polygons(buildings_in).opts(tools=['hover'], color_index=None, color='red', xaxis=None, yaxis=None)
        buildings_out = gv.Polygons(buildings_out).opts(tools=['hover'], color_index=None, color='lightgrey')
        rivers = gv.Polygons(rivers).opts(color='lightblue')
        
        tiles = gv.tile_sources.OSM()

        features = buildings_in * buildings_out * rivers * tiles

        # Similar to matplotlib legend artists have to be declared separately
        
        popts = dict(show_legend=True, apply_ranges=False)
        bldg_in_leg = gv.Polygons(buildings_in, label="Buildings within 500m of rivers/stream").opts(color_index=None, color='red', **popts)
        bldg_out_leg = gv.Polygons(buildings_out, label="Buildings outside 500m of rivers/stream").opts(color_index=None, color='lightgrey', **popts)
        rivers_leg = gv.Polygons(rivers, label="Rivers/streams").opts(color_index=None, color='lightblue', **popts)

        legend = bldg_in_leg * bldg_out_leg * rivers_leg

        title = "Bokeh's hide/mute legend click policy yet to be exposed in GeoViews"

        layout = (features * legend).opts(width=700, height=500, title=title)

        gv.operation.resample_geometry(layout)


        # gv.Element() does not show in VS Code interpreter, hence this workaround with
        # gv.render and bokeh.plotting.show,
        # otherwise use (gv.Overlay(features * legend).opts())
        p = gv.render(layout)
        
        show(p)
    
    elif basemap == False and viz_type == 'interactive/':

        buildings_in = gv.Polygons(buildings_in).opts(tools=['hover'], color_index=None, color='red', xaxis=None, yaxis=None)
        buildings_out = gv.Polygons(buildings_out).opts(tools=['hover'], color_index=None, color='lightgrey')
        rivers = gv.Polygons(rivers).opts(color='lightblue')
        
        features = buildings_in * buildings_out * rivers

        # Similar to matplotlib legend artists have to be declared separately
        
        popts = dict(show_legend=True, apply_ranges=False)
        bldg_in_leg = gv.Polygons(buildings_in, label="Buildings within 500m of rivers/stream").opts(color_index=None, color='red', **popts)
        bldg_out_leg = gv.Polygons(buildings_out, label="Buildings outside 500m of rivers/stream").opts(color_index=None, color='lightgrey', **popts)
        rivers_leg = gv.Polygons(rivers, label="Rivers/streams").opts(color_index=None, color='lightblue', **popts)

        legend = bldg_in_leg * bldg_out_leg * rivers_leg

        title = "Bokeh's hide/mute legend click policy yet to be exposed in GeoViews"

        layout = (features * legend).opts(width=700, height=500, title=title)

        gv.operation.resample_geometry(layout).opts(width=400, height=400)

        p = gv.render(layout)

        # without basemap, aspect ratio seems to be skewed slightly,
        # hence accessing the Bokeh Figure aspect_ratio attribute directly here
        p.aspect_ratio = aspect_ratio

        show(p)
        
    elif basemap == False and viz_type == 'static/':           
    
        layout = gv.Polygons(buildings_in, roup="buildings_in") * gv.Polygons(buildings_out, group="buildings_out") * gv.Polygons(rivers, group="rivers")

        layout.opts(
            opts.Polygons('buildings_in', cmap=['red'], edgecolor='black', linewidth=0.5, xaxis=None, yaxis=None, backend="matplotlib"),
            opts.Polygons('buildings_out', cmap=['lightgrey'], edgecolor='black', linewidth=0.5, backend="matplotlib"),
            opts.Polygons('rivers', backend="matplotlib"),
            opts.Overlay(aspect=aspect_ratio, backend='matplotlib')
        )
        
        gv.output(layout, size=500, fig='svg', backend='matplotlib')

        
    elif basemap and viz_type == 'static/':
        raise NotImplementedError("Addition of basemap not yet implemented for GeoViews' matplotlib interface.")
    
    
    if savefig and viz_type == 'interactive/':
        if not os.path.exists(outputdir + viz_type):
            os.makedirs(outputdir + viz_type)

        gv.save(layout, outputdir + viz_type + "geoviews" + " (" + db_name + ").html")
    
    elif savefig and viz_type == 'static/':
        if not os.path.exists(outputdir + viz_type):
            os.makedirs(outputdir + viz_type)
        
        gv.save(layout, outputdir + viz_type + "geoviews" + " (" + db_name + ").svg", backend='matplotlib')
    

if __name__ == "__main__":

    buildings_in, buildings_out, rivers = sql2gdf(db_name, password)

    ((buildings_in, buildings_out, rivers), aspect_ratio) = prepGDFs(buildings_in, buildings_out, rivers)

    renderFigure(buildings_in, buildings_out, rivers)

    