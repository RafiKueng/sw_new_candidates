# -*- coding: utf-8 -*-
"""
Created on Fri May 20 02:01:26 2016

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


import create_data as CRDA
import parse_candidates as PACA

from EinsteinRadius import getEinsteinR


DBG = SET.DEBUG
#DBG = True
DBG_DO = ["SW57",]

MODELS, MAPS = CRDA.get_dataset_data()
ALL_MODELS = CRDA.ALL_MODELS


fpath = join(S['output_dir'], "kappa_encl")
filename = SET.filename_base % "kappa_encl"


# rE text label position
rEpos = 0.5 # in axes coordinates
t_dx = 0.0
t_dy = 0.1



t_props = STY['text']

if not os.path.exists(fpath):
    os.makedirs(fpath)




for swid, asw in sorted(MAPS['swid2asw'].items()):
    
    #mid = MAPS['swid2mid'].get(swid, "")
    for mid in sorted(MAPS['swid2mids'].get(swid, "")):

        print swid, asw, mid
        
        if DBG and ((swid not in DBG_DO) and (mid not in DBG_DO)): continue
        
        imgname = join(fpath, filename.format(_={'asw':asw, 'mid':mid,'swid':swid}))
        
        m      = ALL_MODELS[mid]
        aswobj = PACA.DATA[asw]
        
        # load correcting factors
        # RedshiftCorrectionFactor
        r_rcf  = m['dis_fact']          # corrects lengths for wrong redshifts
        m_rcf  = m['sig_fact']          # corrects masses for wrong redshifts
        k_rcf  = m['kappa_fact']        # corrects kappa for wrong redshifts
        isZCorr = m['z_corrected']
    
        # m['kappa(<R)'] is actually kappa_infty!
        # kappa = D_ls / D_s * kappa_infty
        
        print "      ", r_rcf, m_rcf, k_rcf, isZCorr

        
    #    if not r_rcf:
    #        print "   no redshifts given, skipping"
    #        continue
        
        rr = m['R']['data']        
        da = m['kappa(<R)']['data'] * k_rcf
        mn = m['kappa(<R)']['min']  * k_rcf
        mx = m['kappa(<R)']['max']  * k_rcf
        
        xmax = np.max(rr)
        xmin = 0.0
        ymin = np.min(mn)
        ymax = np.max(mx)
    
        fig = plt.figure(**STY['figure_sq_small'])
        ax = fig.add_subplot(1,1,1)
    
        # the x coords of this transformation are data, and the
        # y coord are axes
        trans = transforms.blended_transform_factory(
            ax.transData, ax.transAxes)
    
        
        #ax.plot(rr, mn, 'b')
        #ax.plot(rr, mx, 'b')
        ax.plot(rr, da, **STY['fg_line1'])
        ax.fill_between(rr, mx, mn, **STY['fg_area1'])
    
    
        #plt.plot([xmin,xmax], [1,1], 'k:')  
        ax.axhline(1, **STY['bg_line'])
    
        rE_mean = getEinsteinR(rr, da)
        rE_min  = getEinsteinR(rr, mn)
        rE_max  = getEinsteinR(rr, mx)
        #a_re_mean = np.array([rE_mean, rE_mean])
        
        print_rE = False
        print_rE_line = True
        
        if not rE_mean:
            # print "ALERT!!!! did not found an rE.. we should handle this.."
            # rE_mean = xmax/2
            print_rE = False
    
        if print_rE_line:
            #ax.axvline(rE_mean, 0, rEpos, **STY['fg_line3'])
            if rE_mean>0:
                ax.axvline(rE_mean, 0, 1, **STY['fg_line3'])
    
        if print_rE:
            #rE_pos = max(round(ymax*0.5), 2)
            
            #plt.plot(np.array([rE_mean, rE_mean]), [0,rE_pos], '--', color=(0,0.5,0))
            
            if rE_mean > 0.75*xmax:
                ha = "right" 
            elif rE_mean < 0.5*xmax:
                ha = "left"
            else:
                ha = "center" 
            
            lbl = r'$\Theta_\mathrm{E} = {%4.2f}' % rE_mean
    
            # for alignment, first add signes
    
            if rE_min or rE_max:
                lbl += r'\stackrel'
    
            if rE_max:
                lbl += r'{+ %4.2f}' % (rE_max-rE_mean)
            else:
                lbl += r'{?}'
            if rE_min:
                lbl += r'{\,-\,%4.2f} ' % (rE_mean-rE_min)
            else:
                lbl += r'{?}'
    
                
            lbl += r'$'
    
            # print lbl
            ax.text(
                rE_mean+t_dx, rEpos,
                lbl,
                transform=trans,
                horizontalalignment=ha,
                **STY['text'])
    
        
        #append the max in 0/0
        #m['images'].append({'pos':0+0j, 'type':'max', 'angle':0})
        
        SET.plot_image_positions(ax, m['images'] + [{'pos':0,'type':'max'},] )
    
    #    kw2 = dict(STY['smallticks'])
    #    kw2.update({
    #               'labelleft': True
    #               })
    #    ax.tick_params(axis='both', **STY['bigtickslabel'])
    #    ax.tick_params(axis='both', **kw2)
    
        ax.tick_params(**STY['ticks_bottom_left'])
        ax.tick_params(**STY['big_majorticks'])
        ax.tick_params(**STY['big_minorticks'])
        ax.tick_params(**STY['labels_bottom_left'])
    
    
        #plt.tight_layout()
        ax.set_ylim(bottom=0.51, top=7.9)
        ax.set_yscale('log')    
        
        ddxx = np.max(rr) * 0.05
        ax.set_xlim(left=-ddxx, right=np.max(rr)+ddxx)
        
    
        plt.xlabel(r'Image radius $r$ [arcsec]', **STY['label'])
        plt.ylabel(r'Enclosed kappa $\kappa_{< R}$ [1]', **STY['label'])
    
        formatter = mpl.ticker.FuncFormatter(
            lambda x, p: str(int(round(x))) if x>=1 else str(round(x,1))
        )
        ax.yaxis.set_major_formatter(formatter)
        ax.yaxis.set_minor_formatter(formatter)
    
        SET.add_caption_swid(ax, text=swid, color='bright')
        SET.add_caption_mid(ax, text=mid+("" if isZCorr else "*"), color='bright')
        
        fig.tight_layout()        
        fig.savefig(imgname, **STY['figure_save'])
    
        if DBG:
            plt.show()
            break
        
        plt.close(fig)

