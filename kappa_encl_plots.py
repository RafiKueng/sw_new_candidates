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
import matplotlib.transforms as transforms
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
    



# rE text label
rEpos = 0.6667 # in axes
t_dx = 0.0
t_dy = 0.1

t_props = {
    'ha':'left',
    'va':'bottom',
    'size': 14,
} 

# Image marker postitions
iypos = 0.8 # general y postion of the image marker line
dy = 0.075  # length of the line 
oy = 0.025   # offset between lines



for swid, asw in sorted(CRDA.MAPS['swid2asw'].items()):
    
    mid = CRDA.MAPS['swid2model'].get(swid, "")
    aswobj = PACA.DATA[asw]

    print swid, asw, mid
    
    if not mid:
        print "   no mid, skipping"
        continue
    
    imgname = "output/M_encl/%s_%s_M_encl.png" % (asw, mid)
    
    m = CRDA.ALL_MODELS[mid]
    
    # load correcting factors
    s_cf = m['scale_fact'] # corrects wrong pixel scaling
    m_cf = m['sig_fact']   # corrects masses for wrong redshifts
    r_cf = m['dis_fact']   # corrects lengths for wrong redshifts
    D = m['D']

    # m['kappa(<R)'] is actually kappa_infty!
    # kappa = D_ls / D_s * kappa_infty
    #
    f_D = D['ls']['actual'] / D['s']['actual'] * D['l']['used'] / D['l']['actual']
    
    print "      ",s_cf, m_cf, r_cf, f_D
    
    if not m_cf:
        print "   no redshifts given, skipping"
        continue

    rr = m['R']['data']
    da = m['kappa(<R)']['data'] * f_D
    mn = m['kappa(<R)']['min']  * f_D
    mx = m['kappa(<R)']['max']  * f_D
    
    xmax = np.max(rr)
    xmin = 0.0
    ymin = np.min(mn)
    ymax = np.max(mx)

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    # the x coords of this transformation are data, and the
    # y coord are axes
    trans = transforms.blended_transform_factory(
        ax.transData, ax.transAxes)

    
    plt.plot(rr, mn, 'b')
    plt.plot(rr, mx, 'b')
    plt.plot(rr, da, 'b--')
    plt.fill_between(rr, mx, mn, facecolor='blue', alpha=0.5)


    #plt.plot([xmin,xmax], [1,1], 'k:')  
    plt.axhline(1, color="k", ls=":")

    rE_mean = getEinsteinR(rr, da)
    rE_min  = getEinsteinR(rr, mn)
    rE_max  = getEinsteinR(rr, mx)
    #a_re_mean = np.array([rE_mean, rE_mean])
    
    print_rE = True
    if not rE_mean:
        # print "ALERT!!!! did not found an rE.. we should handle this.."
        # rE_mean = xmax/2
        print_rE = False

    if print_rE:
        rE_pos = max(round(ymax*0.75), 3)
        
        #plt.plot(np.array([rE_mean, rE_mean]), [0,rE_pos], '--', color=(0,0.5,0))
        plt.axvline(rE_mean, 0, rEpos, ls='--', color=(0,0.5,0))
        
        if rE_mean > 0.75*xmax:
            ha = "right" 
        elif rE_mean < 0.25*xmax:
            ha = "left"
        else:
            ha = "center" 
        
        lbl = r'$r_\Theta = %4.2f \; ' % rE_mean
        if rE_min:
            lbl += r'_{-%4.2f} ' % (rE_mean-rE_min)
        else:
            lbl += r'_{?}'

        if rE_max:
            lbl += r'^{+%4.2f}' % (rE_max-rE_mean)
        else:
            lbl += r'^{?}'
            
        lbl += r'$'
        plt.text(
            rE_mean+t_dx, rEpos,
            lbl,
            transform=trans,
            horizontalalignment=ha,
            **t_props)

    
    #append the max in 0/0
    #m['images'].append({'pos':0+0j, 'type':'max', 'angle':0})

    for ii in m['images']:
        xpos = np.abs(ii['pos'])
        jj = ["min", "sad", "max"].index(ii['type'])
        c = ["red", "blue", "green"][jj]
        m = ['1', '2', '3'][jj] # assign marker style
        m = ['v', '>', '^'][jj] # assign marker style
        # http://matplotlib.org/examples/lines_bars_and_markers/marker_reference.html
        de = [(0,3),(2,3),(2,3)][jj] # draw every (start, offset)
        
        sy = oy * jj
        #plt.axvline(xpos, iypos+sy, iypos+dy+sy, color="k" )
        
        #_, iypt=  ax.transData.transform_point((0, iypos+dy+sy))
        #_, iypb=  ax.transData.transform_point((0, iypos+sy))
        #print iypt, iypb
        plt.plot([xpos, xpos, xpos], [iypos+sy, iypos+dy/2.+sy, iypos+dy+sy],
                 color=c,
                 marker=m,
                 markevery=de,
                 markeredgecolor=c, markerfacecoloralt=c,
                 transform=trans)
    
    plt.tick_params(axis='both', which='both', labelsize=16)


    #plt.tight_layout()
    plt.ylim([0.5,10])
    ax.set_yscale('log')    

    plt.xlabel(r'image radius [arcsec]', fontsize = 18)
    plt.ylabel(r'$\kappa$(\textless R) [1]', fontsize = 18)

    formatter = mpl.ticker.FuncFormatter(lambda x, p: '$'+str(int(round(x)))+'$' if x>=1 else '$'+str(round(x,1))+'$')
    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.set_minor_formatter(formatter)

    #plt.show()
    plt.savefig(imgname)
    plt.close()
    #break
