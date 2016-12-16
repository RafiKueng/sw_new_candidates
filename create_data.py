# -*- coding: utf-8 -*-
"""
Here we create and save the final data selcections we use to generate the plots

Created on Fri Oct 30 16:37:03 2015

@author: rafik
"""


import sys, os, csv
import cPickle as pickle
from os.path import join

from settings import settings as S, INT, save_pickle, load_pickle, save_csv
from settings import print_first_line, print_last_line, getI, del_cache

import get_stellar_pop as gspo
import parse_candidates as PACA
import sanitise_model_data as samd


DATASETS = {}


ALL_MODELS = {}

def create_all_models():
    print I,"create all models",
    ALL_MODELS.update(samd.DATA)
    print "DONE"





ONLY_RECENT_MODELS = {}

def create_recent_models():
    print I,"create only recent",

    global tmpp
    tmpp = {}
    for mid, adata in samd.DATA.items():
        asw = adata['asw'] 
        dat = adata['created_on']
        #print INT, '%10s'%mid, asw, dat
    
        if not adata['Mtot_ave_z_corrected'] > 0.0:
            continue
       
        if tmpp.has_key(asw):
            if tmpp[asw]['created_on'] < dat: # if current newer than previous
                tmpp[asw] = adata
        else:
            tmpp[asw] = adata
    
    for asw, data in tmpp.items():
        data['swid'] = PACA.MAP.get(asw, None)
        ONLY_RECENT_MODELS[data['mid']] = data
    
    print "DONE"


CLAUDE_MODELS = {}

def create_claude_models():
    print I,"create claude models",
    
    with open('claude_lenses.csv') as f:
        lines = f.readlines()
    for line in lines:
        elems = [_.strip() for _ in line.split(',')]
        if len(elems)==3 and len(elems[0])>1:
            swid, asw, mid = elems
            
            if not asw in PACA.MAP.keys():
                print "\nasw not found in paca!", mid, asw, swid,
                continue
            if not mid in samd.DATA.keys():
                print "\nmid not found in samd!", mid, asw, swid,
                continue
            if samd.DATA[mid]['sig_fact'] is None:
                print "\nmid has no messured z", mid, asw, swid,
                continue
            
            data = samd.DATA[mid]
            data['swid'] = PACA.MAP.get(asw, None)
            CLAUDE_MODELS[mid] = data
    
    print "DONE"



LENS_CANDIDATES = {}

def create_lens_candidates():
    print I,"candidate lenses",
    LENS_CANDIDATES.update(gspo.DATA)
    print "DONE"


    
def get_map(data):
    m = {}
    m['swid2model'] = dict(((m['swid'], k) for k,m in data.items()))
    m['asw2model'] = dict(((m['asw'], k) for k,m in data.items() if m.get('asw')))
    return m
    
    

MAPS = {}

def create_maps():
    print I,"create maps",
    MAPS['swid2asw'] = dict((v['swid'], k) for k, v in PACA.DATA.items())
    MAPS['asw2swid'] = dict((k, v['swid']) for k, v in PACA.DATA.items())
    
    #MAPS['swid2model'] = dict(((m['swid'], k) for k,m in ONLY_RECENT_MODELS.items()))
    #MAPS['asw2model'] = dict(((m['asw'], k) for k,m in ONLY_RECENT_MODELS.items() if m.get('asw')))
    
    MAPS['asw2all_models'] = dict(((m['asw'], []) for k,m in ALL_MODELS.items() if m.get('asw')))
    for k,m in ALL_MODELS.items():
        if "asw" in m:
            MAPS['asw2all_models'][m['asw']].append(k)

    MAPS['swid2all_models'] = dict(((MAPS['asw2swid'][s], m) for s, m in MAPS['asw2all_models'].items()))
    print "DONE"


##############################################################################


def define_datasets():
    reg(0,'all_models', ALL_MODELS, create_all_models, pkey='mid')
    reg(1,'only_recent_models', ONLY_RECENT_MODELS, create_recent_models,pkey='mid')
    reg(2,'claude_models', CLAUDE_MODELS, create_claude_models, pkey='mid')
    reg(3,'lens_candidates', LENS_CANDIDATES, create_lens_candidates, pkey='asw')
    reg(4,'maps', MAPS, create_maps, pkey=None)


def reg(iD, name, data, fn, pkey):
    DATASETS[name] = {
        'iD'        : iD, # defines the ordering
        'data'      : data,
        'fn'        : fn,
        'pkey'      : pkey,
#        'pickle_fn' : join(S['cache_dir'], name+'.pickle'),
#        'csv_fn'    : join(S['temp_dir'],  name+'.csv')
    }


### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)

define_datasets()


if len(sys.argv)>1:
    if '-d' in sys.argv:
        print I,"deleting cache and quitting"
        for name in DATASETS.keys():
            fn = join(S['cache_dir'], name+'.pickle')
            print INT,fn
            try:
                os.remove(fn)
            except OSError:
                pass

       
    sys.exit()
        
for iD, name, val in sorted([ (v['iD'], k, v) for k,v in DATASETS.items()]):
    data = val['data']
    fn = val['fn']
    pkey = val['pkey']
    
    pickle_fn = join(S['cache_dir'], name+'.pickle')
    csv_fn    = join(S['temp_dir'],  name+'.csv')
    
    if os.path.isfile(pickle_fn):
        data.update(load_pickle(pickle_fn))
        
    else:
        fn()
        #save_pickle(pickle_fn, data)

    #save_csv(I, csv_fn, data, pkey)
    print '-----'

print_last_line(I,DATASETS)

