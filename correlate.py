# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 16:45:27 2015

@author: rafik
"""
import os
import cPickle as pickle
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from stelmass.stelpops2 import get_stellar_masses

pickle_name = 'all_data.pickle'

#
#
#
#def load_all_models():
#    models_asw = {}
#    models_sw = {}
#    all_models_asw = {}
#    all_models_sw = {}
#    
#    with open('all_candidates_data.csv') as f:
#        for line in f.readlines():
#            tkns = line[:-1].split(',')
#            
#            #skip header
#            try:
#                i = int(tkns[0])
#            except:
#                continue
#            
#            asw = tkns[2]
#            swid = tkns[3]
#            
#            #this only uses the latest model
#            models_asw[asw] = tkns
#            models_sw[swid] = tkns
#            
#            # this uses all models
#            if al_models_asw.has_key(asw):
#                all_models_asw[asw].append(tkns)
#                all_models_sw[swid].append(tkns)
#            else:
#                all_models_asw[asw] = [tkns,]
#                all_models_sw[swid] = [tkns,]
#            
#           
#    #return models_asw, models_sw
#    return all_models_asw, all_models_sw
#



#
#data_asw, data_sw = get_stellar_masses('stelmass/Rafael_salp.dat')
#models_asw, models_sw = load_all_models()
#
#coll_data = []
#
#x1 = []
#x2 = []
#y = []
#
#for swid, vals in data_sw.items():
#
#    if vals[0] == 0:
#        continue
#    
#    stel_mass1 = vals[0]
#    stel_mass2 = vals[1]
#
#    for model in models_sw[swid]:
#        try:
#            tot_mass = model[9]
#            tot_mass_lo = 
#        except KeyError:
#            continue
#        
#        

#    try:
#        tot_mass = models_sw[swid][9]
#        stel_mass1 = vals[0]
#        stel_mass2 = vals[1]
#    except KeyError:
#        continue
#    x1.append(stel_mass1)
#    x2.append(stel_mass2)
#    y.append(tot_mass)



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

for mid, adata in all_models.items():
    
    asw = adata['asw']
    swid = adata['swid']
    
    if adata['Mtot_ens_ave_z_corrected'] == 0.0:
        continue
    
    Mtot_ave = adata['Mtot_ens_ave_z_corrected']
    Mtot_lo = 0.0
    Mtot_hi = 0.0
    
    try:
        Mstel_ave, Mstel_lo, Mstel_hi = stel_data_sw[swid]
    except KeyError:
        continue
    
    x.append(Mstel_ave)
    x_lo.append(Mstel_ave - Mstel_lo)
    x_hi.append(Mstel_hi - Mstel_ave)
    
    y.append(Mtot_ave)

        
x = np.array(x)
x_lo = np.array(x_lo)
x_hi = np.array(x_hi)
y = np.array(y)

ax = plt.subplot(111)

ax.plot([1e7,1e15],[1e7,1e15],'k:')

ax.errorbar(x, y, yerr=[x_lo*0, x_lo*0], xerr=[x_lo, x_hi],
            fmt='o', ecolor='g', capthick=1)

#axis limits
amin = 1e8
amax = 1e13

ax.set_xscale("log", nonposx='clip')
ax.set_yscale("log", nonposy='clip')
ax.set_ylim(ymin=amin, ymax=amax)
ax.set_xlim(xmin=amin, xmax=amax)

plt.show()
    
    
    