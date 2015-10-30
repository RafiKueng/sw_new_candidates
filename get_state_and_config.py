# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 02:16:15 2015

@author: rafik
"""


import os

import requests as rq

from settings import settings as S, INT
from settings import print_first_line, print_last_line, getI, del_cache
from settings import state_path, state_fn, cfg_path, cfg_fn

import filter_models as FIMO

# safeguard
if not os.path.exists(state_path):
    os.makedirs(state_path)
if not os.path.exists(cfg_path):
    os.makedirs(cfg_path)

      

def get_states():
    for i, mid in enumerate(FIMO.DATA.keys()):
        print INT,"%5.1f%% | getting state %12s " % (100.0/len(FIMO.DATA.keys())*i, mid),
        get_single_state(mid)


def get_single_state(mid):
    if FIMO.DATA[mid]['type']=='old':
        url = 'http://mite.physik.uzh.ch/result/%s/state.txt' % mid    
    else:
        p1 = mid[:2]
        p2 = mid[2:]
        url = 'http://labs.spacewarps.org/media/spaghetti/%s/%s/state.glass' % (p1, p2)
        
    #print url
    
    path = os.path.join(state_path, state_fn % mid)
    
    if not os.path.isfile(path):
        stream_get(url, path)
        print "done"
    else:
        print "state already present, skipping"



def stream_get(url, filepath):
    
    r = rq.get(url, stream=True)
    
    if r.status_code >= 300: # requests takes care of redirects!
        print 'ERROR:', r.status_code
        return

    if 'content-type' in r.headers and 'json' in r.headers['content-type']:
        print 'ERROR while getting %s (%s)' % (filepath, url),
        return

    with open(filepath, 'w') as f:
        for chunk in r.iter_content(1024*4):
            f.write(chunk)
    

def get_configs():
    for i, mid in enumerate(FIMO.DATA.keys()):
        print INT,"%5.1f%% | getting config %12s" % (100.0/len(FIMO.DATA.keys())*i, mid),
        get_single_config_file(mid)
    

def get_single_config_file(mid):
    
    if FIMO.DATA[mid]['type']=='old':
        url = 'http://mite.physik.uzh.ch/result/%s/cfg.gls' % mid
    else:
        url = 'http://labs.spacewarps.org:8080/db/spaghetti/%s' % mid
        
    path = os.path.join(cfg_path, cfg_fn % mid)
    
    if not os.path.isfile(path):
        stream_get(url, path)
        print "done"
    else:
        print "cfg already present, skipping"






### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)

get_states()
get_configs()

print_last_line(I,FIMO.DATA)


