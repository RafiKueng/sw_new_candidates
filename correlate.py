# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 16:45:27 2015

@author: rafik
"""
import os
import cPickle as pickle
import numpy as np
import matplotlib as mpl

mpl.rc('font', family='serif')
mpl.rc('text', usetex=True)

import matplotlib.pyplot as plt

import candidates
from stelmass.stelpops2 import get_stellar_masses



pickle_name = 'all_data.pickle'


all_models = {}

# get total masses
if os.path.isfile(pickle_name):
    print "correlate: loaded all data from pickle"
    with open(pickle_name) as f:
        all_models = pickle.load(f)

#get stellar masses
stel_data_asw, stel_data_sw = get_stellar_masses('stelmass/Rafael_salp.dat')

x = []
x_lo = []
x_hi = []
y = []
y_lo = []
y_hi = []


# only slect newest
if True:
    tmpp = {}
    for mid, adata in all_models.items():
        asw = adata['asw'] 
        dat = adata['created_on']
    
        if adata['Mtot_ens_ave_z_corrected'] == 0.0:
            continue
       
        if tmpp.has_key(asw):
            if tmpp[asw]['created_on'] < dat: # if current newer than previous
                tmpp[asw] = adata
        else:
            tmpp[asw] = adata
    
    selected_models = {}
    for asw, data in tmpp.items():
        selected_models[data['mid']] = data

else:
    selected_models = all_models       


for mid, adata in selected_models.items():
    
    asw = adata['asw']
    swid = adata['swid']
    print "gathering data:", swid, asw, mid
    
    if adata['Mtot_ens_ave_z_corrected'] == 0.0:
        continue
    
    Mtot_ave = adata['Mtot_ens_ave_z_corrected']
    Mtot_lo = Mtot_ave - adata['Mtot_min_z_corrected']
    Mtot_hi = adata['Mtot_max_z_corrected'] - Mtot_ave
    
    try:
        Mstel_ave, Mstel_err_lo, Mstel_err_hi, Mstel_jr, Mstel_sr = stel_data_sw[swid]
    except KeyError:
        continue
    
    x.append(Mstel_ave)
    x_lo.append(Mstel_err_lo)
    x_hi.append(Mstel_err_hi)
    
    y.append(Mtot_ave)
    y_lo.append(Mtot_lo)
    y_hi.append(Mtot_hi)

        
x = np.array(x)
x_lo = np.array(x_lo)
x_hi = np.array(x_hi)
y = np.array(y)
y_lo = np.array(y_lo)
y_hi = np.array(y_hi)

fig = plt.figure(figsize=(4.5,4), dpi=200)
ax = fig.add_subplot(111)

ax.plot([1e7,1e15],[1e7,1e15],'k:')

ax.errorbar(x, y, yerr=[y_lo, y_hi], color='b', xerr=[x_lo, x_hi],
            fmt='.', ecolor='r', capthick=1)

#axis limits
amin = 2e8
amax = 2e13

plt.title("Stellar vs Lensing Mass")
ax.set_xlabel('Stellar Mass $\mathrm{M_{\odot}}$')
ax.set_ylabel('Lensing Mass $\mathrm{M_{lens}}$')

ax.set_xscale("log", nonposx='clip')
ax.set_yscale("log", nonposy='clip')
ax.set_ylim(ymin=amin, ymax=amax)
ax.set_xlim(xmin=amin, xmax=amax)

plt.tight_layout()
fig.savefig('plot.png', dpi=1200)
#plt.show()
    

# analysis

#lenses with photometr. redshift in paper
l_zphot = [k for k, v in candidates.by['asw'].items() if v['z_lens']>0]

# those that are in the plot
l_used = [str(_) for _ in tmpp.keys()]

missing_l = []
for asw in l_zphot:
    swid = candidates.by['asw'][asw]['swid']
    if asw not in l_used:
        missing_l.append((asw, swid))

t = len(l_zphot)
s = len(tmpp.keys())
q = len(set([str(v['asw']) for k, v in all_models.items()]))
print 'report:'
print 'candidates in paper:', len(candidates.by['asw'])
print 'we have models for those many candidates', q
print 'candidates in paper with z_phot:', t
print 'from those: candidates that have a model and are in the plot:', s
print 'models missing:', t-s
for r in missing_l: print r


    