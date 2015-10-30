# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 00:53:28 2015

@author: rafik
"""


import sys, os
import requests as rq
from os.path import join

from settings import settings as S, INT, save_pickle, load_pickle, save_csv
from settings import print_first_line, print_last_line, getI, del_cache


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
            'mid': mid,
            'lensid': lensid,
            'type': 'new'
        }    

        print '    got: ', mid, asw
        DATA[mid] = data



### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)
pickle_fn = join(S['cache_dir'], 'new_models.pickle')
csv_fn    = join(S['temp_dir'],  'new_models.csv')

if len(sys.argv)>1:
    if '-d' in sys.argv: del_cache(I,pickle_fn)
    print I,"DONE"
    sys.exit()
        

if os.path.isfile(pickle_fn):
    DATA = load_pickle(I, pickle_fn)
else:
    get_from_labs()
    save_pickle(I, pickle_fn, DATA)
save_csv(I, csv_fn, DATA, 'mid')
    
print_last_line(I, DATA)

