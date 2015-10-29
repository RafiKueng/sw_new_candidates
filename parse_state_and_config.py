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



import sys, os
import csv
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
       
#        asw = all_models[mid]['asw']
#        try:
#            z_lens_actual = candidates.by['asw'][asw]['z_lens']
#        except KeyError:
#            z_lens_actual = 0.0
#        all_models[mid]['z_lens_actual'] = z_lens_actual



def parse_state(mid):
    '''
    since this takes a long time, this step will be cached as well
    '''
    
    print INT,'parsing state %010s ...' % mid,
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
        'Mtot_ens_ave': M_ens_ave,
        'Mtot_min': M_min,
        'Mtot_max': M_max,
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
        
    
    _ = {
        'gls_ver': 1,
        'lmt_ver': '',
        'pxscale': 0.0,
        'pixrad': 0,
        'n_models': 0,
        'z_lens_used': 0.0,
        'z_src_used': 0.0,
        'user': '',
        'type': tp,
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
    cast = {
        'gls_ver'     : int,
        'lmt_ver'     : str,
        'pxscale'     : float,
        'user'        : (lambda x: unicode(x).strip()),
        'pixrad'      : int,
        'n_models'    : int,
        'z_src_used'  : float,
        'z_lens_used' : float,
        'created_on'  : str,
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
    








parse_mainloop()






#
#
#
#
#
#
#
#
#import numpy as np
#import os
#import json
#import cPickle as pickle
#
#import settings as S
#
#from get_state_and_config import state_path, state_fn, cfg_path, cfg_fn
#import get_all_models
#import candidates
#
#
#csv_name = 'all_data.csv'
#pickle_name = 'all_data.pickle'
#
##all_models = []
##def load_all_models():
##    
##    with open('tmp3_all_models_with_state_id_cfg.csv') as f:
##        for line in f.readlines():
##            all_models.append(line[:-1].split(','))
#
#    
#def parse_state(mid):
#    
#    print '   parsing state', mid
#    
#    if all_models[mid].has_key('Mtot_ens_ave'):
#        print '      skipping, data already present'
#        return
#        
#    path = os.path.join(state_path, state_fn % mid)
#
#    state = None    
#    try:
#        state = loadstate(path)
#    except IOError:
#        print "!! error reading state %s, skipping" % mid
#        
#    if state:
#        state.make_ensemble_average()
#        obj, data = state.ensemble_average['obj,data'][0]
#        
#        M_ens_ave = data['M(<R)'][-1]
#
#        M_min = M_ens_ave
#        M_max = M_ens_ave
#        for gmodel in state.models:
#            M = gmodel['obj,data'][0][1]['M(<R)'][-1]
#            
#            if M < M_min: M_min = M 
#            if M > M_max: M_max = M
#
#    else:
#        M_ens_ave = 0.0
#        M_min = 0.0
#        M_max = 0.0
#
#    
#    all_models[mid]['Mtot_ens_ave'] = M_ens_ave
#    all_models[mid]['Mtot_min'] = M_min
#    all_models[mid]['Mtot_max'] = M_max
#    
#    print '      %9.2e (%9.2e ... %9.2e)' % (M_ens_ave, M_min, M_max)
#    
#
## quick hack incomming...
#oldtabledate = {}
#def loadoldtable():
#    global oldtabledate
#    with open('output/all_results.csv') as f:
#        lines = f.readlines()
#    lines = lines[1:]
#    for line in lines:
#        tkns = line.split(',')
#        oldtabledate[int(tkns[0])] = tkns[5]
#    
#
#def parse_cfg(mid):
#    
#    print '   parsing cfg', mid
#
#    tp = all_models[mid]['type']
#    path = os.path.join(cfg_path, cfg_fn % mid)
#
#    with open(path) as f:
#        lines = f.readlines()
#        
#    glsv = 1
#    lmtv = ''
#    pxscale = 0.0
#    pixrad = 0
#    nmodel = 0
#    zlens = 0.0
#    zsrc = 0.0
#    user = ''
#    
#    if tp=='old':
#        for l in lines:
#            if l.startswith("# LMT_GLS_v"):
#                glsv = l[11:12]
#            if l.startswith("# LMT_v"):
#                lmtv = l[7:-1]
#            if l.startswith(" 'pxScale'"):
#                pxscale = l.split(':')[1].strip()[:-1]
#            if l.startswith('pixrad('):
#                pixrad = l.split('(')[1].split(')')[0]
#            if l.startswith('model('):
#                nmodel = l.split('(')[1].split(')')[0]
#            if l.startswith('zlens('):
#                zlens = l.split('(')[1].split(')')[0]
#            if l.startswith('source('):
#                zsrc = l.split('(')[1].split(',')[0]
#            if l.startswith('meta(author='):
#                user = l.split("'")[1]
#        created_on = oldtabledate[mid][:19]
#                
#    else:
#        try:
#            jcfg = json.loads(''.join(lines))
#        except:
#            "      !! error could not load json file", mid
#            return ['',]*6
#        
#        glsv = '5'
#        lmtv = '2.0.0'
#        pxscale = jcfg['obj']['pxScale']
#        pixrad = jcfg['obj']['pixrad']
#        nmodel = jcfg['obj']['n_models']
#        zlens = jcfg['obj']['z_lens']
#        zsrc = jcfg['obj']['z_src']
#        user = jcfg['obj']['author']
#        ddd = jcfg['created_at']
#        created_on = ddd[:10]+' '+ddd[11:-1]
#        
#    print '      ', glsv, lmtv, pxscale, pixrad, nmodel, zlens, zsrc, user, created_on
#            
#    #return (glsv, lmtv, pxscale, pixrad, nmodel, zlens, zsrc)
#    
#    data = {
#        'gls_ver'     : int(     glsv    ),
#        'lmt_ver'     : str(     lmtv    ),
#        'pixscale'    : float(   pxscale ),
#        'user'        : unicode( user    ).strip(),
#        'pixrad'      : int(     pixrad  ),
#        'n_models'    : int(     nmodel  ),
#        'z_src_used'  : float(   zsrc    ),
#        'z_lens_used' : float(   zlens   ),
#        'created_on'  : str(     created_on)
#    }
#    
#    for k,v in data.items():
#        if k in all_models[mid].keys() and not all_models[mid].get(k) == v:
#            print "      !!overwriting value!! key: %16s  old: %s %s with %s %s" % tuple([
#                str(_) for _ in (k, all_models[mid].get(k), type(all_models[mid].get(k)), v, type(v))
#            ])
#        all_models[mid][k] = v
#
#
#      
#
#scale_fact = 440./500*0.187
#
#def correct_scaling(mid):
#    
#    f = ( (scale_fact*100)**2 )
#
#    # version 3 and higher have correct scaling already applied
#    if all_models[mid]['gls_ver'] < 3 and all_models[mid]['gls_ver'] >= 0:
#        print '   correcting scaling with f=%5.2f' % f
#        
#        all_models[mid]['Mtot_ens_ave'] *= f
#        all_models[mid]['Mtot_min'] *= f
#        all_models[mid]['Mtot_max'] *= f
#        
#        # make it negative to indicate that this has already been fixed in a previous run
#        # this is a problem in case of reruns in the same session
#        all_models[mid]['gls_ver'] *= -1 
#        
#
#
#from stelmass.angdiam import sig_factor
#
#def correct_mass(mid):
#
#    print '   correcting mass for differen redshifts'
#    
#    model = all_models[mid]
#    
#    zl_actual = model['z_lens_actual']
#    zs_actual = 2.0                 #!!!!!!!!! source redshifts not yet available, using estimate
#    zl_used = model['z_lens_used']
#    zs_used = model['z_src_used']
#    
#    # we trust claude.. he looks up stuff, if we don't have any data, and if he didn't used default values
#    if zl_actual == 0.0 and model['user']=='c_cld' and not zl_used == 0.5 and not zs_used == 1.0:
#        print '!!!   trusting claudes values ',
#        print "( zl_act: %4.2f  zl_use: %4.2f  zs_act: %4.2f  zs_use: %4.2f )" % (zl_actual,zl_used,zs_actual,zs_used)
#        zl_actual = zl_used
#        zs_actual = zs_used
#        
#    f_act = sig_factor(zl_actual,zs_actual)
#    f_use = sig_factor(zl_used,zs_used)
#    
#    print "      zl_act: %4.2f  zl_use: %4.2f  zs_act: %4.2f  zs_use: %4.2f  f1: %e  f2: %e" % (
#        zl_actual,zl_used,zs_actual,zs_used,
#        f_act, f_use
#    )
#
#    keys = ['Mtot_ens_ave', 'Mtot_min', 'Mtot_max']
#    
#    for k in keys:
#        if zl_actual * zs_actual * zl_used * zs_used > 0:
#            org_mass = model[k]
#            corr_mass = org_mass * f_act / f_use
#            model[k+'_z_corrected'] = corr_mass
#            print '      m: %e -> %e' % (model[k], model[k+'_z_corrected'])
#        else:
#            model[k+'_z_corrected'] = 0.0
#            print '      no data available'
#
#
#
#
#def parse_stuff():
#    print "parse_state_and_config: parse stuff"
#
#    for i, mid in enumerate(all_models.keys()):
#    
#        print "%5.1f%% working on %s (%i)..." % (100.0/len(all_models.keys())*i, mid, i)
#        
#        parse_state(mid)        
#        parse_cfg(mid)
#       
#        asw = all_models[mid]['asw']
#        try:
#            z_lens_actual = candidates.by['asw'][asw]['z_lens']
#        except KeyError:
#            z_lens_actual = 0.0
#        all_models[mid]['z_lens_actual'] = z_lens_actual
#
#        
#def correct_stuff():
#    
#    for i, mid in enumerate(all_models.keys()):
#        print "%5.1f%% correcting on %s (%i) [%s by %s]..." % (100.0/len(all_models.keys())*i, mid, i, all_models[mid]['asw'], all_models[mid]['user'])
#        correct_scaling(mid)
#        correct_mass(mid)
#        
#
#
#def save_csv():
#    print "parse_state_and_config: save_csv"
#    
#    keys = {}
#    for mid, m in all_models.items():
#        for k in m.keys():
#            keys[k] = ''
#    keys = keys.keys()
#    
#    with open(csv_name, 'w') as f:
#        f.write(','.join(keys)+'\n') # write header
#        
#        for mid, data in all_models.items():
#            for k in keys:
#                f.write('%s,' % str(data.get(k,'')))
#            f.write('\n')
#  
#
#def save_pickle():
#    print "parse_state_and_config: save_pickle"
#    
#    with open(pickle_name, 'wb') as f:
#        pickle.dump(all_models, f, -1)
#
#
# 
#    
#
#all_models = {}
#
#def main():
#    print "parse_state_and_config: running main"
#    
#    loadoldtable()
#    parse_stuff()
#    correct_stuff()
#    save_csv()
#    save_pickle()
#    
#
#if __name__ == "__main__":
#    all_models = get_all_models.data
#    main()
#else:
#    if os.path.isfile(pickle_name):
#        print "parse_state_and_config: loaded all data from pickle"
#        with open(pickle_name, 'rb') as f:
#            all_models = pickle.load(f)
#    else:
#        all_models = get_all_models.data
#        main()
#
#
#
