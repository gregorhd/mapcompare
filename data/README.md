### Data source

The dataset used in the analysis consisted of two tables from a 14GB vector dataset containing the German city of Dresden’s complete [real-estate cadastre](https://www.geodaten.sachsen.de/downloadbereich-alkis-4176.html) covering an area of 637 square kilometres. The dataset is available for download as 111 individual files in the Extensible Mark-up Language (XML) format. The dataset’s schema follows Germany’s [Authoritative Real Estate Cadastre Information System ‘ALKIS’](http://www.adv-online.de/Products/Real-Estate-Cadastre/ALKIS/), which itself is based on the [ISO 19100 series of standards](https://www.iso.org/committee/54904.html).

### Data preparation and query

Two separate locally hosted PostGIS v3.0.0-enabled PostgreSQL v12.4 databases were populated, one containing the complete dataset and another containing a smaller subset. Table creation and the XML-to-PostgreSQL data transfer was performed using the (German only) *norGIS ALKIS Import tool* available via the advanced installation options of the [*OSGeo4W*](https://trac.osgeo.org/osgeo4w) binary distribution for Windows.

As the spatial query itself was secondary to the research objective, it was kept simple and was performed via *GeoPandas*’ `from_postgis()` function. Of the numerous columns available in each base table, only the feature ID and geometry columns were queried for both. However, to avail of interactive libraries’ ability to indicate one or more additional data attributes through hover tools, a **table update** was performed in-database on the building tables’ building use column (‘gebaeudefunktion’) translating the scheme’s four digit attribute values representing fine-grained building uses into broader, English language building use categories. The respective **SQL file** is [provided](building_use_to_english.sql) in this directory.

The updated building use column was then included in the query’s SELECT statement.