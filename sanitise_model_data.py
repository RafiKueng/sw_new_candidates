# -*- coding: utf-8 -*-
"""
This corrects various things that are wrong in the raw data extracted
from the models / config files in `parse_state_and_config.py`



Created on Thu Oct 29 11:30:31 2015

@author: rafik
"""



import sys, os, csv

import cPickle as pickle

from os.path import join

from settings import settings as S

# make sure this if first run in glass env..
import parse_state_and_config as psac


NAME = os.path.basename(__file__)
I = NAME + ":"
INT = '       '


pickle_fn  = join(S['cache_dir'], 'sane_data.pickle')
csv_fn     = join(S['temp_dir'],  'sane_data.csv')
rawdata_fn = join(S['cache_dir'], 'parsed_state_and_config_files.pickle')


sane_data = {'0000':{'a':1}}
rawdata = {}


def sanitise():
    print I, "main start"
    
    rawdata.update(psac.stateconf_data)
    
        
    



##############################################################################

def save_pickle():
    print I, 'save data to cache (pickle)'
    with open(pickle_fn, 'wb') as f:
        pickle.dump(sane_data, f, -1)
        
def load_pickle():
    print I, 'load cached data from pickle'
    with open(pickle_fn, 'rb') as f:
        return pickle.load(f)

def save_csv():
    print I, 'save_csv'

    with open(csv_fn, 'w') as f:

        fieldnames = ['mid',] + sane_data.values()[0].keys()

        csvw = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        csvw.writeheader()
        
        for mid, v in sane_data.items():
            csvw.write(v.update({'mid':mid}))


### MAIN #####################################################################

if len(sys.argv)>1:

    if '-d' in sys.argv:
        print I,"deleting cache and quitting"
        try:
            os.remove(pickle_fn)
        except OSError:
            pass

       
    sys.exit()
        

#if os.path.isfile(pickle_fn):
#    sane_data = load_pickle()
#    save_csv()
#    
#else:
#    sanitise()
#    save_pickle()
#    save_csv()

sanitise()


