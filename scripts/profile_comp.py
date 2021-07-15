#!/usr/bin/env python3

"""Create bar chart of total cProfile run time of renderFigure across all tested libraries for either the interactive or static track and either the full ('dd') or subset ('dd_subset') database.

Commented out: display snakeviz icicle graph in browser for a single cProfile.
"""

import io
import pstats
import pandas as pd
import glob
from datetime import datetime
import matplotlib.pyplot as plt
from mapcompare.cProfile_viz import num_times

# INPUTS
viz_type = 'static/'
db_name = 'dd_subset'

profiledir = 'mapcompare/profiles/' + viz_type + db_name + "/"

if __name__ == "__main__":

    """
    # Visualise individual cProfile in browser with snakeviz

    # Indicate for which viualisation library to show cProfile snakeviz graph 
    module = 'gpd'

    profilepath = profiledir + module + ' ' + '(' + db_name + ')' + ".prof"

    subprocess.run(["snakeviz", profilepath])
    """


    # Create pandas dataframe with the total cumtimes for each module

    all_files = glob.glob(profiledir + "/*.prof")

    li = []

    for f in all_files:
        
        # sort by cumtimes and print top result to stdout

        p_output = io.StringIO()

        prof_stats = pstats.Stats(f, stream = p_output).sort_stats("cumulative").print_stats(1)
        
        # read content of StringIO buffer into string variable
        # turn relevant portion (last 2 lines) into comma-separated string
        p_output = p_output.getvalue()
        p_output = 'ncalls' + p_output.split('ncalls')[-1]
        result = '\n'.join([','.join(line.rstrip().split(None,5)) for line in p_output.split('\n')])

        # read comma-separated string into dataframe
        df = pd.read_csv(io.StringIO(result), sep=",", header=0)

        # add column with module to identify result
        df['library'] = f.split(' ')[0].split('\\')[1]
        li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)

    df1 = df.groupby('library', as_index=False)['cumtime'].mean().rename(columns={'cumtime': 'mean'})

    df1['std'] = df.groupby('library', as_index=False)['cumtime'].std()['cumtime']

    if viz_type == 'interactive/':
        rename_dict = {'carto': 'Cartopy', 'gpd': 'GeoPandas', 'gplt': 'geoplot', 'bkh': 'Bokeh', 'plotly_py': 'Plotly.py', 'gv': 'GeoViews+\nBokeh', 'hv_ds': 'HoloViews+\ndatashader+\nBokeh'}
    
    else:
        rename_dict = {'carto': 'Cartopy', 'gpd': 'GeoPandas', 'gplt': 'geoplot', 'bkh': 'Bokeh', 'plotly_py': 'Plotly.py', 'gv': 'GeoViews', 'ds': 'Datashader'}
        

    df1['library'].replace(rename_dict, inplace=True)

    if viz_type == 'static/':
        
        x_label = 'Static visualisation via'

    else:

        x_label="Interactive visualisation via"
    
    df1.rename(columns={'library': x_label}, inplace=True)

    # Plot cumtimes to bar chart

    df1.plot.bar(x=x_label, y="mean", yerr=list(df1['std']), ecolor='grey', capsize=5, alpha=0.5, ylabel="seconds", rot='horizontal', title="cProfile: mean cumulative CPU time (runs=" + str(num_times) + ')', legend=False)

    for i in range(len(df1['mean'])):
        plt.annotate("{:.2f}".format(df1['mean'][i]) + 's', xy=(df.index[i], df1['mean'][i]), ha='center', va='bottom')

    plt.subplots_adjust(bottom=0.25)

    plt.savefig(profiledir + datetime.today().strftime('%Y-%m-%d') + ' ' + db_name + ' comparison', facecolor='white')
