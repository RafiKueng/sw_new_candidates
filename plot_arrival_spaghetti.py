#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""

copy & paste & adapt from glass


Created on Tue Jul 26 18:24:18 2016

@author: rafik
"""

import os
from os.path import join

import settings as SET
reload(SET)
SET.set_mpl_rc()
STY = SET.styles
S = SET.settings


import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm

import create_data as CRDA
import parse_candidates as PACA


MODELS, MAPS = CRDA.get_dataset_data()
ALL_MODELS = CRDA.ALL_MODELS

DBG = SET.DEBUG
#DBG = True
DBG_DO =  ["SW01"] #[ "ENWYZIEIV6", "TGM4U2TZBS"] #"SW42",

itemname = "arrival_spaghetti"
fpath = join(S['output_dir'], itemname)
filename = SET.filename_base % itemname

if not os.path.exists(fpath):
    os.makedirs(fpath)


def arrival_plot(model, ax):

    clevels         = 40

    source_indices =         model['source_indices']
    arrival_contour_levels = model['arrival_contour_levels']
    arrival_grid =           model['arrival_grid']
    R =                      model['mapextend']


    def plot_one(src_index,g,lev,kw):
        matplotlib.rcParams['contour.negative_linestyle'] = 'solid'

        if clevels:
            loglev=clevels
            kw.update(STY['bg_contour'])
            kw.update({
                'zorder' : -89,
            })
            ax.contour(g, loglev, **kw)

        if lev:
            kw.update(STY['fg_contour'])
            kw.update({
                'zorder' : 89,
            })
            ax.contour(g, lev, **kw)


    for src_index in source_indices:

        if arrival_contour_levels:
            levels = arrival_contour_levels[src_index]
        g = arrival_grid[src_index]

        kw = {
            'clevels': clevels,
            'extent' : [-R,R,-R,R]
        }

        plot_one(src_index, g, levels, kw)
        plt.xlim(-R, R)
        plt.ylim(-R, R)

    plt.gca().set_aspect('equal')
    
    
    
def overlay_input_points(model, ax):
    '''adds the input points (min, max, sad, pmass) ontop of existing plot'''
  
    overlay_ext_pot = True

    source_images = model['source_images']
    extra_potentials = model['extra_potentials']


    if overlay_ext_pot:
        for epot in extra_potentials:
            ax.plot([epot['r'].real], [epot['r'].imag], 'sy')
  

    for img in source_images:
        #['min', 'sad', 'max', 'unk'].index(parity)
        # tp = ['c', 'g', 'r', 'm'][img['parity']]
        tp = STY['EXTPNT']['colors'][img['parity']]
        #print img['pos'], tp
        ax.plot([img['pos'].real], [img['pos'].imag], marker='o', color=tp, zorder=110)

    #mark origin
    ax.plot([0], [0], marker='o', color=STY['EXTPNT']['colors'][2], zorder=110)


    

#
# main loop
#
for swid, asw in sorted(MAPS['swid2asw'].items()):

    for mid in sorted(MAPS['swid2mids'].get(swid, [])):

        #mid = CRDA.MAPS['swid2model'].get(swid, "")
        #mid = MAPS['swid2mid'].get(swid, "")
        
        if DBG and ( not swid in DBG_DO and not mid in DBG_DO ):
            continue
    
        print swid, asw, mid

        if not mid:
            print "   no mid, skipping"
            continue
    
        m = ALL_MODELS[mid]
        aswobj = PACA.DATA[asw]
    
        imgname = join(fpath, filename.format(_={'asw':asw, 'mid':mid,'swid':swid}))
        
        # load correcting factors
        # ScaleCorrectionFactors
        px_scf = m['pixel_scale_fact'] # corrects wrong pixel scaling in old version [old_pxl -> arcsec]
        aa_scf = m['area_scale_fact']  # corrects areas due to wrong pixel scaling in old version [old_pxl**2 -> arcsec**2]
        # RedshiftCorrectionFactor
        r_rcf  = m['dis_fact'] or 1          # corrects lengths for wrong redshifts
        m_rcf  = m['sig_fact'] or 1          # corrects masses for wrong redshifts
        k_rcf  = m['kappa_fact'] or 1        # corrects kappa for wrong redshifts
    
        print "   "," | ".join(['%3.3f'%_ for _ in [px_scf, aa_scf, r_rcf, m_rcf, k_rcf]])
    
        #print m['source_indices']
        #print m['arrival_contour_levels']
        #print np.average(m['arrival_grid'])
        print "   ",m['mapextend']
        print "   ",m['lmt_ver'], " | ", m['gls_ver']
        
    
        fig = plt.figure(**STY['figure_sq_small'])
        ax = fig.add_subplot(111)
        
        arrival_plot(m, ax)
        overlay_input_points(m, ax)
        
        ax.tick_params(**STY['no_ticks'])
        ax.tick_params(**STY['no_labels'])
        #ax.grid()
        
        if m['mapextend'] > 1.2:
            Llng = 1
            Llbl = r"1$^{\prime\prime}$"
        else:
            Llng = 0.1
            Llbl = r"0.1$^{\prime\prime}$"
            
        
        tmp1 = SET.add_inline_label(ax, swid, color="bright")
        tmp2 = SET.add_size_bar(ax, Llbl,
                                length=Llng,
                                height=0.01,
                                heightIsInPx = True,
                                theme = "bright",
                                **STY['scalebar']
                                )
        
        plt.tight_layout()
        
        fig.savefig(imgname, **STY['figure_save'])
        
        if DBG:
            #plt.show()
            #break
            pass
        plt.close()
    