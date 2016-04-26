# -*- coding: utf-8 -*-
"""
execute this file in an interactive glass ipython shell

Does double cache the stuff..
creates per element pickles and a total pickle as all the other scripts do

cd .
../glass/interactive_glass

%run <this_file.py>


If cached files exist, glass is not needed.
So this file can be imported as usual..

Idea. Run on it's own inside glass env first time
afterwards you can just run the rest of the chain


Created on Wed Oct 28 15:07:18 2015

@author: rafik
"""



import sys, os, shutil, glob, json
from os.path import join

import cPickle as pickle
import numpy as np

from settings import settings as S, INT, save_pickle, load_pickle, save_csv
from settings import print_first_line, print_last_line, getI, del_cache
from settings import state_path, state_fn, cfg_path, cfg_fn, stateconf_cache_path

import get_state_and_config as gsac # indirect import.. this file loads stuff genrerated by this module, so even if not used directly we need it to run prior
gsac.I # do this such that the gsac import lookes used ;)


DATA = {}


def parse_mainloop():
    '''
    this scans only those models that have a state AND a config file locally
    available
    '''
    
    print I, "parse stuff"
    
    #
    cfgmids =   set([_.split('/')[2].split('.')[0] for _ in glob.glob(join(cfg_path, cfg_fn % '*'))])
    statemids = set([_.split('/')[2].split('.')[0] for _ in glob.glob(join(state_path, state_fn % '*'))])
    
    # intersect the two sets
    all_mids = list(cfgmids & statemids)
    n_mids = len(all_mids)
    
    print INT,"status:"
    print INT,"- config files:", len(cfgmids)
    print INT,"- state  files:", len(statemids)
    print INT,"- both   files:", n_mids
    print INT,"-"*40
    print INT,"we are missing:"
    for mid in sorted(list(cfgmids ^ statemids)): # symmetric_difference https://docs.python.org/2/library/sets.html
        print INT," *", mid
    print INT,"-"*40+"\n"
    
    # saveguard
    if not n_mids > 0:
        print INT,"!!! ERROR: NO MODEL AND CONFIG FILES FOUND. ABORTING"
        print INT,"make sure you run 'get_state_and_config' first!"
        sys.exit(1)
    
    
    for i, mid in enumerate(sorted(all_mids)):
    
        print INT,"%5.1f%% (% 3i/% 3i) working on %10s ..." % (100.0/n_mids*i, i, n_mids, mid)
        
        DATA[mid] = {}
        
        data1 = parse_state(mid)
        DATA[mid].update(data1)

        data2 = parse_cfg(mid)
        DATA[mid].update(data2)
        
        print "DONE"



def parse_state(mid):
    '''
    since this takes a long time, this step will be cached as well
    '''
    
    print INT,'parsing state  %010s ...' % mid,
    sys.stdout.flush()
    
    cpath = join(stateconf_cache_path, state_fn%mid + '.pickle')
    if os.path.isfile(cpath):
        with open(cpath, 'rb') as f:
            data = pickle.load(f)
            print "DONE, found cached (%s)" % cpath
            return data
    
    path = join(state_path, state_fn % mid)

    state = None

    try:
        state = loadstate(path)
    except IOError:
        print "!! error reading state %s, skipping" % mid + " "*10 + "!!!"
        return
    except NameError:
        print "!! you didn't run this inside a glass env.. read the docu. ABORT"
        sys.exit()     
        

    state.make_ensemble_average()
    obj, data = state.ensemble_average['obj,data'][0]
    
    # keys to save in the pickle
    keys = ['M(<R)', 'kappa(R)', 'R', 'Rlens', 'Sigma(R)']

    # init temp data storage to NaN
    minmax_storage = {}
    for k in keys:
        minmax_storage[k] = np.empty((len(state.models),) + data[k].shape) * np.NaN
    
    M_ens_ave = data['M(<R)'][-1]

    M_min = M_ens_ave
    M_max = M_ens_ave
    for i, gmodel in enumerate(state.models):
        mdata = gmodel['obj,data'][0][1]
        
        M = mdata['M(<R)'][-1]

        for k in keys:
            minmax_storage[k][i] = mdata[k]
        
        if M < M_min: M_min = M 
        if M > M_max: M_max = M
    
    # unwrap glass data type into native types for further processing
#    mltr   = data['M(<R)']
#    kappar = data['kappa(R)']
#    r      = data['R']
#    rlens  = data['Rlens']
#    sigmar = data['Sigma(R)']
    
    # catch bug in glass or maybe problem with model? for example state 007242
    try:
        dt = data['time delays']
    except TypeError:
        dt = None

    ddd = {
        'Mtot_ave_uncorrected': M_ens_ave,
        'Mtot_min_uncorrected': M_min,
        'Mtot_max_uncorrected': M_max,
        
        # simple datatypes
        "H0"          : data['H0'],
        "kappa"       : data['kappa'],
        "time delays" : dt,
        
#        "M(<R)" : {
#            'data':   np.array(mltr),
#            'units':  mltr.units,
#            'symbol': mltr.symbol
#        },
#        "kappa(R)" : {
#            'data':   np.array(kappar),
#            'units':  kappar.units,
#            'symbol': kappar.symbol
#        },
#        "R" : {
#            'data':   np.array(r),
#            'units':  r.units,
#            'symbol': r.symbol
#        },
#        "Rlens" : {
#            'data':   np.array(rlens),
#            'units':  rlens.units,
#            'symbol': rlens.symbol
#        },
#        "Sigma(R)" : {
#            'data':   np.array(sigmar),
#            'units':  sigmar.units,
#            'symbol': sigmar.symbol
#        },
    }
    
    for k in keys:
        ddd[k] = {
            'data':   np.array(data[k]),
            'min' :   np.min(minmax_storage[k], axis=0),
            'max' :   np.max(minmax_storage[k], axis=0),
            'units':  data[k].units,
            'symbol': data[k].symbol
        }
    
    print 'DONE (M_lens=%8.2e [%8.2e ... %8.2e])' % (M_ens_ave, M_min, M_max)

    # cache the result
    with open(cpath, 'wb') as f:
        pickle.dump(ddd, f, -1)

    return ddd





def parse_cfg(mid):
    
    print INT,'parsing config %010s ...' % mid,
    sys.stdout.flush()


    cpath = join(stateconf_cache_path, cfg_fn%mid + '.pickle')
    if os.path.isfile(cpath):
        with open(cpath, 'rb') as f:
            data = pickle.load(f)
            print "DONE, found cached (%s)" % cpath
            return data
    
    #determine the type of config file
    if len(mid)==6:
        tp = 'old'
    elif len(mid)==10:
        tp = 'new'
    else:
        print "ERROR, some problem here, cant estimate the type    !!!"
        sys.exit()

    #print tp,
    sys.stdout.flush()
        
    path = join(cfg_path, cfg_fn % mid)

    with open(path) as f:
        lines = f.readlines()
        
    # init default values
    _ = {
        'gls_ver'    : 1,
        'lmt_ver'    : None,
        'pxscale'    : 0.0,
        'pixrad'     : 0,
        'n_models'   : 0,
        'z_lens_used': 0.0,
        'z_src_used' : 0.0,
        'user'       : '',
        'type'       : tp,
        'created_on' : None,
    }
    
    
    if tp=='old':
        for l in lines:
            if l.startswith("# LMT_GLS_v"):
                _['gls_ver'] = l[11:12]
            if l.startswith("# LMT_v"):
                _['lmt_ver'] = l[7:-1]
            if l.startswith(" 'pxScale'"):
                _['pxscale'] = l.split(':')[1].strip()[:-1]
            if l.startswith('pixrad('):
                _['pixrad'] = l.split('(')[1].split(')')[0]
            if l.startswith('model('):
                _['n_models'] = l.split('(')[1].split(')')[0]
            if l.startswith('zlens('):
                _['z_lens_used'] = l.split('(')[1].split(')')[0]
            if l.startswith('source('):
                _['z_src_used'] = l.split('(')[1].split(',')[0]
            if l.startswith('meta(author='):
                _['user'] = l.split("'")[1]
#        created_on = oldtabledate[mid][:19]
                
    else:
        try:
            jcfg = json.loads(''.join(lines))
        except:
            "      !! error could not load json file", mid
            return ['',]*6
        
        _['gls_ver']     = '5'
        _['lmt_ver']     = '2.0.0'
        _['pxscale']     = jcfg['obj']['pxScale']
        _['pixrad']      = jcfg['obj']['pixrad']
        _['n_models']    = jcfg['obj']['n_models']
        _['z_lens_used'] = jcfg['obj']['z_lens']
        _['z_src_used']  = jcfg['obj']['z_src']
        _['user']        = jcfg['obj']['author']
        ddd = jcfg['created_at']
        _['created_on'] = ddd[:10]+' '+ddd[11:-1]
        
    # convert to proper datatype MAKE SURE all are listed here!
    StrOrNone = (lambda x: str(x) if x else x)
    cast = {
        'gls_ver'     : int,
        'lmt_ver'     : StrOrNone,
        'pxscale'     : float,
        'user'        : (lambda x: unicode(x).strip()),
        'pixrad'      : int,
        'n_models'    : int,
        'z_src_used'  : float,
        'z_lens_used' : float,
        'created_on'  : StrOrNone,
        'type'        : str,
    }
    
    dat = {}
    
    #print "(",
    for k,v in _.items():
        try:
            dd = cast[k](v)
        except KeyError:
            print "ERROR with casting..", k, v, cast[k]
            sys.exit(1)
        dat[k] = dd
        #print '%s:%s; ' % (k,dd),

    #print ")",
        
    # cache the result
    with open(cpath, 'wb') as f:
        pickle.dump(dat, f, -1)
    
    print "DONE (pixrad:%i; z=%.1f/%.1f; user:%s)" % (
        dat['pixrad'], dat['z_lens_used'], dat['z_src_used'], dat['user'])

    return dat
    


### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)

pickle_fn = join(S['cache_dir'], 'data_from_state_and_config_files.pickle')
csv_fn    = join(S['temp_dir'],  'data_from_state_and_config_files.csv')


if len(sys.argv)>1:

    if '-d' in sys.argv: del_cache(I,pickle_fn)

    if '-D' in sys.argv:
        print I,"deleting cache and quitting (really everything)"
        
        if os.path.isfile(pickle_fn):
            os.remove(pickle_fn)
        if os.path.exists(stateconf_cache_path):
            shutil.rmtree(stateconf_cache_path)
        if not os.path.exists(stateconf_cache_path):
            os.makedirs(stateconf_cache_path) #restore path again
        
    print I,"DONE"
    sys.exit()
        

if os.path.isfile(pickle_fn):
    DATA = load_pickle(I, pickle_fn)
else:
    parse_mainloop()
    save_pickle(I, pickle_fn, DATA)

save_csv(I, csv_fn, DATA, 'mid')
    
print_last_line(I,DATA)






