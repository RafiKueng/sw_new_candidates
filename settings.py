# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 23:04:17 2015

@author: rafik
"""

import os
from os.path import join

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
        stateconf_cache_path
    ]:
    if not os.path.exists(p):
        os.makedirs(p)

# cosmetics
INT = ' '*4 # default 1 level intentsion
