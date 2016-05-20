# -*- coding: utf-8 -*-
"""
Created on Fri May 20 02:01:26 2016

@author: rafik
"""


import create_data as CRDA
from create_data import ALL_MODELS as MODELS, LENS_CANDIDATES as LENSES
import parse_candidates as PACA

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy import optimize, interpolate



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
    




t_dx = 0.0
t_dy = 0.1
t_props = {'ha':'left', 'va':'bottom'} 


for swid, asw in sorted(CRDA.MAPS['swid2asw'].items()):
    
    mid = CRDA.MAPS['swid2model'].get(swid, "")
    aswobj = PACA.DATA[asw]

    if not mid:
        continue
    
    imgname = "output/M_encl/%s_M_encl.png" % mid
    
    m = CRDA.ALL_MODELS[mid]

    rr = m['R']['data']
    da = m['kappa(<R)']['data']
    mn = m['kappa(<R)']['min']
    mx = m['kappa(<R)']['max']
    
    xmax = np.max(rr)
    xmin = 0.0
    ymin = np.min(mn)
    ymax = np.max(mx)

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    
    plt.plot(rr, mn, 'b')
    plt.plot(rr, mx, 'b')
    plt.plot(rr, da, 'b--')
    plt.fill_between(rr, mx, mn, facecolor='blue', alpha=0.5)

    plt.plot([xmin,xmax], [1,1], 'k:')  


    rE_mean = getEinsteinR(rr, da)
    rE_min  = getEinsteinR(rr, mn)
    rE_max  = getEinsteinR(rr, mx)
    #a_re_mean = np.array([rE_mean, rE_mean])

    rE_pos = max(round(ymax*0.75), 3)
    
    plt.plot(np.array([rE_mean, rE_mean]), [0,rE_pos], '--', color=(0,0.5,0))
    plt.text(rE_mean+t_dx, rE_pos+t_dy, '$r_E = %4.2f [%4.2f .. %4.2f]$'%(rE_mean, rE_min, rE_max), **t_props)

    
    plt.tick_params(axis='both', which='both', labelsize=16)


    #plt.tight_layout()
    plt.ylim([0.5,10])
    ax.set_yscale('log')    

    plt.xlabel(r'image radius [arcsec]', fontsize = 18)
    plt.ylabel(r'kappa(R) [1]', fontsize = 18)

    formatter = mpl.ticker.FuncFormatter(lambda x, p: '$'+str(int(round(x)))+'$' if x>=1 else '$'+str(round(x,1))+'$')
    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.set_minor_formatter(formatter)

    #plt.show()
    plt.savefig(imgname)
    plt.close()
    #break
