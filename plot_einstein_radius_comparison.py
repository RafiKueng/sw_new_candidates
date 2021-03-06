#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 03:39:18 2016

@author: rafik
"""

import os
from os.path import join

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
#import matplotlib.transforms as transforms

import scipy.interpolate as interpolate
import scipy.optimize as optimize
#from scipy import optimize, interpolate

import create_data as CRDA
import get_parameterised_form as PARA
#reload(PARA)


DBG = SET.DEBUG
#DBG = True

MODELS, MAPS = CRDA.get_dataset_data('selected_models')
ALL_MODELS = CRDA.ALL_MODELS

fpath     = join(S['output_dir'], 'rE_comp')
filename = "rE_comp." + SET.imgext
fnn = join(fpath, filename)

# txt data of simulations
#params_file = join(S['input_dir'], 'parameters.csv')


if not os.path.exists(fpath):
    os.makedirs(fpath)


def getEinsteinR(x, y):
    #poly = interpolate.PiecewisePolynomial(x,y[:,np.newaxis])
    poly = interpolate.BPoly.from_derivatives(x,y[:,np.newaxis])
    
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
    



#with open(params_file) as f:
#    lines = f.readlines()
#    
#PARAMS = {}
#for line in lines:
#    d = [_.strip() for _ in line.split(";")]
#    if len(d)==5 and d[0][:3]=="ASW":
#        PARAMS[d[0]] = float(d[2])
#    print d



PNTS = {'x':[],'y':[]}

for swid, asw in sorted(MAPS['swid2asw'].items()):
    
    #print swid, asw
    
    #mid = CRDA.MAPS['swid2model'].get(swid, "")
    for mid in MAPS['swid2mids'].get(swid, ""):
        
        print swid, asw, mid
        
        m = ALL_MODELS[mid]
        
        # load correcting factors
        # RedshiftCorrectionFactor
        r_rcf  = m['dis_fact']          # corrects lengths for wrong redshifts
        m_rcf  = m['sig_fact']          # corrects masses for wrong redshifts
        k_rcf  = m['kappa_fact']        # corrects kappa for wrong redshifts
    
        rr = m['R']['data'] 
        da = m['kappa(<R)']['data'] * k_rcf
        
        rE = getEinsteinR(rr, da)
        
    #    if asw in PARAMS.keys():
    #        PNTS['x'].append(rE)
    #        PNTS['y'].append(PARAMS[asw])
    
        if mid in PARA.DATA.keys() and rE > 0:
            PNTS['x'].append(rE)
            PNTS['y'].append(PARA.DATA[mid]['eR'])
            print "    %5.3f %5.3f [%5.3f]" % (rE, PARA.DATA[mid]['eR'],k_rcf)
        else:
            print "    !!! skipping this mid"


x = np.array(PNTS['x'])
y = np.array(PNTS['y'])

fig = plt.figure(**STY['figure_rect_med'])
ax = fig.add_subplot(1,1,1)

# m = 1 line
mi = min([np.min(x),np.min(y)])
mx = max([np.max(x),np.max(y)])

ax.plot([0, mx], [0, mx] , **STY['fg_line2'])


kw = dict(STY['fg_marker1'])
#kw.pop('markeredgecolor', None)
#kw.pop('markeredgewidth', None)
#kw.pop('markersize', None)
kw.pop('facecolor', None)
kw['linestyle'] = 'none'
ax.plot(x, y, **kw)



#from scipy.optimize import curve_fit
#
#data = np.array([x,y])
#data.sort()
#x = data[0]
#y = data[1]
#
#def func(x,m,q):
#    return m * x # + q
#
#w = np.ones(len(x))
#w[np.argmax(x)] = 0.001
#w[np.argmax(x)-1] = 0.001
#
#popt, pcov = curve_fit(func, x, y, sigma=1/w) # popt = OPTimal Parameters for fit; COVariance matrix
#sigma = np.sqrt([pcov[0,0], pcov[1,1]]) # sqrt(diag elements) of pcov are the 1 sigma deviations
#print popt
#
#values = np.array([
#    func(x, popt[0] + sigma[0], popt[1] + sigma[1]), 
#    func(x, popt[0] + sigma[0], popt[1] - sigma[1]), 
#    func(x, popt[0] - sigma[0], popt[1] + sigma[1]), 
#    func(x, popt[0] - sigma[0], popt[1] - sigma[1]), 
#])
#fitError = np.std(values, axis=0)
#
#xv = np.linspace(0,6,100)
#curveFit = func(xv,popt[0], popt[1])
#ax.plot(xv, curveFit, 
#    linewidth=2.5, 
#    color = 'green',
#    alpha = 0.6)
#
#curveFit = func(x,popt[0], popt[1])
#nSigma = 1
#
#ax.fill_between(x, curveFit - nSigma*fitError, curveFit + nSigma*fitError,
#    color = 'purple',
#    edgecolor = None,
#    alpha = 0.5,          
#                )


ax.set_xlabel('$r_E$ modeled [arcsec]', **STY['label'])
ax.set_ylabel('$r_E$ parameterized [arcsec]', **STY['label'])

ax.set_xlim([0,np.ceil(np.max(x))])
ax.set_ylim([0,np.ceil(np.max(y))])
#ax.set_aspect('equal')

plt.tight_layout()

plt.locator_params(axis='x', numbins=5)
plt.locator_params(axis='y', numbins=7)

fig.savefig(fnn, **STY['figure_save'])

#plt.show()

    
    