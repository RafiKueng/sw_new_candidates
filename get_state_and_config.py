# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 02:16:15 2015

@author: rafik
"""


state_path = 'data'
state_fn = "%s.state"

cfg_path = 'data'
cfg_fn = "%s.cfg"


import os
import requests as rq


all_models = []
def load_all_models():
    
    with open('all_candidate_models.csv') as f:
        for line in f.readlines():
            all_models.append(line[:-1].split(','))

candidate_id_lookup = {}
def add_candidate_id_lookup():

    with open('candidates.csv') as f:
        lns = f.readlines()
    for line in lns:
        tkn = line.strip().split('\t')
        pid = tkn[0]
        asw = tkn[8]
        
        candidate_id_lookup[asw] = pid
        
    for i, m in enumerate(all_models):
        asw = m[2].split(' ')[0]
        try:
            npid = candidate_id_lookup[asw]
        except KeyError:
            npid = '----'
        opid = m[3]
        
        if not opid=='' and not npid=='----' and not npid == opid:
            print "horrible error!! check pids", m[0], asw, npid, opid
        all_models[i][3] = npid
        


def get_states():
    for i, m in enumerate(all_models):
        print "%5.1f%% getting state %s ..." % (100.0/len(all_models)*i, m[0])
        get_single_model(m[1], m[0])


def get_single_model(tp, mid):
    if tp=='old':
        url = 'http://mite.physik.uzh.ch/result/%s/state.txt' % mid    
    else:
        p1 = mid[:2]
        p2 = mid[2:]
        url = 'http://labs.spacewarps.org/media/spaghetti/%s/%s/state.glass' % (p1, p2)
    
    path = os.path.join(state_path, state_fn % mid)
    
    stream_get(url, path)



def stream_get(filepath, url):
    
    r = rq.get(url, stream=True)
    
    if r.status_code >= 300: # requests takes care of redirects!
        print 'ERROR:', r.status_code
        return

    if 'content-type' in r.headers and 'json' in r.headers['content-type']:
        print 'ERROR while getting %s (%s)' % (filepath, url)

    with open(filepath, 'w') as f:
        for chunk in r.iter_content(1024*4):
            f.write(chunk)
    

def get_configs():
    for i, m in enumerate(all_models):
        print "%5.1f%% getting config %s ..." % (100.0/len(all_models)*i, m[0])
        get_single_config_file(m[1], m[0])
    

def get_single_config_file(tp, mid):
    
    if tp=='old':
        url = 'http://mite.physik.uzh.ch/result/%s/cfg.gls' % mid
    else:
        url = 'http://labs.spacewarps.org:8080/db/spaghetti/%s' % mid
        
    path = os.path.join(cfg_path, cfg_fn % mid)
    
    stream_get(path, url)



def main():
    load_all_models()
    add_candidate_id_lookup()
    #get_states()

main()
