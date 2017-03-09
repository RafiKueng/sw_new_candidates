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
#DBG = True
DBG_swid=02


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


for swid, asw in sorted(MAPS['swid2asw'].items()):
    
    for mid in MAPS['swid2mids'].get(swid, ""):
#    mid = MAPS['swid2mid'].get(swid, "")

        print swid, asw, mid
        
        if not mid:
            print "   no mid, skipping"
            continue
        
        if DBG and not swid==DBG_swid: continue
        
        #imgname = join(fpath, "%s_%s_kappa_encl.png" % (asw, mid))
        imgname = join(fpath, filename.format(_={'asw':asw, 'mid':mid,'swid':swid}))
        
        m = CRDA.ALL_MODELS[mid]
        aswobj = PACA.DATA[asw]
    
    
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
        R = m['mapextend'] * px_scf
        extent = np.array([-R,R,-R,R])
    
        # prepare data
        grid_org = m['kappa_grid'] * k_rcf
    
        w = m['kappa'] != 0
        if not np.any(w):
            vmin = -15
            grid_org += 10**vmin
        else:
            vmin = np.log10(np.amin(m['kappa'][w]))
    
        # upscale and interpolate spline order
        zoomlvl = 3
        order   = 0
        grid = scipy.ndimage.zoom(grid_org, zoomlvl, order=order)
        #mask = scipy.ndimage.zoom(grid_org==0, zoomlvl, order=0)
        mask = grid_org==0  # actually there is no need to zoom the mask if 
                            # we use imshow with extent
        grid[grid<=10**vmin] = 10**vmin
        grid_log = np.log10(grid)
    
        
        kw = {
            'extent': [-R,R,-R,R],
    #        'vmin': vmin,
    #        'vmax': vmax
        }
        matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
        
    #    ma = np.nanmax(grid_log)
    #    mi = np.nanmin(grid_log)
    #    ab = ma if ma>-mi else -mi
    
    
        delta     = 0.2
        ncontours = 3    # there will actually be (n-1)*2 regions
        clev_up = np.arange(delta, ncontours*delta, delta)
        clevels = np.concatenate((sorted(-clev_up), [0,], clev_up))
    
    
        # plot
        fig = plt.figure(**STY['figure_sq_small'])
        ax = fig.add_subplot(1,1,1)
    
    
    #    kw.update(STY['fg_contour'])
    #    Cup = ax.contour(grid_log, levels=clev_up, **kw)
    #    kw.update(STY['bg_contour'])
    #    Cdn = ax.contour(grid_log, levels=clev_dn, **kw)
        kw.update(STY['filled_contours'])
        #grid_log[grid_log<-0.6] = -0.6
    
        Cdn = ax.contourf(grid_log, levels=clevels, **kw)
    #    ax.imshow(grid_log,
    #              extent=[-R,R,-R,R],
    #              interpolation='nearest',
    #              cmap = "coolwarm",
    #              vmin = clevels[0], vmax=clevels[-1],
    #              )
        
        kw.update(STY['main_contour'])
        Cdn = ax.contour(grid_log, levels=[0,], **kw)
        
    #    if False:
    #        ax.clabel(Cup, inline=1, fontsize=10)
    #        ax.clabel(Cdn, inline=1, fontsize=10)
            
        cc= matplotlib.colors.ColorConverter()
        r,g,b = cc.to_rgb("gray")
        img = np.zeros(mask.shape + (4,))
        img[:, :, 0] = r
        img[:, :, 1] = g
        img[:, :, 2] = b
        img[:, :, 3] = mask # alpha channel
        #ax.imshow(img, extent=[-R,R,-R,R], interpolation='nearest', zorder=2)
    
            
        ax.set_aspect('equal')
        
        ax.tick_params(**STY['no_ticks'])
        ax.tick_params(**STY['no_labels'])
        
        #ax.grid()
    
        SET.add_inline_label(ax, swid, color='bright')
        tmp2 = SET.add_size_bar(ax, r"1$^{\prime\prime}$",
                                length=1,
                                height=0.01,
                                heightIsInPx = True,
                                theme = "bright",
                                **STY['scalebar']
                                )
        
        fig.tight_layout()
        fig.savefig(imgname, **STY['figure_save'])
            
        if DBG:
            plt.show()
            break
        
        fig.clear()
        plt.close()
    
    
    
    
    








