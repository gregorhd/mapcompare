from setuptools import setup

setup(name='mapcompare',
      version='0.1.0',
      description='Comparison of Python packages and libraries for visualising geospatial vector data: applications for Smarter Cities.',
      url='https://github.com/gregorhd/mapcompare',
      author='Gregor Herda',
      author_email='gregorherda@gmail.com',
      license='GPL',
      packages=['mapcompare'],
      install_requires=[
                        'numpy', 'matplotlib', 'pandas', 'altair', 'geopandas', 'cartopy',
                        'geoplot', 'geoviews', 'holoviews', 'datashader', 'hvplot', 'bokeh', 'plotly', 'wrapt'],
      scripts=['scripts/alt.py', 'scripts/bkh.py', 'scripts/carto.py',
               'scripts/ds.py', 'scripts/gpd.py',
               'scripts/gplt.py', 'scripts/gv.py',
               'scripts/gv_ds.py', 'scripts/plotly_py.py',
               'scripts/hv_plot.py', 'scripts/profile_comp.py',
               'scripts/profile_comp.py',
               'scripts/min_code/code_comp.py'],
      zip_safe=False)