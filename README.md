


# pyviz-mapcompare
Comparison of Python libraries for creating non-interactive and interactive visualisations of large geospatial vector datasets (n=140,000+).

An MSc thesis at Ulster University.

## Which visualisation libraries are included in the comparison?

| **Non-interactive** | **Interactive** | 
|--|--|
| Different *matplotlib* interfaces via (1) *GeoPandas*, (2) *cartopy*, and (3) *geoplot*. | (1) *Bokeh*, (2) *plotly/dash*, (3) *datashader/holoviews*, (4) *geoplotlib*, (5) *folium*, (6) *Altair* |

## How are libraries being compared?

A visualisation task common in urban development will be performed across both the non-interactive and interactive track. A 144,727 polygon dataset, located in two tables of a PostGIS database containing the city of Dresden's real-estate cadastre, is queried, returning three sets of results tables which are converted to GeoDataFrames to serve as inputs to the visualisation libraries. The figure below is a sample visualisation of the dataset using GeoPandas' **GeoDataFrame.plot()** method.

![Sample visualisation](sample_viz.png)

Short-listed libraries are then compared as follows:

 1. Definition of a common feature symbology, producing a ‘map template’;
    
 2. Separating the query and data loading portion of the script from the
    data processing (if required) and rendering portions through
    respective function definitions;
 3. Reproducing the map template as closely as possible using the
            capabilities of all short-listed libraries;
 4. Comparing the complexity of the syntax to reproduce the map
        template;
 5. Comparing the time taken for the rendering portion of a script to
        complete, i.e. excluding the data acquisition and, if required by
        any library, the data formatting portion, using *cProfile* and *_snakeviz_* to visualise results as ‘icicle’ graphs such as the below, comparing two different *matplotlib* interfaces: *GeoPandas'* **GeoDataFrame.plot()** method and *cartopy*'s **GeoAxes.add_geometries()** method.
        
![Snakeviz icicle graph for GeoDataFrame.plot()](snakeviz_gpd.png)
![Snakeviz icicle graph for GeoAxes.add_geometries()](snakeviz_cartopy.png)

  6. Comparing the visual quality and functionality of the map products
    (resolution, conformity with the map template, responsiveness, interactive enhancements);
    
 7. Any limitations and technical challenges encountered.
    
    
    

        

