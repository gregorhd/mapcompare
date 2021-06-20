"""Create bar chart of total cProfile run time of renderFigure across all tested libraries or display snakeviz icicle graph in browser for individual libraries.
"""

import os
import io
import cProfile
from functools import wraps
import pstats
import pandas as pd
import glob
from datetime import datetime
import matplotlib.pyplot as plt

viz_type = 'interactive/'
basemap = True

def to_cProfile(func):
    """Create cProfile for the wrapped function if no basemap is added.
    
    This is to avoid tile loading affecting performance measurement of the core rendering functionality.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if basemap:
            return func(*args, **kwargs)
        else:
            p = cProfile.Profile()
            p.enable()

            value = func(*args, **kwargs)

            p.disable()
            p.dump_stats("mapcompare/profiles/" + viz_type + os.path.basename(__file__)[:-3] + ' ' + '(' + db_name + ')' + ".prof")
            
            print(f"\ncProfile created in mapcompare/profiles/" + viz_type + " for {}() in module {}".format(func.__name__, os.path.basename(__file__)))
            return value
    return wrapper

if __name__ == "__main__":

    profiledir = 'mapcompare/profiles/non-interactive/'

    # Set database name to compare results from either the complete or subset db

    db_name = 'dd_subset'


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
        df['mpl interface via'] = f.split(' ')[0].split('\\')[1]
        li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)


    # Plot cumtimes to bar chart

    df.plot.bar(x="mpl interface via", y="cumtime", ylabel="cumulative time in seconds", rot='horizontal', title="cProfile: cumulative CPU time for renderFigure()", legend=False)

    for i in range(len(df['cumtime'])):
        plt.annotate(str(df['cumtime'][i]) + 's', xy=(df.index[i], df['cumtime'][i]), ha='center', va='bottom')

    plt.savefig(profiledir + datetime.today().strftime('%Y-%m-%d') + ' ' + db_name + ' comparison', facecolor='white')



