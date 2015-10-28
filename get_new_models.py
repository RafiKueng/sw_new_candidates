# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 00:53:28 2015

@author: rafik
"""


import sys, os
import csv

import requests as rq
import cPickle as pickle

from os.path import join
from StringIO import StringIO


from settings import settings as S

NAME = os.path.basename(sys.argv[0])
I = NAME + ":"


pickle_fn = join(S['cache_dir'], 'new_models.pickle')
csv_fn    = join(S['temp_dir'],  'new_models.csv')


new_models = {}


def get_from_labs():
    print I, "fetch swlabs"

    r1 = rq.get('http://labs.spacewarps.org:8080/db/spaghetti/_design/isfinal/_view/isfinal')
    rows = r1.json()['rows']
    for row in rows:
        try:
            mid = row['id']
            lensid = row['value']['lens_id']
            r2 = rq.get('http://labs.spacewarps.org:8080/db/lenses/'+lensid)
            asw = r2.json()['metadata']['zooniverse_id']
        except KeyError:
            print '    FAILED: ', mid
            continue
            
        data = {
            'asw': asw,
            'lensid': lensid,
            'type': 'new'
        }    

        print '    got: ', mid, asw
        new_models[mid] = data





def save_pickle():
    print I, 'save data to cache (pickle)'
    with open(pickle_fn, 'wb') as f:
        pickle.dump(new_models, f, -1)
        
def load_pickle():
    print I, 'load cached data from pickle'
    with open(pickle_fn, 'rb') as f:
        return pickle.load(f)

def save_csv():
    print I, 'save_csv'

    with open(csv_fn, 'w') as f:
        for mid, v in new_models.items():
            f.write(mid + ',' + ','.join(v.values())+'\n')

### MAIN #####################################################################

if os.path.isfile(pickle_fn):
    new_models = load_pickle()
    save_csv()
    
else:
    get_from_labs()
    save_pickle()
    save_csv()
