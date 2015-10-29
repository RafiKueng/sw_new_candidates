# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 00:53:28 2015

@author: rafik
"""


import sys, os, csv

import requests as rq
import cPickle as pickle

from os.path import join

from settings import settings as S


NAME = os.path.basename(__file__)
I = NAME + ":"


pickle_fn = join(S['cache_dir'], 'new_models.pickle')
csv_fn    = join(S['temp_dir'],  'new_models.csv')


DATA = {}


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
        DATA[mid] = data






##############################################################################


def save_pickle():
    print I, 'save data to cache (pickle)',
    with open(pickle_fn, 'wb') as f:
        pickle.dump(DATA, f, -1)
    print "DONE"
        
def load_pickle():
    print I, 'load cached data from pickle',
    with open(pickle_fn, 'rb') as f:
        p = pickle.load(f)
    print "DONE"
    return p

def save_csv(pkey_n = 'mid'):
    print I, 'save_csv',

    with open(csv_fn, 'w') as f:
        
        # get all available keys
        keys = set([pkey_n])
        for v in DATA.values():
            keys.update(v.keys())

        # write output
        csvw = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        csvw.writeheader()
        for pkey, v in DATA.items():
            d=dict()
            d.update({pkey_n:pkey})
            d.update(v)
            csvw.writerow(d)

    print "DONE"


### MAIN #####################################################################

print I, "START\n"

if len(sys.argv)>1:

    if '-d' in sys.argv:
        print I,"deleting cache and quitting"
        try:
            os.remove(pickle_fn)
        except OSError:
            pass

    print I,"DONE"
    sys.exit()
        

if os.path.isfile(pickle_fn):
    DATA = load_pickle()
    save_csv()
    
else:
    get_from_labs()
    save_pickle()
    save_csv()

print '\n',I, "FINISHED\n\n" + '-'*80 + '\n'

