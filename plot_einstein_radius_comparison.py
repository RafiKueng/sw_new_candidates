#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 03:39:18 2016

@author: rafik
"""

import os
from os.path import join
import glob
import pickle

# reminder: settings before mpl
import settings as SET
reload(SET)
SET.set_mpl_rc()
STY = SET.styles # for better reload() in ipython
S = SET.settings
# from settings import getI, INT


import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

import scipy.interpolate as interp
import scipy.optimize as optimize
from scipy import optimize, interpolate

import create_data as CRDA


DBG = SET.DEBUG

fpath     = join(S['output_dir'], 'rE_comp')
filename = "rE_comp." + SET.imgext
fnn = join(fpath, filename)

# txt data of simulations
params_file = join(S['input_dir'], 'parameters.csv')


if not os.path.exists(fpath):
    os.makedirs(fpath)


def getEinsteinR(x, y):
    poly = interpolate.PiecewisePolynomial(x,y[:,np.newaxis])
    
    def one(x):
        return poly(x)-1
    
    x_min = np.min(x)
    x_max = np.max(x)
    x_mid = poly(x[len(x)/2])
    
    rE,infodict,ier,mesg = optimize.fsolve(one, x_mid, full_output=True)
    
    #print rE,infodict,ier,mesg
    
    if (ier==1 or ier==5) and x_min<rE<x_max and len(rE)==1:
        return rE[0]
    elif len(rE)>1:
        for r in rE:
            if x_min<r<x_max:
                return r
    else:
        return False
    



with open(params_file) as f:
    lines = f.readlines()
    
PARAMS = {}
for line in lines:
    d = [_.strip() for _ in line.split(";")]
    if len(d)==5 and d[0][:3]=="ASW":
        PARAMS[d[0]] = float(d[2])
    print d


PNTS = {'x':[],'y':[]}

for swid, asw in sorted(CRDA.MAPS['swid2asw'].items()):
    
    print swid, asw
    
    mid = CRDA.MAPS['swid2model'].get(swid, "")
    
    if not mid:
        print "   no mid, skipping"
        continue


    m = CRDA.ALL_MODELS[mid]
    
    # load correcting factors
    # ScaleCorrectionFactors
    px_scf = m['pixel_scale_fact'] # corrects wrong pixel scaling in old version [old_pxl -> arcsec]
    aa_scf = m['area_scale_fact']  # corrects areas due to wrong pixel scaling in old version [old_pxl**2 -> arcsec**2]
    # RedshiftCorrectionFactor
    r_rcf  = m['dis_fact']          # corrects lengths for wrong redshifts
    m_rcf  = m['sig_fact']          # corrects masses for wrong redshifts
    k_rcf  = m['kappa_fact']        # corrects kappa for wrong redshifts

    rr = m['R']['data'] * px_scf * r_rcf
    da = m['kappa(<R)']['data'] * k_rcf
    
    rE = getEinsteinR(rr, da)
    
    if asw in PARAMS.keys():
        PNTS['x'].append(rE)
        PNTS['y'].append(PARAMS[asw])


x = np.array(PNTS['x'])
y = np.array(PNTS['y'])

fig = plt.figure(**STY['figure_sq'])
ax = fig.add_subplot(1,1,1)

kw = dict(STY['fg_marker1'])
#kw.pop('markeredgecolor', None)
#kw.pop('markeredgewidth', None)
#kw.pop('markersize', None)
kw.pop('facecolor', None)
kw['linestyle'] = 'none'
ax.plot(x, y, **kw)

mi = min([np.min(x),np.min(y)])
mx = max([np.max(x),np.max(y)])

ax.plot([mi, mx], [mi, mx] , **STY['bg_line'])

ax.set_xlabel('r_E model', **STY['label'])
ax.set_ylabel('r_E parametr', **STY['label'])

plt.tight_layout()
fig.savefig(fnn, **STY['figure_save'])

plt.show()

    
    