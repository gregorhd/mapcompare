"""Compare number of lines of code for each reduced code version,
excluding comments and blank lines.
"""

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# INPUTS
viz_type = 'interactive'

if not '\\'.join(__file__.split('\\')[:-1]) == os.getcwd():
    os.chdir('scripts/min_code/')
    line_dict = {}
    for fn in glob.glob('*.py'):
        if fn.endswith(viz_type + '.py'):
            with open(fn) as f:
                line_dict[fn] = sum(1 for line in f if line.strip() and not line.startswith('#') and not line.startswith('"""'))
    os.chdir('../../')
else:
    print("os.chdir() to repo root directory and rerun script")

df = pd.DataFrame(line_dict.items(), columns=['library','code_num'])

df['library'] = [lib_name.split('_' + viz_type)[0] for lib_name in df['library']]

if viz_type == 'interactive':
    rename_dict = {'bkh': 'Bokeh', 'plotly_py': 'Plotly.py', 'gv': 'GeoViews+\nBokeh', 'gv_ds': 'GeoViews+\ndatashader+\nBokeh Server', 'hv_plot': 'hvPlot+\nHoloViews+\nBokeh'}

else:
    rename_dict = {'alt': 'Altair+\nVega-Lite', 'carto': 'Cartopy+\nMatplotlib', 'ds': 'Data-\nshader', 'gpd': 'GeoPandas+\nMatplotlib', 'gplt': 'geoplot+\nMatplotlib', 'gv': 'GeoViews+\nMatplotlib*'}
        
df['library'].replace(rename_dict, inplace=True)

if viz_type == 'interactive':
    
    x_label="Interactive visualisation via"

else:

    x_label = 'Static visualisation via'

df.rename(columns={'library': x_label}, inplace=True)

# Plot cumtimes to bar chart

ax = df.plot.bar(x=x_label, y="code_num", alpha=0.5, ylabel="# of lines of code", rot='horizontal', title="Code complexity by lines of code", legend=False)

for i in range(len(df['code_num'])):
    plt.annotate(df['code_num'][i], xy=(df.index[i], df['code_num'][i]), ha='center', va='bottom')

plt.subplots_adjust(bottom=0.25)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.savefig("scripts/min_code/" + datetime.today().strftime('%Y-%m-%d') + ' ' + ' code comparison_' + viz_type, facecolor='white')

plt.savefig('comp_code_' + viz_type, facecolor='white')

