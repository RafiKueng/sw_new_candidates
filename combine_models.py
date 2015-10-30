# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 01:13:26 2015

@author: rafik
"""

import os, sys
from os.path import join

from settings import settings as S, INT, save_pickle, load_pickle, save_csv
from settings import print_first_line, print_last_line, getI, del_cache

import get_new_models as GNMO
import get_old_models as GOMO


DATA = {}


def combine():

    for mid, data in GOMO.DATA.items():
        DATA[mid] = data
    for mid, data in GNMO.DATA.items():
        DATA[mid] = data
        



### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)

pickle_fn = join(S['cache_dir'], 'combined_models.pickle')
csv_fn    = join(S['temp_dir'],  'combined_models.csv')

if len(sys.argv)>1:
    if '-d' in sys.argv: del_cache(I,pickle_fn)
    print I,"DONE"
    sys.exit()
        

if os.path.isfile(pickle_fn):
    DATA = load_pickle(I, pickle_fn)
else:
    combine()
    save_pickle(I, pickle_fn, DATA)

save_csv(I, csv_fn, DATA, 'mid')
    
print_last_line(I,DATA)
