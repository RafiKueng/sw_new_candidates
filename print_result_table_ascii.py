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
from EinsteinRadius import getEinsteinR
from stelmass.angdiam import sig_factor, kappa_factor

UK = ''

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

'log_10 ( Mstel / Msun ) [1]',
'log_10 ( Mlens / Msun ) [1]',

'halo-matching index H [1]',

'Mstel [Msun]','Mlens [Msun]','Mmoster [Msun]',
'Mstel_yr [Msun]','Mstel_sr [Msun]',
'Mlens_min [Msun]','Mlens_max [Msun]',

'EinsteinRadius [arcsec]'
]) + "\n"
    
print ss

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

    m_stel = UK
    m_stel_jr = UK
    m_stel_sr = UK

    m_lens = UK
    m_lens_min = UK
    m_lens_max = UK

    m_moster = UK
    rE = UK
    
    if mid:
        M = MODELS[mid]

        if M['z_corrected']:
            m_rcf = M['sig_fact']
            k_rcf  = M['kappa_fact']
        else:   # you could enable this to set the redshifts of uncorrected models to 0.5/2
            zl_actual = 0.5
            zs_actual = 2
            zl_used   = 0.5
            zs_used   = 2
            m_rcf = sig_factor(zl_actual,zs_actual) / sig_factor(zl_used,zs_used)
            k_rcf  = kappa_factor(zl_used, zs_used)
#            k_rcf  = kappa_factor(0.5,2)

        m_lens = M['M(<R)']['data'][-1] * m_rcf # usually called m_lens in the pipeline
        m_lens_max = M['M(<R)']['max'][-1] * m_rcf
        m_lens_min = M['M(<R)']['min'][-1] * m_rcf
        
        rr = M['R']['data']
        da = M['kappa(<R)']['data'] * k_rcf
        rE = getEinsteinR(rr, da)
        
        if not M['z_corrected']:
            # if these values are not corrected they are not useable...
            # remove this if if you want to approx with redshifts 0.5/2, as defined above
            m_lens = UK
            m_lens_max = UK
            m_lens_min = UK
            rE = UK


    if mid and 'm_s_geom' in LENSES[asw].keys():
        m_stel = LENSES[asw].get('m_s_geom', None)
        m_stel_jr = LENSES[asw].get('m_s_jr', UK)
        m_stel_sr = LENSES[asw].get('m_s_sr', UK)

        m_moster = moster.inv(m_stel)
        
        zL = "%s" % MODELS[mid]['z_lens_measured']
        
        if m_stel is not None:
            
            haloindex = np.log(m_lens / m_stel) / np.log(m_moster / m_stel)
            
            r = m_lens / m_stel
            if r<99.:
                m_ratio = '%i'%r
            else:
                m_ratio = '%.1e'%r
                
    fmt = "%6.4e"

    try:
        log_m_lens = fmt % np.log10(m_lens)  # dito
    except:
        log_m_lens = UK
        
    try:
        haloindex = "%5.3f" % haloindex
        log_m_stel = fmt % np.log10(m_stel)  # / msun they are already in solar masses
    except:
        haloindex  = UK
        log_m_stel = UK

    try:
        m_stel     = fmt % m_stel
        m_stel_jr  = fmt % m_stel_jr
        m_stel_sr  = fmt % m_stel_sr
    except:
        m_stel     = UK
        m_stel_jr  = UK
        m_stel_sr  = UK
        
    try:
        m_lens     = fmt % m_lens
        m_lens_min = fmt % m_lens_min
        m_lens_max = fmt % m_lens_max
    except:
        m_lens     = UK
        m_lens_min = UK
        m_lens_max = UK

    try:
        m_moster   = fmt % m_moster
    except:
        m_moster = UK

    try:
        rE   = "%4.2f" % rE
    except:
        rE = UK
    
    m = {
        'asw'      : asw,
        'swid'     : swid,
        #'mid':    mid,
        'coords'   : name,
        'log_m_stel'   : log_m_stel,
        'log_m_lens'   : log_m_lens,
        'm_ratio'  : m_ratio,
        'haloindex': haloindex,
        'zL' : zL,
        'd0' : dd[swid][0],
        'd1' : dd[swid][1],
        'd2' : dd[swid][2],
        'd3' : dd[swid][3],
        'd4' : dd[swid][4],
        'd5' : dd[swid][5],
        'm_stel'    : m_stel, 
        'm_stel_jr' : m_stel_jr,
        'm_stel_sr' : m_stel_sr,
        'm_lens'    : m_lens,
        'm_lens_min': m_lens_min,
        'm_lens_max': m_lens_max,
        'm_moster'  : m_moster,
        'rE'        : rE
    }
    
    s = """
{swid},{asw},{coords},{zL},
{d1},{d2},{d3},{d0},{d4},{d5},
{log_m_stel},{log_m_lens},{haloindex},
{m_stel},{m_lens},{m_moster},
{m_stel_jr},{m_stel_sr},{m_lens_min},{m_lens_max},
{rE}
""".format(**m).replace('\n', '') 

    print s
    ss += s + "\n"

#pyperclip.copy(ss)

with open("output/table_1.csv", "w") as f:
    f.write(ss)

