# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 10:22:51 2016

@author: rafik
"""

#import pyperclip
import numpy as np

import create_data as CRDA
from create_data import LENS_CANDIDATES as LENSES
import parse_candidates as PACA

MODELS, MAPS = CRDA.get_dataset_data("selected_models")
ALL_MODELS = CRDA.ALL_MODELS

import moster

UK = '-'

with open('input/eval.txt', 'r') as f:
    lns = f.readlines()

dd = {}    
for l in lns:
    if l.startswith('SW'):
        _ = l[:-1].split(',') # remove \n
        swid = _[0].strip(' *+')
        d = [x.strip(' *+') for x in _[1:]] # remove review marker and white space used for formating
        for i, j in enumerate(d):
            if j.startswith('y'):
                d[i] = 'Y'
            elif j.startswith("n"):
                d[i] = 'N'
            elif j.startswith("-") or j == "":
                d[i] = UK  # unknown
               
        if len(d)>=6:
            dd[swid] = d
        else:
            print "%s: no complete record found" % (swid,)
            dd[swid] = [UK]*6

ss = ",".join([
'SWID,ZooID,CFHTLS Name',
'z_lens',
'unblended images',
'all images discernible',
'isolated lens',

'image morphology',

'synthetic image reasonable',
'mass map reasonable',

'log_10 ( Mstel / Msun )',
'log_10 ( Mlens / Msun )',

'halo-matching index H',
])

for swid, asw in sorted(MAPS['swid2asw'].items()):
    
    mids = MAPS['swid2mids'].get(swid, None)

    if mids and len(mids)==1:
        mid = mids[0]
    else:
        mid = None
    
    aswobj = PACA.DATA[asw]
    #CRDA.ALL_MODELS[mid]
    
    
    name = aswobj['name'].split(' ')[1]
    #name = "$-$".join(name.split('-'))
    #name = "$+$".join(name.split('+'))

    zL = UK
    m_ratio = None
    haloindex = None
    
    if mid and 'm_s_geom' in LENSES[asw].keys():
        m_stel = LENSES[asw].get('m_s_geom', None)
        m_lens = MODELS[mid]['M(<R)']['data'][-1] # usually called m_lens in the pipeline
        m_moster = moster.inv(m_stel)
        
        m_rcf = MODELS[mid]['sig_fact']
        m_lens = m_lens * m_rcf
        
        zL = "%s" % MODELS[mid]['z_lens_measured']
        
        if m_stel is not None:
            
            haloindex = np.log(m_lens / m_stel) / np.log(m_moster / m_stel)
            
            r = m_lens / m_stel
            if r<99.:
                m_ratio = '%i'%r
            else:
                m_ratio = '%.1e'%r
                
    
    try:
        haloindex = "%6.4f" % haloindex
        log_m_stel = "%6.4f" % np.log10(m_stel)  # / msun they are already in solar masses
        log_m_lens = "%6.4f" % np.log10(m_lens)  # dito
    except:
        haloindex = UK
        log_m_stel = UK
        log_m_lens = UK
    
    m = {
        'asw'      : asw,
        'swid'     : swid,
        #'mid':    mid,
        'coords'   : name,
        'm_stel'   : log_m_stel,
        'm_halo'   : log_m_lens,
        'm_ratio'  : m_ratio,
        'haloindex': haloindex,
        'zL' : zL,
        'd0' : dd[swid][0],
        'd1' : dd[swid][1],
        'd2' : dd[swid][2],
        'd3' : dd[swid][3],
        'd4' : dd[swid][4],
        'd5' : dd[swid][5],
    }
    
    s = """{swid}, {asw}, {coords}, {zL},
{d1}, {d2}, {d3}, {d0}, {d4}, {d5},
{m_stel}, {m_halo}, {haloindex}\n    
""".format(**m)

    print s
    ss += s

#pyperclip.copy(ss)

with open("output/table.csv", "w") as f:
    f.write(ss)

