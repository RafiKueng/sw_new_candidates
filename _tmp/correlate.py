# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 16:45:27 2015

@author: rafik
"""
import os
import sys
import cPickle as pickle
import numpy as np
import matplotlib as mpl
import webbrowser

mpl.rc('font', family='serif')
mpl.rc('text', usetex=True)

import matplotlib.pyplot as plt

import candidates
from stelmass.stelpops2 import get_stellar_masses

from get_ratings import ratings


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

categories = []


# only slect newest
if False:
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


# filter models 
if True:
    cml_sel_models = []
    print "scanning args:"
    for i,arg in enumerate(sys.argv):
        print arg
        if i>0:
            cml_sel_models.append(arg)
    if len(cml_sel_models)>0:
        tmpp={}
        for mid, data in selected_models.items():
            if data['asw'] in cml_sel_models:
                tmpp[mid] = data
                
        selected_models = tmpp
    
    



urlss = []

asws = []
swids = []

with open("selected_models.txt", "w") as f:
    for mid, adata in selected_models.items():
        
        asw = adata['asw']
        swid = adata['swid']
        print "gathering data: %s %s %10s" % (swid, asw, mid) ,
        
        # print 
        if len("%s"%mid)<6:
            urll = "http://mite.physik.uzh.ch/data/%06i" % int(mid)
        else:
            urll = "http://labs.spacewarps.org/spaghetti/model/" + mid
        f.write("         %s %s %10s %s\n" % (swid, asw, mid, urll))
        urlss.append((urll,"%s %10s %s"%(swid, asw, mid)))
        
        if adata['Mtot_ens_ave_z_corrected'] == 0.0:
            print "SKIP"
            continue
        
        Mtot_ave = adata['Mtot_ens_ave_z_corrected']
        Mtot_lo = Mtot_ave - adata['Mtot_min_z_corrected']
        Mtot_hi = adata['Mtot_max_z_corrected'] - Mtot_ave
        
        try:
            Mstel_ave, Mstel_err_lo, Mstel_err_hi, Mstel_jr, Mstel_sr = stel_data_sw[swid]
        except KeyError:
            print "SKIP"
            continue
        
        try:
            rat = ratings[asw]
        except:
            rat = None
        #print rat
        # depending on rating, assign a category
        if rat is None:
            cat = 0
        elif rat==-1:
            cat = 1
        elif rat==0:
            cat = 2
        elif rat>0:
            cat = 3
        print cat
        
        x.append(Mstel_ave)
        x_lo.append(Mstel_err_lo)
        x_hi.append(Mstel_err_hi)
        
        y.append(Mtot_ave)
        y_lo.append(Mtot_lo)
        y_hi.append(Mtot_hi)

        categories.append(cat)
        asws.append(asw)
        swids.append(swid)

categories = np.array(categories)
#colormap = np.array(['y', 'r', 'g', 'b'])
f = 0.6
colormap = np.array([[1,1,f], [1,f,f], [f,1,f], [f,f,1]])
        
x = np.array(x)
x_lo = np.array(x_lo)
x_hi = np.array(x_hi)
y = np.array(y)
y_lo = np.array(y_lo)
y_hi = np.array(y_hi)

fig = plt.figure(figsize=(4.5,4), dpi=200)
ax = fig.add_subplot(111)

ax.plot([1e7,1e15],[1e7,1e15],'k:')
ax.plot([1e7,1e15],[1e7,1e15],'k:')

for i, _x in enumerate(x):
    _y = [y[i]]
    _y_lo = [y_lo[i]]
    _y_hi = [y_hi[i]]
    _cat = categories[i]
    _x_lo = [x_lo[i]]
    _x_hi = [x_hi[i]]
    
#    ax.errorbar(_x, _y, yerr=[_y_lo, _y_hi], c=colormap[_cat], xerr=[_x_lo, _x_hi],
#            fmt='.', ecolor='k', capthick=0.5)
    ax.scatter(_x, _y, c=colormap[_cat])

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
fig.savefig('plot.png', dpi=200)
#plt.show()
    

## analysis
#
##lenses with photometr. redshift in paper
#l_zphot = [k for k, v in candidates.by['asw'].items() if v['z_lens']>0]
#
## those that are in the plot
#l_used = [str(_) for _ in selected_models.keys()]
#
#missing_l = []
#for asw in l_zphot:
#    swid = candidates.by['asw'][asw]['swid']
#    if asw not in l_used:
#        missing_l.append((asw, swid))
#
#t = len(l_zphot)
#s = len(tmpp.keys())
#q = len(set([str(v['asw']) for k, v in all_models.items()]))
#print 'report:'
#print 'candidates in paper:', len(candidates.by['asw'])
#print 'we have models for those many candidates', q
#print 'candidates in paper with z_phot:', t
#print 'from those: candidates that have a model and are in the plot:', s
#print 'models missing:', t-s
#for r in missing_l: print "  >",r
#
#
##for u,s in urlss:
##    print "working on:", s,"...",
##    webbrowser.open(u)
##    raw_input(">")