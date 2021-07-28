from setuptools import setup

setup(name='mapcompare',
      version='0.1',
      description='Comparison of Python packages and libraries for visualising geospatial vector data: applications for Smarter Cities.',
      url='https://github.com/gregorhuh/mapcompare',
      author='Gregor Herda',
      author_email='gregorherda@gmail.com',
      license='GPL',
      packages=['mapcompare'],
      install_requires=[
                        'numpy', 'matplotlib', 'pandas', 'geopandas', 'cartopy',
                        'geoplot', 'geoviews', 'holoviews', 'datashader','bokeh', 'plotly', 'wrapt'],
      scripts=['scripts/alt.py', 'scripts/bkh.py', 'scripts/carto.py',
               'scripts/ds.py', 'scripts/gpd.py',
               'scripts/gplt.py', 'scripts/gv.py',
               'scripts/hv_ds.py', 'scripts/plotly_py.py',
               'scripts/profile_comp.py'],
      zip_safe=False)