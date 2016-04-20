# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 23:04:17 2015

@author: rafik
"""

import os, csv
from os.path import join
import cPickle as pickle


settings = {

# setup directories
    'asset_dir': 'assets', # use for external, static files that should not change (downloads)
    'cache_dir': 'cache',  # use for internal, possibly changing files (pickles)
    'input_dir': 'input', # input / data files generated manually, used here
    'output_dir': 'output', # where the calculated data is stored
    'temp_dir': 'temp', # use this dir to create temp files, like csv versions of pickle files for checking



    
}

_=settings

# where to store all the state and config files (uses gigabytes!)
state_path = join(_['asset_dir'], 'models')
cfg_path = join(_['asset_dir'], 'models')
sworg_path = join(_['asset_dir'], 'spacewarps_orginals')

# where to store the processed state file pickles
stateconf_cache_path = join(_['cache_dir'], 'stateconf')

# how to name the config and state files..
state_fn = "%s.state"
cfg_fn = "%s.cfg"



# make sure the folders exist
for k,v in settings.items():
    if k.endswith('_dir') and not os.path.exists(v):
        os.makedirs(v)

for p in [
        state_path,
        cfg_path,
        sworg_path,
        stateconf_cache_path
    ]:
    if not os.path.exists(p):
        os.makedirs(p)

# cosmetics
INT = ' '*4 # default 1 level intentsion







def save_pickle(I, fn, data):
    print I, 'save data to cache (pickle)',
    with open(fn, 'wb') as f:
        pickle.dump(data, f, -1)
    print "DONE"
        
def load_pickle(I, fn):
    print I, 'load cached data from pickle',
    with open(fn, 'rb') as f:
        p = pickle.load(f)
    print "DONE"
    return p

def save_csv(I, fn, data, pkey_n):
    print I, 'save_csv',

    with open(fn, 'w') as f:
        
        # get all available keys
        keys = set()
        for v in data.values():
            keys.update(v.keys())
        keys = [pkey_n,]+list(keys)

        # write output
        csvw = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        csvw.writeheader()
        for pkey, v in data.items():
            d=dict()
            d.update({pkey_n:pkey})
            d.update(v)
            csvw.writerow(d)

    print "DONE"


def getI(f):
    return os.path.basename(f)+':'

def print_first_line(I):
    print '\n',I,"STARTING\n"
    
def print_last_line(I, data=None):
    s=" (got %i entries)" % len(data) if data else ""
    print '\n',I, "FINISHED%s\n" % s
    print '-'*80

def del_cache(I,fn):
    print I,"deleting cache and quitting"
    try:
        os.remove(fn)
    except OSError:
        pass
