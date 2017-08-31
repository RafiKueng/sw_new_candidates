# -*- coding: utf-8 -*-
"""
this will load all models and returns only the ones, that were in the
candidates list.

We filter this early in the stage such that we don't download and process
too much data


Created on Wed Oct 28 01:19:01 2015

@author: rafik
"""


import os, sys
from os.path import join

from settings import settings as S, INT, save_pickle, load_pickle, save_csv
from settings import print_first_line, print_last_line, getI, del_cache


import combine_models as COMO
import parse_candidates as PACA


DATA = {}


def filter_models():
    print I, "filtering... select:"

    for mid, dat in COMO.DATA.items():
        asw = dat['asw']
        
        if asw in PACA.ASW2SWID.keys():
            DATA[mid] = dat
            print INT, "%10s (%s) incl" % (mid, asw)
        else:
            print INT, "%10s (%s) GONE" % (mid, asw)

    print I,"status: total: %i / selected: %i" % (len(COMO.DATA.keys()), len(DATA.keys()))



### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)
pickle_fn = join(S['cache_dir'], 'filtered_models.pickle')
csv_fn    = join(S['temp_dir'],  'filtered_models.csv')

if len(sys.argv)>1:
    if '-d' in sys.argv: del_cache(I,pickle_fn)
    print I,"DONE"
    sys.exit()
        

if os.path.isfile(pickle_fn):
    DATA = load_pickle(I, pickle_fn)
else:
    filter_models()
    save_pickle(I, pickle_fn, DATA)
save_csv(I, csv_fn, DATA, 'mid')
    
print_last_line(I,DATA)
