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
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
from scipy import optimize, interpolate


import create_data as CRDA
# from create_data import ALL_MODELS as MODELS, LENS_CANDIDATES as LENSES
import parse_candidates as PACA


DBG = SET.DEBUG


fpath = join(S['output_dir'], "kappa_plot")
filename = SET.filename_base % "kappa_encl"


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


    delta  = 0.1  # contour level spacing in log space
    rscale = m['pxscale_fact']

    kw = {
        'extend'        : 'both', # contour levels are automatically added to one or both ends of the range so that all data are included
        'aspect'        : 'equal',
        'origin'        : 'upper',
        'colors'        : 'k',
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
    clevels = np.concatenate((-clev[:0:-1],clev))
    
    print "ma, mi, ab", ma, mi, ab
    print "extent", extent
    np.set_printoptions(precision=3)
    print clevels
    

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
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.contour(grid, levels=clevels, **kw)
    ax.set_aspect('equal')
    ax.tick_params(
        axis='both',       # changes apply to the x- and y-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        left='off',        # ticks along the bottom edge are off
        right='off',       # ticks along the top edge are off
        labelbottom='off',
        labeltop='off',
        labelleft='off',
        labelright='off'
        )
    
    plt.show()














