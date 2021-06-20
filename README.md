
  
  
  

# pyviz-mapcompare

Comparison of Python libraries for creating non-interactive and interactive visualisations of large geospatial vector datasets (n=140,000+).

  

An MSc thesis at Ulster University.

  

## Which visualisation libraries are included in the comparison?

The Python visualisation landscape is highly complex and interconnected. The figure below expands on [VanderPlas (2017)]( https://www.youtube.com/watch?v=FytuB8nFHPQ), highlighting long-listed packages or libraries with geospatial functionalities (find an interactive mind map [here]( https://www.mindomo.com/mindmap/d932a80b26bc4cc59d0729ccb6a01a2b)). The landscape broadly clusters around a non-interactive track, primarily interfacing with *matplotlib*, and an interactive track relying on *Javascript* or *OpenGL*.

![The Python visualisation landscape](python_viz_landscape.png)
For the purpose of this study, the provisional long list of libraries and packages includes:
| **Non-interactive** | **Interactive** |
|--|--|
| (1) *GeoPandas*, (2) *cartopy*, (3) *geoplot*, (4) *datashader/holoviews*, (5) *geoviews*, (6) *Altair*. | (1) *Bokeh*, (2) *plotly/dash*, (3) *datashader/holoviews*, (4) *geoviews*, (5) *Altair*, (6) *folium*, (7) *mplleaflet*, (8) *geoplotlib*.  |

## How are libraries being compared?

  

A visualisation task common in urban development will be performed across both the non-interactive and interactive track. A 144,727 polygon dataset, located in two tables of a PostGIS database containing the city of Dresden's real-estate cadastre, is queried, returning three sets of results tables which are converted to GeoDataFrames to serve as inputs to the visualisation libraries. 

The figure below is a sample visualisation of the dataset using GeoPandas' **GeoDataFrame.plot()** method.

![Sample GeoPandas visualisation](sample_geopandas.png)

 The figures below demonstrate interactive visualisations using using *plotly.py*’s **express.choropleth_mapbox()** (left) and *bokeh*’s  **plotting.figure.patches()** methods (right)
|  ![Sample plotly.py visualisation](sample_plotly.png)  | ![Sample bokeh visualisation](sample_bokeh.png) |
|--|--|


Short-listed libraries are then compared as follows:

  

1. Comparing a range of library metadatea including:

	* Ease of installation (install via the _pip_ package installer, the _conda_ main channel or the _conda-forge_ community channel, or via _setup.py_);

	* Input formats (e.g. GeoDataFrames, from disk via .shp or .geojson);

	* Output formats;

	* Continuity of the developer community (_measures_: number of GitHub releases since first release, number of total commits; date of last commit; number of dependent packages and number of dependent repositories (‘repos’)_,_ as a measure of the library’s centrality and popularity in the Python visualisation ecosystem (both geospatial and otherwise);

2. Reproducing a pre-defined map template as closely as possible using the 
capabilities of all short-listed libraries;

3. Comparing the complexity of the syntax to reproduce the map template;

4. Comparing the time taken for only the rendering portion of a script to complete, i.e. excluding the data acquisition and, if required by any library, the data formatting portion, using *cProfile* and *_snakeviz_* to visualise results as ‘icicle’ graphs such as the below, which compares two different *matplotlib* interfaces: *GeoPandas'*  **GeoDataFrame.plot()** method (left) and *cartopy*'s **GeoAxes.add_geometries()** method (right).

| ![Snakeviz icicle graph for GeoDataFrame.plot()](snakeviz_gpd.png)  | ![Snakeviz icicle graph for GeoAxes.add_geometries()](snakeviz_cartopy.png)  |
|--|--|


  

![CPU time comparison for renderfigure()](cProfile_time_comp.png)

7. Comparing the visual quality and functionality of the map products (conformity with the map template, responsiveness, interactive enhancements);

8. Any limitations and technical challenges encountered.
