# -*- coding: utf-8 -*-
"""
Here we create and save the final data selcections we use to generate the plots

Created on Fri Oct 30 16:37:03 2015

@author: rafik
"""


import sys, os
import cPickle as pickle
from os.path import join

import settings as SET
reload(SET)
from settings import settings as S, INT #, save_pickle, load_pickle, save_csv
#from settings import print_first_line, print_last_line, getI #, del_cache

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

    
    
SELECTED_MODELS = {}

def create_selected_models():
    print I,"create selected models",

    with open('input/selected_models.csv') as f:
        lines = f.readlines()
    
    for line in lines:
        elems = [_.strip() for _ in line.split(',')]
        if len(elems)==2 and len(elems[0])>1 and len(elems[1])>1:
            swid, mid = elems
            asw = PACA.MAP.get(swid, None)
            
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
            SELECTED_MODELS[mid] = data
    
    print "DONE"
    


LENS_CANDIDATES = {}

def create_lens_candidates():
    print I,"candidate lenses",
    LENS_CANDIDATES.update(gspo.DATA)
    print "DONE"


    
def get_maps(data):
    m = {}
    
    # those below are outdated, always use the lists!
#    m['swid2mid'] = dict(((m['swid'], k) for k,m in data.items()))
#    m['asw2mid'] = dict(((m['asw'], k) for k,m in data.items() if m.get('asw')))

    m['swid2asw'] = dict((v['swid'], k) for k, v in PACA.DATA.items())
    m['asw2swid'] = dict((k, v['swid']) for k, v in PACA.DATA.items())
    
    m['asw2mids'] = dict(((mm['asw'], []) for k,mm in data.items() if mm.get('asw')))
    for k,mm in data.items():
        if "asw" in mm:
            m['asw2mids'][mm['asw']].append(k)
        else:
            print "skipping:", k 

    m['swid2mids'] = dict(((mm['swid'], []) for k,mm in data.items() if mm.get('swid')))
    for k,mm in data.items():
        if "swid" in mm:
            m['swid2mids'][mm['swid']].append(k)
    return m
    
    

    
#MAPS = {}
#
#def create_maps():
#    print I,"create maps",
#    MAPS['swid2asw'] = dict((v['swid'], k) for k, v in PACA.DATA.items())
#    MAPS['asw2swid'] = dict((k, v['swid']) for k, v in PACA.DATA.items())
#    
#    #MAPS['swid2model'] = dict(((m['swid'], k) for k,m in ONLY_RECENT_MODELS.items()))
#    #MAPS['asw2model'] = dict(((m['asw'], k) for k,m in ONLY_RECENT_MODELS.items() if m.get('asw')))
#    
#    MAPS['asw2all_models'] = dict(((m['asw'], []) for k,m in ALL_MODELS.items() if m.get('asw')))
#    for k,m in ALL_MODELS.items():
#        if "asw" in m:
#            MAPS['asw2all_models'][m['asw']].append(k)
#
#    MAPS['swid2all_models'] = dict(((MAPS['asw2swid'][s], m) for s, m in MAPS['asw2all_models'].items()))
#    print "DONE"

    

##############################################################################

# this would be a more generalised approach, but we don't use it due to time
# constraints (would need more time to program than it's worth it...)

_dataset = None
_data    = None
_maps    = None
'''
def GET_DATASET(dataset_str = SET.DATASET):
    
    _dataset = DATASETS[dataset_str]

    _data = _dataset['data']
    
    _maps = {}
    _maps.update(MAPS)
    _maps.update(get_map(_data))
    
    return _data, _maps


def GET_MODEL(swid):

    if _dataset is None:
        print "define a dataset to use first calling GET_DATASET"
        return False
        
    return 
'''

def get_dataset_data(dataset_str = None):
    reload(SET)
    
    if dataset_str is None:
        dataset_str = SET.DATASET_TO_USE
    print "-"*80
    print "using dataset:", dataset_str
    print "-"*80
    data = DATASETS[dataset_str]['data']
    maps = get_maps(data)
    return data, maps

##############################################################################


def define_datasets():
    reg(0,'all_models', ALL_MODELS, create_all_models, pkey='mid')
    reg(1,'only_recent_models', ONLY_RECENT_MODELS, create_recent_models,pkey='mid')
    reg(2,'claude_models', CLAUDE_MODELS, create_claude_models, pkey='mid')
    reg(3,'selected_models', SELECTED_MODELS, create_selected_models, pkey='mid')
    reg(4,'lens_candidates', LENS_CANDIDATES, create_lens_candidates, pkey='asw')
#    reg(5,'maps', MAPS, create_maps, pkey=None)


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

I = SET.getI(__file__)
SET.print_first_line(I)

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
        data.update(SET.load_pickle(pickle_fn))
        
    else:
        fn()
        #save_pickle(pickle_fn, data)

    #save_csv(I, csv_fn, data, pkey)
    print '-----'

SET.print_last_line(I,DATASETS)

