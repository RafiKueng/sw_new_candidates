# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 10:22:51 2016

@author: rafik
"""

import os
import sys

import numpy as np
import matplotlib as mpl

#mpl.rc('font', family='serif')
#mpl.rc('text', usetex=True)

import matplotlib.pyplot as plt
import matplotlib.transforms as transforms


from stelmass.angdiam import sig_factor, dis_factor

import create_data as CRDA
#from create_data import ONLY_RECENT_MODELS as MODELS, LENS_CANDIDATES as LENSES

from settings import settings as S, INT
from settings import print_first_line, getI, print_last_line




path     = os.path.join(S['output_dir'], 'plots2')
filename = '{_[swid]}_{_[asw]}_{_[mid]}_enclMass_dispersion.png'
title = '{_[swid]} {_[asw]} {_[mid]}'

if not os.path.exists(path):
    os.makedirs(path)


#def create_plot(mid):
#if True:
init = True

swid = "SW05"
for mid in CRDA.MAPS['swid2all_models'][swid]:
    
    
    #mid = CRDA.MAPS['swid2model']['SW05']
    #mid = CRDA.MAPS['swid2model']['SW28']

    m = CRDA.ALL_MODELS[mid]
    if not 'swid' in m:
        m['swid'] = swid

    print title.format(_=m)

        
    ffn = os.path.join(path, filename.format(_=m))

    fig = plt.figure(figsize=(8,4), dpi=100)
    #fig = plt.figure(dpi=100)
    ax1 = fig.add_subplot(1,2,1)
    ax2 = fig.add_subplot(1,2,2)


    # make redshoft correction
    zl_actual = 0.56 # m['z_lens_meassured']
    zs_actual = 2.9                 #!!!!!!!!! source redshifts not yet available, using estimate
    zl_used = m['z_lens_used']
    zs_used = m['z_src_used']
       
    m_cf = sig_factor(zl_actual,zs_actual) / sig_factor(zl_used,zs_used)
    r_cf = dis_factor(zl_actual,zs_actual) / dis_factor(zl_used,zs_used)

    #m_cf = 1.0
    #r_cf = 1.0

    arcsec_2_kpc = m['R']['units']['kpc'][0] * r_cf
    r = m['R']['data'] * m['R']['units']['kpc'][0] # factor at the end converts from arcsec to kpc
    r = r * r_cf # correct for wrong redshifts
    
    r = m['R']['data'] * arcsec_2_kpc

    _me = m['M(<R)']

    me = _me['data'] * m_cf
    me_min = _me['min'] * m_cf
    me_max = _me['max'] * m_cf
    
    err_m = me - me_min
    err_p = me_max - me 
    
    scl = 1e12
    ax1.errorbar(r, me/scl, yerr=[err_m/scl, err_p/scl], fmt='ko')
    
    #ax1.set_title("Stellar vs Lensing Mass")
    ax1.set_xlabel(ur'Radius $\mathrm{r}$ \, $(kpc)$')
    ax1.set_ylabel(ur'Enclosed Mass $\mathrm{M_{<R}}$ \, $(10^{12} M_{\odot})$')
    
    #axis limits
#    ax.set_xlim(xmin=2e8, xmax=1e12)
#    ax.set_ylim(ymin=2e10, ymax=1e14)
#    ax.set_xscale("log", nonposx='clip')
#    ax.set_yscale("log", nonposy='clip')

    # convert raduis to meter, mass to kg, ...
    G = 6.674e-11
    kpc_2_m = 3.086e19
    Msol = 1.988e30

    menc_kg = me * Msol
    menc_kg_min = me_min * Msol
    menc_kg_max = me_max * Msol

    sigma = np.sqrt(2*G*menc_kg/3./np.pi/(r*kpc_2_m))
    err_p = np.sqrt(2*G*menc_kg_max/3./np.pi/(r*kpc_2_m)) -sigma
    err_m = sigma - np.sqrt(2*G*menc_kg_min/3./np.pi/(r*kpc_2_m))

    yscl = 1e3
    ax2.errorbar(r, sigma/yscl, yerr=[err_m/yscl, err_p/yscl], fmt='ko')
    ax2.set_ylim([0,525])

    ax2.set_xlabel(u'Radius $\mathrm{r}$ \, $[kpc]$')
    ax2.set_ylabel(u'Dispersion $\sigma$ \, $[km\;sec^{-1}]$')
    
    #ax2.set_title("Stellar vs Lensing Mass")
    #ax2.set_xlabel(u'Radius $\mathrm{r (kpc)$')
    #ax2.set_ylabel(u'Formal dispersion $\mathrm{\sigma_{lens} (km\,s^{-1})}$')


    # Image marker postitions
    iypos = 0.8 # general y postion of the image marker line
    dy = 0.075  # length of the line 
    oy = 0.025   # offset between lines

    for ax in [ax1, ax2]:
        # the x coords of this transformation are data, and the
        # y coord are axes
        trans = transforms.blended_transform_factory(
            ax.transData, ax.transAxes)
    
        for ii in m['images']:
            xpos = np.abs(ii['pos']) * arcsec_2_kpc
            jj = ["min", "sad", "max"].index(ii['type'])
            c = ["red", "blue", "green"][jj]
            mk = ['1', '2', '3'][jj] # assign marker style
            #mk = ['v', '>', '^'][jj] # assign marker style
            # http://matplotlib.org/examples/lines_bars_and_markers/marker_reference.html
            de = [(0,3),(2,3),(2,3)][jj] # draw every (start, offset)
            
            sy = oy * jj
            #plt.axvline(xpos, iypos+sy, iypos+dy+sy, color="k" )
            
            #_, iypt=  ax.transData.transform_point((0, iypos+dy+sy))
            #_, iypb=  ax.transData.transform_point((0, iypos+sy))
            #print iypt, iypb
            ax.plot([xpos, xpos, xpos], [iypos+sy, iypos+dy/2.+sy, iypos+dy+sy],
                     color=c,
                     marker=mk,
                     markevery=de,
                     markeredgecolor=c, markerfacecoloralt=c,
                     transform=trans)



    fig.suptitle(title.format(_=m), fontsize=12)
    fig.set_tight_layout(True)
    #plt.tight_layout()
    fig.savefig(ffn, dpi=150)
    if init:
        plt.show()
        init=False
    #break
    plt.clf()
    plt.close(fig)




### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)


print_last_line(I)

    

            