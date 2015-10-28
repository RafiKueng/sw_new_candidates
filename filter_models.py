# -*- coding: utf-8 -*-
"""
this will load all models and returns only the ones, that were in the candidates list


Created on Wed Oct 28 01:19:01 2015

@author: rafik
"""


import os

import cPickle as pickle

from os.path import join

from settings import settings as S

import combine_models as cm
import parse_candidates as cands



NAME = os.path.basename(__file__)
I = NAME + ":"


pickle_fn = join(S['cache_dir'], 'filt_models.pickle')
csv_fn    = join(S['temp_dir'],  'filt_models.csv')


filt_models = {}


def filter_models():
    print I, "filtering"

    for mid, data in cm.comb_models.items():
        asw = data['asw']
        print "   ", mid, asw, 
        
        if asw in cands.get_swid.keys():
            filt_models[mid] = data
            print 'taken'
        else:
            print "GONE"



def save_pickle():
    print I, 'save data to cache (pickle)'
    with open(pickle_fn, 'wb') as f:
        pickle.dump(filt_models, f, -1)
        
def load_pickle():
    print I, 'load cached data from pickle'
    with open(pickle_fn, 'rb') as f:
        return pickle.load(f)

def save_csv():
    print I, 'save_csv'

    with open(csv_fn, 'w') as f:
        for mid, v in filt_models.items():
            f.write(mid + ',' + ','.join(v.values())+'\n')

### MAIN #####################################################################

if os.path.isfile(pickle_fn):
    filt_models = load_pickle()
    save_csv()
    
else:
    filter_models()
    save_pickle()
    save_csv()
