# -*- coding: utf-8 -*-
"""
get the data from mite..
use the result tables
http://mite.physik.uzh.ch/tools/ResultDataTable?9415-9714

Created on Tue Oct 27 23:53:21 2015

@author: rafik
"""

import sys, os, csv
import requests as rq
from os.path import join
from StringIO import StringIO

from settings import settings as S, INT, save_pickle, load_pickle, save_csv
from settings import print_first_line, print_last_line, getI, del_cache


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

        print INT,'working on: %05i - %05i' % (i, i+step-1),
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
            print INT*2,'- %s' % mid, data
            

        print INT,'done'



def parse_row(row):
    '''
    Theres much more data around here..
    But we will get this later anyways using the config files
    '''
    
    mid     = '%06i' % int(row['result_id'])
    try:
        parent  = '%06i' % int(row['parent'])
    except ValueError:
        parent = ""
    
    data = {
        'asw': row['model_name'],
        'mid': mid,
        'lensid':'%05i' % int(row['model_id']),
        'created_on': row['created'][0:19],
        'type': 'old',
        'parent' : parent
    }    
    
    return (mid, data)





### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)
pickle_fn = join(S['cache_dir'], 'old_models.pickle')
csv_fn    = join(S['temp_dir'],  'old_models.csv')

if len(sys.argv)>1:
    if '-d' in sys.argv: del_cache(I,pickle_fn)
    print I,"DONE"
    sys.exit()
        

if os.path.isfile(pickle_fn):
    DATA = load_pickle(I, pickle_fn)
else:
    fetchSLresults()
    save_pickle(I, pickle_fn, DATA)
save_csv(I, csv_fn, DATA, 'mid')
    
print_last_line(I,DATA)


