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
import scipy
#from scipy import interpolate, ndimage

import create_data as CRDA
import parse_candidates as PACA


MODELS, MAPS = CRDA.get_dataset_data()

DBG = SET.DEBUG
#DBG = True


fpath = join(S['output_dir'], "kappa_map_simple")
filename = SET.filename_base % "kappa_map_simple"


# rE text label position
#rEpos = 0.68 # in axes coordinates
#t_dx = 0.0
#t_dy = 0.1


obj_index = 0


t_props = STY['text']

if not os.path.exists(fpath):
    os.makedirs(fpath)


for swid, asw in sorted(CRDA.MAPS['swid2asw'].items()):
    
    #mid = CRDA.MAPS['swid2model'].get(swid, "")
    mid = MAPS['swid2mid'].get(swid, "")

    print swid, asw, mid
    if not mid:
        print "   no mid, skipping"
        continue
    
    #imgname = join(fpath, "%s_%s_kappa_encl.png" % (asw, mid))
    imgname = join(fpath, filename.format(_={'asw':asw, 'mid':mid,'swid':swid}))
    
    m = CRDA.ALL_MODELS[mid]
    aswobj = PACA.DATA[asw]


    delta  = np.log10( 10 ** 0.2 )  # contour level spacing in log space
    #rscale = m['pxscale_fact']

    # ScaleCorrectionFactors
    px_scf = m['pixel_scale_fact'] # corrects wrong pixel scaling in old version [old_pxl -> arcsec]
    aa_scf = m['area_scale_fact']  # corrects areas due to wrong pixel scaling in old version [old_pxl**2 -> arcsec**2]
    # RedshiftCorrectionFactor
    r_rcf = m['dis_fact']          # corrects lengths for wrong redshifts
    m_rcf = m['sig_fact']          # corrects masses for wrong redshifts
    k_rcf = m['kappa_fact']        # corrects kappa for wrong redshifts



    kw = {}


    # SET UP DATA

    # fix the different scaling of glass and SL
    R = m['mapextend']
    extent = np.array([-R,R,-R,R]) * px_scf * r_rcf

    # prepare data
    grid = m['kappa_grid'] * k_rcf
    grid = np.where(grid==0,np.nan,np.log10(grid))


    ma = np.nanmax(grid)
    mi = np.nanmin(grid)
    ab = ma if ma>-mi else -mi
    clev = np.arange(0,ab+1e-10,delta)
    clev2=-clev[:0:-1]
    clevels = np.concatenate((-clev[:0:-1],clev))
    
    #print "   ma, mi, ab", ma, mi, ab
    #print "   extent", extent
    # np.set_printoptions(precision=3)
    #print "   clevels", clevels
    

    # PLOTTING

    # setup
    kw.update({'extent': extent})

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
    
    # flip laong y axis
    #grid = np.flipud(grid)
    
    mask = np.isnan(grid)
#    grid1 = grid
#    grid1[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), grid[~mask])
#
#    f = interpolate.RectBivariateSpline(X,Y, grid1)
#    
#    maskf = interpolate.RectBivariateSpline(X,Y,mask, kx=1, ky=1)
#
#    bg_mask = np.clip(maskf(Xnew, Ynew), 0,1)
#    mask_inp = bg_mask < 0.5
#    grid_inp = f(Xnew,Ynew)
#    
#    grid_inpnan = grid_inp
#    grid_inpnan[~mask_inp] = np.nan

    #grid = scipy.ndimage.zoom(grid, 3)
    #mask = scipy.ndimage.zoom(mask, 3, order=0)
    
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("mycm",
             [ "white", SET.colors['bg_elem'] ])
    
    ax.imshow(mask, extent=extent, cmap=cmap, interpolation='nearest')#'gray_r')
    
    kw.update(STY['fg_contour'])
    CS1 = ax.contour(grid, levels=clev, **kw)

    kw.update(STY['bg_contour'])
    CS2 = ax.contour(grid, levels=clev2, **kw)
    

#    # contour labels
#    def fmt(x):
#        return "%1.1f" % 10**x
#    offs = len(clevels)//2%2 # makes sure 0 -> 1 is always labeled
#    # ax.clabel(CS, clevels[offs::2], fmt=fmt, fontsize=SET.sizes['small'])
#
#    ax.clabel(CS1, clev[::2], fmt=lambda x:"%i" % np.around(10**x) , fontsize=SET.sizes['small'], inline_spacing=5)
#    ax.clabel(CS2, clev2[::-1][1::2], fmt=lambda x:"1/%i" % np.around(10**(-x)) , fontsize='10')
    

    ax.set_aspect('equal')
    
    ax.tick_params(**STY['big_majorticks'])
    ax.tick_params(**STY['no_labels'])
    
    ax.grid()
    
    SET.add_inline_label(ax, swid, color='bright')
    SET.add_size_bar(ax, r"1$^{\prime}$", length=1, color="bright")
    
    fig.tight_layout()
    fig.savefig(imgname, **STY['figure_save'])
        
    if DBG:
        plt.show()
        break
    
    fig.clear()
    plt.close()













