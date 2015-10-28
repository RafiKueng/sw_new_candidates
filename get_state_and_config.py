# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 02:16:15 2015

@author: rafik
"""


import os

import requests as rq

from os.path import join
from settings import settings as S

from filter_models import filt_models as models

NAME = os.path.basename(__file__)
I = NAME + ":"


state_path = join(S['asset_dir'], 'models')
state_fn = "%s.state"

cfg_path = join(S['asset_dir'], 'models')
cfg_fn = "%s.cfg"


#all_models = get_all_models.data
      

def get_states():
    for i, mid in enumerate(models.keys()):
        print "%5.1f%% getting state %12s " % (100.0/len(models.keys())*i, mid),
        get_single_state(mid)


def get_single_state(mid):
    if models[mid]['type']=='old':
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
        print 'ERROR while getting %s (%s)' % (filepath, url)
        return

    with open(filepath, 'w') as f:
        for chunk in r.iter_content(1024*4):
            f.write(chunk)
    

def get_configs():
    for i, mid in enumerate(models.keys()):
        print "%5.1f%% getting config %12s" % (100.0/len(models.keys())*i, mid),
        get_single_config_file(mid)
    

def get_single_config_file(mid):
    
    if models[mid]['type']=='old':
        url = 'http://mite.physik.uzh.ch/result/%s/cfg.gls' % mid
    else:
        url = 'http://labs.spacewarps.org:8080/db/spaghetti/%s' % mid
        
    path = os.path.join(cfg_path, cfg_fn % mid)
    
    if not os.path.isfile(path):
        stream_get(url, path)
        print "done"
    else:
        print "cfg already present, skipping"






### MAIN ####################################################################

get_states()
get_configs()

