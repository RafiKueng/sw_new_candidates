# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 16:39:16 2016

@author: rafik
"""

from create_data import ONLY_RECENT_MODELS as ormods, LENS_CANDIDATES as LENSES, ALL_MODELS as amods
import parse_candidates as PACA


i=0
d = {}

for i in range(1,60):
    d[i] = {'c':0,'m':[]}

for mid, model in amods.items():
    asw = model['asw']
    if asw in PACA.MAP.keys():
        swid = PACA.MAP[asw]
        swid_int = int(swid[2:])
        if model['Mtot_ave_z_corrected']:
            m = model['Mtot_ave_z_corrected']
        elif model['Mtot_ave_scaled']:        
            m = model['Mtot_ave_scaled']
        else:
            m = model['Mtot_ave_uncorrected']
        if swid_int in d:
            d[swid_int]['c'] += 1
            d[swid_int]['m'].append(m)
#        else:
#            d[swid_int] = {'c':1,'m':[m,]}
        print mid, asw, PACA.MAP[asw], i, m
        
from math import log10
for i in range(1,60):
    d[i]['swid'] = '\SW{%02i}'%i
    # get average
    if d[i]['c'] >0:
        d[i]['m_ave'] = sum(d[i]['m']) / d[i]['c']
        d[i]['exp'] = int(log10(d[i]['m_ave']))
        d[i]['base'] = d[i]['m_ave'] / 10**d[i]['exp']
    else:
        d[i]['m_ave'] = 0
        d[i]['exp'] = 0
        d[i]['base'] = 0
        

    # get add data from paper
    asw = PACA.MAP['SW%02i'%i]
    dd = PACA.DATA[asw]
    d[i]['z_lens'] = dd['z_lens']
    

j = 30
ss = "{swid} & {c} & ${base:.2f} \\times 10^{{{exp}}}$"
st = "  &  "
for i in range(1,31):
    print ss.format(**d[i]),
    print st ,
    if i+j in d:
        print ss.format(**d[i+j]) , " \\\\"
    else:
        print " & & \\\\"
    
