
> A comparison of Python libraries for static and interactive visualisations of large vector data. 
> An MSc thesis at Ulster University (on-going).

- [Which libraries are being compared?](#which-libraries-are-being-compared)
- [How are libraries being compared?](#how-are-libraries-being-compared)
- [Results](#results)
  - [Code complexity](#code-complexity)
  - [CPU runtime](#cpu-runtime)
    - [Subset dataset (feature count: 2,645)](#subset-dataset-feature-count-2645)
    - [Complete dataset (feature count: 144,727)](#complete-dataset-feature-count-144727)
- [Output samples](#output-samples)
  - [Static visualisations](#static-visualisations)
  - [Interactive visualisations](#interactive-visualisations)

  

## Which libraries are being compared?

  

The figure below expands on [VanderPlas (2017)]( https://www.youtube.com/watch?v=FytuB8nFHPQ), highlighting long-listed packages or libraries with geospatial functionalities (find an interactive mind map of this figure to view or to copy and edit [here]( https://www.mindomo.com/mindmap/d932a80b26bc4cc59d0729ccb6a01a2b)).

 

![The Python visualisation landscape](python_viz_landscape.png)

  

The table below summarises the long-list and indicates short-listed libraries in **bold**.

  
| **Static** | **Interactive** |
|--|--|
| (1) ***GeoPandas***, (2) ***cartopy***, (3) ***geoplot***, (4) ***datashader*** (for illustration only), (5) *GeoViews* + *mpl* (apparently no legend support yet), (6) ***Altair*** (no basemap support yet). | (1) ***Bokeh***, (2) ***Plotly.py***, (3) ***GeoViews+Bokeh***, (4) ***GeoViews+datashader+Bokeh***, (5) ***hvPlot+Bokeh***, (6) *Altair* (no *Vega-Lite* support for interactivity with geoshapes yet), (7) *folium*, (8) *mplleaflet*, (9) *geoplotlib*. |



## How are libraries being compared?

  

A simple visualisation task is performed across both the static and interactive track, and secondly for both a complete dataset and a smaller subset. The complete dataset contains 144,727 polygons representing the city of Dresden's real-estate cadastre. The subset contains 2,645 polygons from the same dataset. Both databases are queried in PostGIS via *GeoPandas*' `from_postgis()` function, returning three *GeoPandas* GeoDataFrames to directly or indirectly serve as primary data inputs.

  

Long-listed libraries are first compared by compiling a range of metadata:

  * General implementation strategy (e.g. a high-level interface to a third-party ‘core’ plotting library or a core library itself);

  * Installation channels and requirements;

  

  * Input formats/required conversions;

  * Output formats (static images, interactive maps. or both);;

  * Proxies measuring the vibrancy of the developer and user community  (_measures_: number of GitHub releases since first release, number of total commits; number of contributors; date of last commit; number of dependent packages and number of dependent repositories).

The short-list then tried to include both large-community, comparatively well-funded projects (such as *Bokeh* and *Plotly*) as well as libraries relying on a more limited number of contributors (such as *geoplot*). It was also attempted to cover a variety of backends and both imperative as well as declarative approaches. 

The short-listed libraries were then compared along these indicators:

1.	the range of documentation based on a juxtaposition of documentation ‘elements’ and a sample of applicable code examples consulted to implement the common visualisation task;

2.	the complexity of the syntax as measured by the total number of lines of code of a ‘reduced code’ version required to reproduce the map template, excluding comments and blank lines;

3.	the ability to reproduce the map template including map elements such as a categorical legend and basemap;

4.	resource requirements (output file size and, for interactive visualisations, a subjective assessment of ‘responsiveness’ on pan and zoom);

5.	the time taken for the rendering portion of a script to complete, indicated as an average across a total of 10 runs: The rendering portion excludes data acquisition and, if required by any library, data pre-processing, reprojection or conversion. CPU times were measured using the cProfile module. The following measures were taken to ensure comparability of results:
    *	The Python kernel was restarted before each new benchmarking session;
    *	To prevent some libraries, such as *Cartopy*, from re-using an already drawn canvas, each run was executed manually rather than as part of a `for` loop (with the exception of the ‘out of competition’ runs of *datashader*);
    *	During performance measurement, no basemap tiles were added (`basemap=False` and figures were not written to disk (`savefig=False`). Instead, what was being measured was the time taken for figures to be rendered inside the VSCode interactive interpreter window;
    *	To account for some libraries’ lazy execution of underlying rendering functions, force rendering within the interactive interpreter window during the course of the function call, or prevent libraries from displaying the figure in a browser window by default, the adjustments outlined in the table below were added to respective scripts depending on libraries’ default behaviour, or their particular behaviour if central calls to, say, a `plot` or `chart` object are made within a Jupyter Notebook or the VSCode Python Extension as part of a function call:
  
| **Static** | **Adjustment** |  **Interactive**  | **Adjustment**  |
|:-|:-|:-|:-|
|*GeoPandas + Matplotlib*|`fig.canvas.draw()` (pro-forma only,<br>no effect on behaviour or performance)|*Bokeh*|`bokeh.io.output.output_notebook()`<br>…<br>`bokeh.io.show(plot)`|
|*Cartopy + Matplotlib*|`fig.canvas.draw()`|GeoViews + Bokeh*|`bokeh.plotting.show(gv.render(plot))`
|
|*geoplot + Matplotlib* |`matplotlib.pyplot.gcf()`|*GeoViews+ datashader + Bokeh Server*|*None*|
|*Altair + Vega-Lite*|`altair.renderers.enable('mimetype')`<br>...<br> `IPython.display.display(chart)`|*hvPlot + HoloViews + Bokeh*|`IPython.display.display(plot)`|
|*datashader*|*None*|*Plotly*|*None*|



6.	Any other limitations or challenges encountered.



## Results

The more qualitative results regarding documentation are not reproduced here.

### Code complexity

Excluding blank lines and comments, and assessing the 'reduced code' versions in `scripts/min_code/` which reproduce the map template including a categorical legend and a tiled basemap, where possible.

|  **Static**  | **Interactive**  |
|--|--|
| ![code comparison - static](comp_code_static.png) |  ![code comparison - interactive](comp_code_interactive.png)  |

### CPU runtime

#### Subset dataset (feature count: 2,645)
  
|  **Static**  | **Interactive**  |
|--|--|
| ![cProfile comparison - static](comp_profile_static_dd_subset.png) |  ![cProfile comparison - interactive](comp_profile_interactive_dd_subset.png)  |


####  Complete dataset (feature count: 144,727)

 
| **Static** | **Interactive** |
|--|--|
| ![cProfile comparison - static](comp_profile_static_dd.png)  |  ![cProfile comparison - interactive](comp_profile_interactive_dd.png) |
  

## Output samples

 

### Static visualisations



![Overview of outputs - static](sample_outputs_static.png)

![Comparison of outputs - static](meta_outputs_static.png)

### Interactive visualisations
  

![Overview of outputs - interactive](sample_outputs_interactive.png)

![Comparison of outputs - interactive](meta_outputs_interactive.png)