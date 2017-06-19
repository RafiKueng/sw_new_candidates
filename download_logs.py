# -*- coding: utf-8 -*-
"""
download the log files

Created on Mon Jun 19 18:40:44 2017

@author: rafik
"""

from os import makedirs
from os.path import join, isfile, isdir

import settings as SET
reload(SET)
SET.set_mpl_rc()
STY = SET.styles
S = SET.settings

import requests as rq
#from PIL import Image
import numpy as np
#from scipy import ndimage
from scipy import misc
import matplotlib.pyplot as plt
import gzip


#from settings import settings as S, INT
#from settings import print_first_line, print_last_line, getI

import find_point
import create_data as CRDA

MODELS, MAPS = CRDA.get_dataset_data()

DBG = SET.DEBUG
#DBG = True

DBG_swid = "SW01"
DBG_mid = ['007350', "EUTVAVV6XJ"]

fpath = SET.spllog_path
filename = "{_[swid]}_{_[asw]}_{_[mid]}.log"




##############################################################################



#def main():
#    '''
#    Download one set of images for a particular mid
#    '''
    
data = MODELS
n_models = len(data.items())
print "main"

res = {}
res2 = []
res3 = [[] for _ in range(20)]

# this used to be a for loop downloading all the files, but isn't anymore
# because all the other files are generated in some other way
    
for i, blob in enumerate(sorted(data.items())):

    mid, M = blob
    asw = M['asw']
    swid = M.get('swid', "SWXX")
    typ = M['type']
    
    if DBG and not swid==DBG_swid:
        print "skip no swid", swid, DBG_swid
        continue
    if DBG and not mid in DBG_mid:
        print "skip no mid", mid, DBG_mid
        continue
    
    print "(%3.0f%%) getting log for mid:%-10s asw:%s swid:%s)" % (100.0*i/n_models, mid, asw, swid)
    
    logdir  = fpath
    logfilename = join(fpath, filename.format(_={'asw':asw, 'mid':mid,'swid':swid}))
    logfilenamegz = join(fpath, filename.format(_={'asw':asw, 'mid':mid,'swid':swid})) + ".gz"

    if not isdir(logdir):
        makedirs(logdir)

    
    if typ == "new":
        url = "http://labs.spacewarps.org/media/spaghetti/%s/%s/glass.log" % (mid[0:2],mid[2:])
        # http://labs.spacewarps.org/media/spaghetti/2V/R4GPC2FU/glass.log
    elif typ == "old":
        url = 'http://mite.physik.uzh.ch/result/' + '%06i/log.txt' % int(mid)
        # http://mite.physik.uzh.ch/result/013397/log.txt
    else:
        print "ERROR!!!!"
        continue

    if isfile(logfilenamegz) and not DBG:
        print 'SKIPPING DL (already present)'
        with gzip.open(logfilenamegz, 'rb') as f:
            log = f.read()
        print "file opened"

    else:
    
        r = rq.get(url, stream=True)
        
        if r.status_code >= 300: # reuqests takes care of redirects!
            print 'ERROR:', r.status_code
            continue

        if 'content-type' in r.headers and 'json' in r.headers['content-type']:
            print 'ERROR: no valid png file (json)' 
            continue

        with gzip.open(logfilenamegz, 'wb') as f:
            log = r.content
            # correct for "log append instead replace" bug
            i = log.rfind('GLASS version 0.1')-81
            if i<0: i=0
            log = log[i:]
            #print "i",i
            f.write(log)
            
        print 'downloaded,',
    

    #print len(log.split('\n'))
    logg = log.split('\n')
    
    i = log.rfind('SAMPLEX TIMINGS')
    if i<=0:
        print "no data in log for mid",mid
        continue
    v = []

#[('Initial inner point', '0.73'),
# ('Estimate eigenvectors', '0.48'),
# ('Burn-in', '338.10'),
# ('Modeling', '37.96'),
# ('Max thread time', '34.67'),
# ('Avg thread time', '34.33'),
# ('Total wall-clock time', '377.46')]
    
    pxr = int(logg[8].split('=')[1])
    s = 'Number of CPUs used     = '
    ncpu = int(log[log.rfind(s) + len(s)])
    
    for k, e in enumerate(log[i:].split('\n')[2:8]):
        l1 = e[:23].strip()
        l2 = e[23:]
        
        if k==4:
            l21 = l2.split(" ")[0][:-1]
            l22 = l2.split(" ")[1][:-1]
            #l.append(("Max thread time", l21))
            #l.append(("Avg thread time", l22))
            v.append(l21)
            v.append(l22)
        else:
            l2 = l2[:-1]
            #l.append((l1, l2))
            v.append(l2)
    
    #v = np.array(v, dtype=np.float)
    v = [float(_) for _ in v]
    
    res[mid] = v
    res2.append(v)
    
    res3[pxr].append(v+[mid,ncpu])

    print 'done'
#res["_header"] = [
#    'Initial inner point',
#    'Estimate eigenvectors',
#    'Burn-in',
#    'Modeling',
#    'Max thread time',
#    'Avg thread time',
#    'Total wall-clock time']

res2 = np.array(res2)
print np.mean(res2, 0)

ave_per_pxr = {}
max_per_pxr = {}
min_per_pxr = {}
std_per_pxr = {}
var_per_pxr = {}


for i,u in enumerate(res3):
    if len(u)>0:
        print i, np.mean(u,0)
        ave_per_pxr[i] = np.mean(u,0)
        min_per_pxr[i] = np.min(u,0)
        max_per_pxr[i] = np.max(u,0)
        std_per_pxr[i] = np.std(u,0)
        var_per_pxr[i] = np.var(u,0)

#
#I = SET.getI(__file__)
#SET.print_first_line(I)
#asb = main()
#SET.print_last_line(I)


