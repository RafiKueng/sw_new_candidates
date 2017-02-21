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
import scipy.ndimage

import create_data as CRDA
# from create_data import ALL_MODELS as MODELS, LENS_CANDIDATES as LENSES
import parse_candidates as PACA


MODELS, MAPS = CRDA.get_dataset_data()


DBG = SET.DEBUG
DBG = True


fpath = join(S['output_dir'], "kappa_map_interpol")
filename = SET.filename_base % "kappa_map_interpol"


# rE text label position
rEpos = 0.68 # in axes coordinates
t_dx = 0.0
t_dy = 0.1


obj_index = 0


t_props = STY['text']

if not os.path.exists(fpath):
    os.makedirs(fpath)


for swid, asw in sorted(CRDA.MAPS['swid2asw'].items()):
    
    mid = MAPS['swid2mid'].get(swid, "")

    print swid, asw, mid
    
    if not mid:
        print "   no mid, skipping"
        continue
    
    if not swid=="SW09": continue
    
    #imgname = join(fpath, "%s_%s_kappa_encl.png" % (asw, mid))
    imgname = join(fpath, filename.format(_={'asw':asw, 'mid':mid,'swid':swid}))
    
    m = CRDA.ALL_MODELS[mid]
    aswobj = PACA.DATA[asw]


    delta  = 0.2  # contour level spacing in log space
    #clevels = 20
    vmin = None
    vmax = 1

    # ScaleCorrectionFactors
    px_scf = m['pixel_scale_fact'] # corrects wrong pixel scaling in old version [old_pxl -> arcsec]
    aa_scf = m['area_scale_fact']  # corrects areas due to wrong pixel scaling in old version [old_pxl**2 -> arcsec**2]
    # RedshiftCorrectionFactor
    r_rcf  = m['dis_fact']          # corrects lengths for wrong redshifts
    m_rcf  = m['sig_fact']          # corrects masses for wrong redshifts
    k_rcf  = m['kappa_fact']        # corrects kappa for wrong redshifts
 

    # SET UP DATA
    R = m['mapextend'] * px_scf * r_rcf
    extent = np.array([-R,R,-R,R])

    # prepare data
    grid_org = m['kappa_grid'] * k_rcf

    w = m['kappa'] != 0
    if not np.any(w):
        vmin = -15
        grid_org += 10**vmin
    else:
        vmin = np.log10(np.amin(m['kappa'][w]))
        #print 'min?', np.amin(data['kappa'] != 0)
        # kw['vmin'] = vmin
    #if vmax is not None:
        # kw['vmax'] = vmax
    zoomlvl = 5
    grid = scipy.ndimage.zoom(grid_org, zoomlvl, order=0)
    #mask = scipy.ndimage.zoom(grid_org==0, zoomlvl, order=0)
    mask = grid_org==0  # actually there is no need to zoom the mask if 
                        # we use imshow with extent
    grid[grid<=10**vmin] = 10**vmin
    grid_log = np.log10(grid)

    
    kw = {
        'extent': [-R,R,-R,R],
        'vmin': vmin,
        'vmax': vmax
    }
    matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
    
    ma = np.nanmax(grid)
    mi = np.nanmin(grid)
    ab = ma if ma>-mi else -mi
    clev_up = np.arange(0,ab+1e-10,delta)
    clev_dn = -clev_up[:0:-1]
    clevels = np.concatenate((clev_dn, clev_up))
#    clev_up = 10**clev_up
#    clev_dn = 10**clev_dn


    # plot
    fig = plt.figure(**STY['figure_sq'])
    ax = fig.add_subplot(1,1,1)


    kw.update(STY['fg_contour'])
    Cup = ax.contour(grid_log, levels=clev_up, **kw)
    kw.update(STY['bg_contour'])
    Cdn = ax.contour(grid_log, levels=clev_dn, **kw)
    
#    if False:
#        ax.clabel(Cup, inline=1, fontsize=10)
#        ax.clabel(Cdn, inline=1, fontsize=10)
        
    cc= matplotlib.colors.ColorConverter()
    r,g,b = cc.to_rgb(SET.colors['bg_elem'])
    img = np.zeros(mask.shape + (4,))
    img[:, :, 0] = r
    img[:, :, 1] = g
    img[:, :, 2] = b
    img[:, :, 3] = mask # alpha channel
    #ax.imshow(img, extent=[-R,R,-R,R], interpolation='nearest', zorder=2)

        
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













