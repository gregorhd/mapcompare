#!/usr/bin/env python3

"""Create bar chart of total cProfile run time of renderFigure across all tested libraries for either the interactive or static track and either the full ('dd') or subset ('dd_subset') database.

Commented out: (a) display snakeviz icicle graph in browser for a single cProfile, (b) save final dataframe to docx table.
"""

import io
import pstats
import pandas as pd
import glob
import subprocess
from datetime import datetime
import matplotlib.pyplot as plt
import docx # uncomment last section below to save dataframe to docx
from mapcompare.cProfile_viz import num_times

# INPUTS
viz_type = 'interactive/'
db_name = 'dd_subset'

profiledir = 'mapcompare/profiles/' + viz_type + db_name + "/"

def snakeviz(module, viz_type, db_name):
    """Visualise cProfile for a particular module in browser with snakeviz.
    
    Parameters
    ----------
    module : str
        Abbreviated module name as provided in scripts/
    viz_type : str
        'interactive/' or 'static/' visualisation type.
    db_name : str
        'dd' or 'dd_subset'    
    Returns
    ----------
    Snakeviz icicle graph in browser
    
    """
    profilepath = 'mapcompare/profiles/' + viz_type + db_name + "/" + module + ' (' + db_name + ')' + " run 1.prof"

    subprocess.run(["snakeviz", profilepath])
    
if __name__ == "__main__":

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

    df1 = df.groupby('library', as_index=False)['cumtime'].mean().rename(columns={'cumtime': 'mean'}).round(decimals=3)

    df1['std'] = df.groupby('library', as_index=False)['cumtime'].std()['cumtime'].round(decimals=3)

    if viz_type == 'interactive/':
        rename_dict = {'bkh': 'Bokeh', 'plotly_py': 'Plotly.py', 'gv': 'GeoViews+\nBokeh', 'gv_ds': 'GeoViews+\ndatashader+\nBokeh Server', 'hv_plot': 'hvPlot+\nHoloViews+\nBokeh*'}
    
    else:
        rename_dict = {'alt': 'Altair+\nVega-Lite', 'carto': 'Cartopy+\nMatplotlib', 'ds': 'Data-\nshader*', 'gpd': 'GeoPandas+\nMatplotlib', 'gplt': 'geoplot+\nMatplotlib', 'gv': 'GeoViews+\nMatplotlib'}
        

    df1['library'].replace(rename_dict, inplace=True)

    if viz_type == 'static/':
        
        x_label = 'Static visualisation via'

    else:

        x_label="Interactive visualisation via"
    
    df1.rename(columns={'library': x_label}, inplace=True)

    # Plot cumtimes to bar chart

    ax = df1.plot.bar(x=x_label, y="mean", yerr=list(df1['std']), ecolor='grey', capsize=5, alpha=0.5, ylabel="seconds", rot='horizontal', title="cProfile: mean cumulative CPU runtime ("+ str(num_times) + ' runs)', legend=False)

    for i in range(len(df1['mean'])):
        plt.annotate("{:.2f}".format(df1['mean'][i]) + 's', xy=(df.index[i], df1['mean'][i]), ha='center', va='bottom')

    plt.subplots_adjust(bottom=0.25)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.savefig(profiledir + datetime.today().strftime('%Y-%m-%d') + ' ' + db_name + ' comparison', facecolor='white')

    plt.savefig('comp_profile_' + viz_type[:-1] + '_' + db_name, facecolor='white')

    # # Create a docx containing the final dataframe

    # # open an existing document
    # doc = docx.Document()

    # # add a table to the end and create a reference variable
    # # extra row is so we can add the header row
    # t = doc.add_table(df1.shape[0]+1, df1.shape[1])

    # # add the header rows.
    # for j in range(df1.shape[-1]):
    #     t.cell(0,j).text = df1.columns[j]

    # # add the rest of the data frame
    # for i in range(df1.shape[0]):
    #     for j in range(df1.shape[-1]):
    #         t.cell(i+1,j).text = str(df1.values[i,j])

    # save the doc
    # doc.save(profiledir + datetime.today().strftime('%Y-%m-%d') + ' ' + db_name + ' dataframe.docx')
    

    # snakeviz('bkh', 'interactive/', 'dd')
    