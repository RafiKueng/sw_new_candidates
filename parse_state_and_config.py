# -*- coding: utf-8 -*-
"""
execute this file in an interactive glass ipython shell

cd .
../glass/interactive_glass

%run <this_file.py>



Created on Mon Jun  8 03:47:50 2015

@author: rafik
"""

import numpy as np
import os
import json

from get_state_and_config import state_path, state_fn, cfg_path, cfg_fn


all_models = []
def load_all_models():
    
    with open('tmp3_all_models_with_state_id_cfg.csv') as f:
        for line in f.readlines():
            all_models.append(line[:-1].split(','))

    
def parse_state(mid):
    
    path = os.path.join(state_path, state_fn % mid)
    
    try:
        state = loadstate(path)
    except IOError:
        print "!! error reading state %s, skipping" % mid
        return 0
    state.make_ensemble_average()
    obj, data = state.ensemble_average['obj,data'][0]
    mLtR = data['M(<R)'][-1]
    
    return mLtR
    
    
def parse_cfg(mid, tp):

    path = os.path.join(cfg_path, cfg_fn % mid)

    with open(path) as f:
        lines = f.readlines()
        
    glsv = ''
    lmtv = ''
    pxscale = ''
    pixrad = ''
    nmodel = ''
    zlens = ''
    zsrc = ''
    user = ''
    
    if tp=='old':
        for l in lines:
            if l.startswith("# LMT_GLS_v"):
                glsv = str(l[11:12])
            if l.startswith("# LMT_v"):
                lmtv = str(l[7:-1])
            if l.startswith(" 'pxScale'"):
                pxscale = float(l.split(':')[1].strip()[:-1])
            if l.startswith('pixrad('):
                pixrad = int(l.split('(')[1].split(')')[0])
            if l.startswith('model('):
                nmodel = int(l.split('(')[1].split(')')[0])
            if l.startswith('zlens('):
                zlens = float(l.split('(')[1].split(')')[0])
            if l.startswith('source('):
                zsrc = float(l.split('(')[1].split(',')[0])
            if l.startswith('meta(author='):
                user = str(l.split("'")[1])
                
    else:
        try:
            jcfg = json.loads(''.join(lines))
        except:
            "!! error could not load json file", mid
            return ['',]*6
        
        glsv = '5'
        lmtv = '2.0.0'
        pxscale = float(jcfg['obj']['pxScale'])
        pixrad = int(jcfg['obj']['pixrad'])
        nmodel = int(jcfg['obj']['n_models'])
        zlens = float(jcfg['obj']['z_lens'])
        zsrc = float(jcfg['obj']['z_src'])
        user = str(jcfg['obj']['author'])
        
            
    #return (glsv, lmtv, pxscale, pixrad, nmodel, zlens, zsrc)
    
    return {
        'glsv'    : glsv,
        'lmtv'    : lmtv,
        'pxscale' : pxscale,
        'user'    : user,
        'pixrad'  : pixrad,
        'nmodel'  : nmodel,
        'zsrc'    : zsrc,
        'zlens'   : zlens
    }



paper_table = {}
def read_paper_table():
    with open('candidates.csv') as f:
        lns = f.readlines()
    for line in lns:
        tkn = line.strip().split('\t')

        pid = "SW%02i" % int(tkn[0][2:])
        asw = tkn[8]
        
        d = {
            'z_lens': float(tkn[4]),
            'z_src' : float(tkn[7])
        }
        
        paper_table[pid] = d
        paper_table[asw] = d

       

scale_fact = 440./500*0.187

def correct_scaling(i):
    
    try:
        v = int(all_models[i][10])
    except ValueError:
        v = 0
    if v<3:
        all_models[i][9] = all_models[i][9] * ( (scale_fact*100)**2 )
        

from stelmass.angdiam import sig_factor

def correct_mass(i):
    
    zl_actual = all_models[i][13]
    zs_actual = 2.0                 #!!!!!!!!! source redshifts not yet available, using estimate
    zl_used = all_models[i][7]
    zs_used = all_models[i][8]
    
    org_mass = all_models[i][9]

    print "        ",
    print zl_actual,zs_actual,zl_used,zs_used,org_mass,
    print sig_factor(zl_actual,zs_actual),
    print sig_factor(zl_used,zs_used),
    
    if zl_actual*zs_actual*zl_used*zs_used*org_mass >0:
        corr_mass = org_mass * sig_factor(zl_actual,zs_actual)/sig_factor(zl_used,zs_used)
    else:
        corr_mass = 0
    print corr_mass
    
    all_models[i].append(corr_mass)
    



def print_data():
    head = ['mid', 'type', 'asw', 'paperid', 'user', 'pixrad', 'nmodels',
            'z_lens_used','z_src_used','m<R','glsv','lmtv','pxscale','z_lens_real', 'z_src_real',
            'corrected_mass']

    with open('all_candidates_data.csv', 'w') as f:
        f.write(','.join(head)+'\n')
        for m in all_models:
            f.write(','.join([str(_) for _ in m])+'\n')
        





def parse_stuff():
    for i, model in enumerate(all_models):
    
        mid = model[0]
        tp = model[1]
        print "%5.1f%% working on %s (%i)..." % (100.0/len(all_models)*i, mid, i)
        
        mLtR = parse_state(mid)
        all_models[i].append(mLtR)
        
        cfg = parse_cfg(mid, tp)
        #print cfg
        
        all_models[i].extend([cfg['glsv'], cfg['lmtv'], cfg['pxscale']])
        
        a2b = {
            4 : 'user',
            5 : 'pixrad',
            6 : 'nmodel',
            7 : 'zlens',
            8 : 'zsrc',
        }
        
        for k, v in a2b.items():
            if len(str(model[k]))>0 and not model[k] == str(cfg[v]):
                print '     different vals', model, k, v, model[k], cfg[v]
            all_models[i][k] = cfg[v]
        
        d = paper_table[all_models[i][3]]
        all_models[i].extend([d['z_lens'], d['z_src']])
        
def correct_stuff():
    for i, model in enumerate(all_models):
        mid = model[0]
        tp = model[1]
        print "%5.1f%% correcting on %s (%i)..." % (100.0/len(all_models)*i, mid, i)
        correct_scaling(i)
        correct_mass(i)
        
    
load_all_models()
read_paper_table()
parse_stuff()
correct_stuff()
print_data()    
    






