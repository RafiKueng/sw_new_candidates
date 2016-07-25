#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 23:26:01 2016

@author: rafik
"""

from __future__ import unicode_literals

import os
from os.path import join

import settings as SET
reload(SET)
SET.set_mpl_rc()
STY = SET.styles
S = SET.settings

import numpy as np
#import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors
#import matplotlib.transforms as transforms
#from scipy import optimize, interpolate
from scipy import interpolate

import create_data as CRDA
# from create_data import ALL_MODELS as MODELS, LENS_CANDIDATES as LENSES
import parse_candidates as PACA


DBG = SET.DEBUG


fpath = join(S['output_dir'], "kappa_map")
filename = SET.filename_base % "kappa_map"


# rE text label position
rEpos = 0.68 # in axes coordinates
t_dx = 0.0
t_dy = 0.1


obj_index = 0


t_props = STY['text']

if not os.path.exists(fpath):
    os.makedirs(fpath)


for swid, asw in sorted(CRDA.MAPS['swid2asw'].items()):
    
    mid = CRDA.MAPS['swid2model'].get(swid, "")
    aswobj = PACA.DATA[asw]

    print swid, asw, mid
    
    if not mid:
        print "   no mid, skipping"
        continue
    
    #imgname = join(fpath, "%s_%s_kappa_encl.png" % (asw, mid))
    imgname = join(fpath, filename.format(_={'asw':asw, 'mid':mid,'swid':swid}))
    
    m = CRDA.ALL_MODELS[mid]



    #obj, data = model['obj,data'][obj_index]
    #if not data: return None


    delta  = np.log10( np.sqrt(2))  # contour level spacing in log space
    rscale = m['pxscale_fact']

    kw = {
        'extend'        : 'both', # contour levels are automatically added to one or both ends of the range so that all data are included
        'aspect'        : 'equal',
        'origin'        : 'lower',
        'colors'        : [SET.colors['hilight1'],],
        'antialiased'   : True,
    }


    # SET UP DATA

    # fix the different scaling of glass and SL
    R = m['mapextend']
    extent = np.array([-R,R,-R,R]) * rscale

    # prepare data
    grid = m['kappa_grid']
    grid = np.where(grid==0,np.nan,np.log10(grid))


    ma = np.nanmax(grid)
    mi = np.nanmin(grid)
    ab = ma if ma>-mi else -mi
    clev = np.arange(0,ab+1e-10,delta)
    clev2=-clev[:0:-1]
    clevels = np.concatenate((-clev[:0:-1],clev))
    
    print "   ma, mi, ab", ma, mi, ab
    print "   extent", extent
    # np.set_printoptions(precision=3)
    print "   clevels", clevels
    

    # PLOTTING

    # setup
    kw.update({'extent': extent})
#    kw.setdefault('extend', 'both') # contour levels are automatically added to one or both ends of the range so that all data are included
#    #kw.setdefault('interpolation', 'nearest')
#    kw.setdefault('aspect', 'equal')
#    kw.setdefault('origin', 'upper')
#    #kw.setdefault('cmap', cm.bone)
#    kw.setdefault('colors', 'k')
#    kw.setdefault('antialiased', True)

    # plot
    fig = plt.figure(**STY['figure_sq'])
    ax = fig.add_subplot(1,1,1)
    
    mymin = -R 
    mymax = R
    n_cells = m['pixrad'] * 2 + 1
    dxy = m['pixrad'] * 8 + 1
    
    X = np.linspace(mymin,mymax,n_cells)
    Y = np.linspace(mymin,mymax,n_cells)
    Xnew = np.linspace(mymin,mymax,dxy)
    Ynew = np.linspace(mymin,mymax,dxy)

    x,y = np.meshgrid(X,Y)
    
    # grid1 = np.nan_to_num(grid)
    
    # flip laong y axis
    grid = np.flipud(grid)
    
    mask = np.isnan(grid)
    grid1 = grid
    grid1[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), grid[~mask])

    f = interpolate.RectBivariateSpline(X,Y, grid1)
    
    maskf = interpolate.RectBivariateSpline(X,Y,mask, kx=1, ky=1)

    bg_mask = np.clip(maskf(Xnew, Ynew), 0,1)
    mask_inp = bg_mask < 0.5
    grid_inp = f(Xnew,Ynew)
    
    grid_inpnan = grid_inp
    grid_inpnan[~mask_inp] = np.nan
    
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("mycm",
             [ "white", SET.colors['bg_elem'] ])
    
    ax.imshow(bg_mask, extent=extent, cmap=cmap) #, interpolation='nearest')#'gray_r')
    
    CS1 = ax.contour(grid_inp, levels=clev, **kw)
    kw.update({'colors':[SET.colors['hilight2'],]})
    CS2 = ax.contour(grid_inp, levels=clev2, **kw)
    
    def fmt(x):
        return "%1.1f" % 10**x
    offs = len(clevels)//2%2 # makes sure 0 -> 1 is always labeled
    # ax.clabel(CS, clevels[offs::2], fmt=fmt, fontsize=SET.sizes['small'])

    ax.clabel(CS1, clev[::2], fmt=lambda x:"%i" % np.around(10**x) , fontsize=SET.sizes['small'], inline_spacing=5)
    ax.clabel(CS2, clev2[::-1][1::2], fmt=lambda x:"1/%i" % np.around(10**(-x)) , fontsize='10')
    
    ax.set_aspect('equal')
    ax.tick_params(axis='both', which='both', **STY['ticks'])
    # ax.grid()

#    ax.tick_params(
#        axis='both',       # changes apply to the x- and y-axis
#        which='both',      # both major and minor ticks are affected
#        bottom='off',      # ticks along the bottom edge are off
#        top='off',         # ticks along the top edge are off
#        left='off',        # ticks along the bottom edge are off
#        right='off',       # ticks along the top edge are off
#        labelbottom='off',
#        labeltop='off',
#        labelleft='off',
#        labelright='off'
#    )
    
    #plt.tight_layout()
    plt.savefig(imgname, **STY['figure_save'])
        
    if DBG:
        plt.show()
        break
    
    plt.close()













