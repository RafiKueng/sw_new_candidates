# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 23:53:21 2015

@author: rafik
"""

import sys, os
import csv

import requests as rq
import cPickle as pickle

from os.path import join
from StringIO import StringIO


from settings import settings as S

NAME = os.path.basename(__file__)
I = NAME + ":"


pickle_fn = join(S['cache_dir'], 'old_models.pickle')
csv_fn    = join(S['temp_dir'],  'old_models.csv')




DATA = {}




def fetchSLresults():
    '''I abuse the ResultDataTable functinality from SL
    to get all the results, and then filter it, because I'm too lazy
    and aa bit worried to fiddle with sql on the server database...
    
    '''

    print I, "FETCH SL RESULTS:"
    
    slurl = 'http://mite.physik.uzh.ch/tools/ResultDataTable'

    startid = 115 # because the former are rubbish   
    step = 100 # get somany at a time
    maxid = 15000 #15000 #currently: 13220
    

    for i in range(startid, maxid, step):

        print 'working on: %05i - %05i' % (i, i+step-1),
        sys.stdout.flush()
    
        data = '?'+'&'.join([
            "%s-%s" % (i, i+step),
            'type=csv',
            'only_final=true',
            'json_str=false'
        ])
        rsp = rq.get(slurl+data)
        #return rsp
        if rsp.status_code != 200:
            print 'skipping'
            continue
        print "got 'em!"
        sys.stdout.flush()

        filelike = StringIO(rsp.text)
        csvdr = csv.DictReader(filelike)

        for row in csvdr:
            mid, data = parse_row(row)
            if not data['asw'].startswith("ASW"):
                continue
            DATA[mid] = data
            print '   - %s' % mid, data
            

        print 'done'



def parse_row(row):
    '''
    Theres much more data around here..
    But we will get this later anyways using the config files
    '''
    
    mid     = '%06i' % int(row['result_id'])
    
    data = {
        'asw': row['model_name'],
        'lensid':'%05i' % int(row['model_id']),
        'type': 'old'
    }    
    
    return (mid, data)




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
    fetchSLresults()
    save_pickle()
    save_csv()

print '\n',I, "FINISHED\n\n" + '-'*80 + '\n'


