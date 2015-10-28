# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 01:13:26 2015

@author: rafik
"""

import os

import cPickle as pickle

from os.path import join

from settings import settings as S

import get_new_models as gnm
import get_old_models as gom



NAME = os.path.basename(__file__)
I = NAME + ":"


pickle_fn = join(S['cache_dir'], 'comb_models.pickle')
csv_fn    = join(S['temp_dir'],  'comb_models.csv')


comb_models = {}


def combine():
    for mid, data in gom.old_models.items():
        comb_models[mid] = data
    for mid, data in gnm.new_models.items():
        comb_models[mid] = data
        



def save_pickle():
    print I, 'save data to cache (pickle)'
    with open(pickle_fn, 'wb') as f:
        pickle.dump(comb_models, f, -1)
        
def load_pickle():
    print I, 'load cached data from pickle'
    with open(pickle_fn, 'rb') as f:
        return pickle.load(f)

def save_csv():
    print I, 'save_csv'

    with open(csv_fn, 'w') as f:
        for mid, v in comb_models.items():
            f.write(mid + ',' + ','.join(v.values())+'\n')

### MAIN #####################################################################

if os.path.isfile(pickle_fn):
    comb_models = load_pickle()
    save_csv()
    
else:
    combine()
    save_pickle()
    save_csv()
