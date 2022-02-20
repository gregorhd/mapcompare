"""Compare number of lines of code for each reduced code version,
excluding comments and blank lines.

Creates dark themed plots.
"""

import os
import glob
import pandas as pd

import matplotlib.pyplot as plt
from datetime import datetime

from sqlalchemy import ForeignKey

# INPUTS
viz_type = 'static'

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
    rename_dict = {'bkh': 'Bokeh', 'plotly_py': 'Plotly.py\n(auto\nzoom)', 'plotly_py_manual': 'Plotly.py\n(manual\nzoom)', 'gv': 'GeoViews\n+Bokeh', 'gv_ds': 'GeoViews\n+datashader\n+Bokeh Server', 'hv_plot': 'hvPlot\n+GeoViews\n+Bokeh'}

else:
    rename_dict = {'alt': 'Altair\n+Vega-Lite', 'carto': 'Cartopy\n+Matplotlib', 'ds': 'Data-\nshader', 'gpd': 'GeoPandas\n+Matplotlib', 'gplt': 'geoplot\n+Matplotlib'}

df['library'].replace(rename_dict, inplace=True)

if viz_type == 'interactive':

    x_label="Interactive visualisation via"

else:

    x_label = 'Static visualisation via'

df.rename(columns={'library': x_label}, inplace=True)

# Plot cumtimes to bar chart

ax = df.plot.bar(x=x_label, y="code_num", alpha=0.5, rot='horizontal', legend=False, facecolor="#D9D9D9")

for i in range(len(df['code_num'])):
    plt.annotate(df['code_num'][i], xy=(df.index[i], df['code_num'][i]), ha='center', va='bottom', color='white')

plt.subplots_adjust(bottom=0.25)
plt.rcParams.update({"figure.facecolor": BACKGROUND})

FOREGROUND = '#BFBFBF'
BACKGROUND = '#443C29'
ax.set_xlabel(x_label, color=FOREGROUND)
ax.set_ylabel("# of lines of code", color=FOREGROUND)
ax.tick_params(axis='x', colors=FOREGROUND)
ax.tick_params(axis='y', colors=FOREGROUND)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color(FOREGROUND)
ax.spines["bottom"].set_color(FOREGROUND)

ax.set_facecolor(BACKGROUND)
ax.set_title("Code complexity by lines of code", pad=20, color='white')

plt.tight_layout()

plt.savefig("scripts/min_code/" + datetime.today().strftime('%Y-%m-%d') + ' ' + ' code comparison_' + viz_type + '_dark.jpg', dpi=300, facecolor=BACKGROUND)

