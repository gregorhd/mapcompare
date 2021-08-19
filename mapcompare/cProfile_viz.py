"""Defines the to_cProfile() decorator function applied to renderFigure() in the executables for each visualisation library.

cProfiles are only created for decorated functions, if basemap=False to not skew results due to tile fetching.
"""

from subprocess import STARTF_USESHOWWINDOW
import wrapt
import os
import re
import inspect
import cProfile

# INPUT
num_times = 10 # number of runs when benchmarking

@wrapt.decorator
def to_cProfile(func, instance, args, kwargs):
    """Create cProfile of the wrapped function only if no basemap is added.
    
    This is to avoid tile loading affecting performance measurement of the core rendering functionality.
    """    
    
    db_name = re.findall(r"'(.*?)'", str(inspect.signature(func).parameters['db_name']).split('=')[1])[0]
        
    viz_type = re.findall(r"'(.*?)'", str(inspect.signature(func).parameters['viz_type']).split('=')[1])[0]

    basemap_val = str(inspect.signature(func).parameters['basemap'])[-5:]

    profiledir = 'mapcompare/profiles/' + viz_type + db_name + "/"

    if not os.path.exists(profiledir):
        os.makedirs(profiledir)

    mod_name = os.path.basename(inspect.getmodule(func).__file__)

    """The below if and elif block make performance benchmarking for successive runs
    manual except for the 'out of competition' runs of datashader.
    This is to keep approaches like reuse of already drawn canvases from skewing results.
    """
    
    if basemap_val == 'False' and not mod_name.startswith('ds'):

        profilepath = profiledir + mod_name[:-3] + ' (' + db_name + ")" + " run " + str(num_times) + ".prof"

        if os.path.exists(profilepath):
            print("Profiling complete already. Exiting.")

        else:

            for i in range(num_times):
                
                profilepath = profiledir + mod_name[:-3] + ' (' + db_name + ")" + " run " + str(i + 1) + ".prof"

                while i < num_times:

                    if not os.path.exists(profilepath):

                        p = cProfile.Profile()
                        p.enable()

                        value = func(*args, **kwargs)

                        p.disable()
                        p.dump_stats(profilepath)

                        print(f"\ncProfile created in " + profiledir + " for run #{} of {}() in module {}.".format(str(i + 1), func.__name__, mod_name))

                        if i + 1 < num_times:
                            print("Run {} more time(s).".format(str(num_times - i - 1)))
                        
                        elif i + 1 == num_times:
                            print("Profiling complete.")

                        return value

                    i += 1
    
    # execute datashader's renderFigure() in a loop to demonstrate effect of numba
    # on performance during first and subsequent runs
    
    elif mod_name.startswith('ds'):
        
        for i in range(num_times):

            p = cProfile.Profile()
            p.enable()

            value = func(*args, **kwargs)

            p.disable()
            p.dump_stats(profiledir + mod_name[:-3] + ' ' + '(' + db_name + ")" + " run " + str(i + 1) + ".prof")
            
            print(f"\ncProfile created in " + profiledir + " for run #{} of {}() in module {}".format(str(i + 1), func.__name__, mod_name))

        return value

    else:
        return func(*args, **kwargs)