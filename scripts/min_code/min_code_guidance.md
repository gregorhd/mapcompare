To reduce the subjectiveness of the lines of code (LOC) indicator of the study, and present all libraries or combinations of libraries ('implementations') in their best light, the developers themselves are invited to provide a simple 'best practice' code sample reproducing the map template using the sample data provided in the `data/data.gpkg` GeoPackage, representing a small subset of the city of Dresden's cadastral map.

The requirements are as follows:

A simple categorical choropleth map is to be produced using the recommended elements of the library's standard API. 

The data is to be visualised through an imperative, rather than a declarative approach, following a pre-defined symbology, as is common in urban development applications. The suggested color map for the three provided layers is: {'buildings_in': 'red', 'buildings_out': 'lightblue', 'rivers': 'lightgrey'}

Map elements should include a **categorical legend** in the top right of the map and, where possible, a light **tile layer basemap**, preferably OSM. The optimal **zoom level** should be defined automatically rather than having to be hardcoded manually depending on the data.

## Legibility



