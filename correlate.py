# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 16:45:27 2015

@author: rafik
"""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from stelmass.stelpops2 import bla

def load_all_models():
    models_asw = {}
    models_sw = {}
    all_models_asw = {}
    all_models_sw = {}
    
    with open('all_candidates_data.csv') as f:
        for line in f.readlines():
            tkns = line[:-1].split(',')
            
            #skip header
            try:
                i = int(tkns[0])
            except:
                continue
            
            asw = tkns[2]
            swid = tkns[3]
            
            #this only uses the latest model
            models_asw[asw] = tkns
            models_sw[swid] = tkns
            
            # this uses all models
            if al_models_asw.has_key(asw):
                all_models_asw[asw].append(tkns)
                all_models_sw[swid].append(tkns)
            else:
                all_models_asw[asw] = [tkns,]
                all_models_sw[swid] = [tkns,]
            
           
    #return models_asw, models_sw
    return all_models_asw, all_models_sw





data_asw, data_sw = bla('stelmass/Rafael_salp.dat')
models_asw, models_sw = load_all_models()

coll_data = []

x1 = []
x2 = []
y = []

for swid, vals in data_sw.items():

    if vals[0] == 0:
        continue
    
    stel_mass1 = vals[0]
    stel_mass2 = vals[1]

    for model in models_sw[swid]:
        try:
            tot_mass = model[9]
        except KeyError:
            continue
        
        

#    try:
#        tot_mass = models_sw[swid][9]
#        stel_mass1 = vals[0]
#        stel_mass2 = vals[1]
#    except KeyError:
#        continue
#    x1.append(stel_mass1)
#    x2.append(stel_mass2)
#    y.append(tot_mass)
    
x1 = np.array(x1)
x2 = np.array(x2)
y = np.array(y)

plt.loglog(x1,y, 'ro')
plt.loglog(x2,y, 'bo')
plt.xlim([1e8, 1e13])
plt.ylim([1e8, 1e13])
plt.show()
    
    
    