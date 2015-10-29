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



import sys, os, shutil
import glob
import json

import cPickle as pickle

from os.path import join


from settings import settings as S
from settings import state_path, state_fn, cfg_path, cfg_fn, stateconf_cache_path

NAME = os.path.basename(__file__)
I = NAME + ":"
INT = '       '


pickle_fn = join(S['cache_dir'], 'parsed_state_and_config_files.pickle')
csv_fn    = join(S['temp_dir'],  'parsed_state_and_config_files.csv')



stateconf_data = {}


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
    
    print "status:"
    print " - config files:", len(cfgmids)
    print " - state  files:", len(statemids)
    print " - both   files:", n_mids
    print "-------"
    print "we are missing:"
    for mid in sorted(list(cfgmids ^ statemids)): # symmetric_difference https://docs.python.org/2/library/sets.html
        print " *", mid
    print "-------\n"
    
    
    for i, mid in enumerate(sorted(all_mids)):
    
        print "%5.1f%% (% 3i/% 3i) working on %10s ..." % (100.0/n_mids*i, i, n_mids, mid)
        
        stateconf_data[mid] = {}
        
        data1 = parse_state(mid)
        stateconf_data[mid].update(data1)

        data2 = parse_cfg(mid)
        stateconf_data[mid].update(data2)
       



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
    
    M_ens_ave = data['M(<R)'][-1]

    M_min = M_ens_ave
    M_max = M_ens_ave
    for gmodel in state.models:
        M = gmodel['obj,data'][0][1]['M(<R)'][-1]
        
        if M < M_min: M_min = M 
        if M > M_max: M_max = M

    data = {
        'Mtot_ave_uncorrected': M_ens_ave,
        'Mtot_min_uncorrected': M_min,
        'Mtot_max_uncorrected': M_max,
    }
    
    print 'DONE -> %8.2e (%8.2e ... %8.2e)' % (M_ens_ave, M_min, M_max)

    # cache the result
    with open(cpath, 'wb') as f:
        pickle.dump(data, f, -1)

    return data





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

    print tp,
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
    
    data = {}
    
    print "(",
    for k,v in _.items():
        try:
            dd = cast[k](v)
        except KeyError:
            print "ERROR with casting..", k, v, cast[k]
            sys.exit(1)
        data[k] = dd
        print '%s:%s; ' % (k,dd),

    print ")",
        
    # cache the result
    with open(cpath, 'wb') as f:
        pickle.dump(data, f, -1)
    
    print "DONE"

    return data
    




def save_pickle():
    print I, 'save data to cache (pickle)'
    with open(pickle_fn, 'wb') as f:
        pickle.dump(stateconf_data, f, -1)
        
def load_pickle():
    print I, 'load cached data from pickle'
    with open(pickle_fn, 'rb') as f:
        return pickle.load(f)

def save_csv():
    print I, 'save_csv'

    with open(csv_fn, 'w') as f:
        f.write('mid,' + ','.join(stateconf_data.values()[0].keys())+'\n')
        for mid, v in stateconf_data.items():
            f.write(mid + ',' + ','.join([str(_) for _ in v.values()])+'\n')

### MAIN #####################################################################

print I, "START\n"

if len(sys.argv)>1:

    if '-d' in sys.argv:
        print I,"deleting cache and quitting (leaves the small pickles from models in place)"
        try:
            os.remove(pickle_fn)
        except OSError:
            pass

    if '-D' in sys.argv:
        print I,"deleting cache and quitting (really everything)"
        
        if os.path.isfile(pickle_fn):
            os.remove(pickle_fn)
        if os.path.exists(stateconf_cache_path):
            shutil.rmtree(stateconf_cache_path)
        if not os.path.exists(stateconf_cache_path):
            os.makedirs(stateconf_cache_path) #restore path again
        
    sys.exit()
        

if os.path.isfile(pickle_fn):
    stateconf_data = load_pickle()
    save_csv()
    
else:
    parse_mainloop()
    save_pickle()
    save_csv()







