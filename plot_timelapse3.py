#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 27 19:54:42 2017

@author: rafik
"""

import os
from os.path import join

# reminder: settings before mpl
import settings as SET
reload(SET)
SET.set_mpl_rc()
STY = SET.styles # for better reload() in ipython
S = SET.settings
from settings import getI, INT


import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import datetime as dt
from dateutil import parser


DBG = SET.DEBUG
#DBG = True


fpath    = join(S['output_dir'], 'timelapse')
filename = 'timelapse3.png'


if not os.path.exists(fpath):
    os.makedirs(fpath)

#from create_data import LENS_CANDIDATES as LENSES
import create_data as CRDA
#import parse_candidates  as PACA
#from parse_candidates import MAP as ASW2SWID   #, MAP as SWID2ASW
#

MODELS, MAPS = CRDA.get_dataset_data('all_models')
ALL_MODELS = CRDA.ALL_MODELS
from create_data import LENS_CANDIDATES as LENSES




Dates = {}
Hists = {}
HIST = {}

users = {}

#nBins = 3 * 365 * 24 * 60
#alle = np.zeros(nBins)
#alle2 = np.zeros(nBins)
#xx = np.arange(nBins)

START_DATE = dt.datetime(2013,1,1,0,0,0)

nnn = 2.66 * 365 * 24 * 60 * 60 # max value needed
res = 128  # subsampling..

xx = np.geomspace(1, 10**np.ceil(np.log10(nnn)), np.ceil(np.log10(nnn))*res+1)
xx = np.linspace(0, nnn, res)
nBins = len(xx)

alle = np.zeros(nBins)
alle2 = np.zeros(nBins)

alldates = []
by_users = {}

for swid in MAPS['swid2mids'].keys():
    #if swid == 'SW01': continue
    print swid
    dates = []   
    for mid in MAPS['swid2mids'][swid]:
        print "   ", mid
        M = ALL_MODELS[mid]
        date = (parser.parse(M['created_on']) - START_DATE).total_seconds()
        dates += [date,]
        u = M['user']
        if not u in users:
            users[u] = 0
            by_users[u] = []
        users[u] += 1
        by_users[u].append(date)

    dates = sorted(dates)
    #dates = map(parser.parse,dates)

#    if swid == "SW01":
#        dates = dates[1:] # remove prelim test of me

#    start = dt.datetime(2013,3,1,0,0,0)
    dates = np.array(dates)
    
#    deltas = dates - start
    deltas = dates
    
    #l = [_.days for _ in deltas]
    #l = [int(_.total_seconds()) for _ in deltas] # count in hours
    #hist = np.array(sorted([[x,l.count(x)] for x in set(l)]))

    Dates[swid] = dates
    Hists[swid] = dates

    alldates.extend(dates)
    
ncand = len(Dates.keys())

#np.array(alldates)[:,0]


#fig = plt.figure(**STY['figure_rect_med'])
#ax1 = fig.add_subplot(2,1,1)
#ax2 = fig.add_subplot(2,1,2,sharex=ax1)
#

plot_users = False
#plot_users = True

if plot_users:
    fig, axes = plt.subplots(2, 1, sharex=True, **STY['figure_rect_med'])
    ax1, ax2, ax3 = axes
else:
    fig, axes = plt.subplots(1, 1, sharex=True, **STY['figure_rect_med'])
    ax1 = axes
    ax2 = None
    ax3 = None

#fig.subplots_adjust(hspace=0)

a, b = np.histogram( np.array(alldates), xx)
ax1.step( xx[:-1]/60/60/24, np.cumsum(a), color='k', linestyle='-', linewidth=3, label="all")
#ax1.fill_between(xx[:-1]/60/60/24, np.cumsum(a), color='lightgray', step='pre')

for swid, h in sorted(Hists.items()):
    if swid not in ['SW01','SW05','SW20','SW29', 'SW45']:
        continue
       
    a, b = np.histogram( np.array(h), xx)
#    if swid == 'SW01':
#        a /= 3
    ax1.step(xx[:-1]/60/60/24, np.cumsum(a), label=swid)
#    ax1.step(xx[:-1]/60/60/24, a)

ax1.set_yscale('log')

#plt.show()

if ax3:
    for user, lst in by_users.items():
        if len(lst) < 5:
            continue
        a, b = np.histogram( np.array(lst), xx)
        ax3.step(xx[:-1]/60/60/24, a, label="$%s$" % user)
    
    ax3.legend()
    
ax1.legend()

ax1.set_xlabel("days since %s" % START_DATE.strftime("%b %d %Y"))
#ax1.set_ylabel("total number\nof models")
ax1.set_ylabel("number of models")

plt.tight_layout()

imgname = join(fpath, filename)
plt.savefig(imgname, **STY['figure_save'])
plt.show()
plt.close('all')
    
#    for i,v in hist:
#        if i==0: i=1
#        b = res * np.int(np.round(np.log2(i)))
#        alle[b] += v
#        
#    if not swid == 'SW01':
#        for i,v in hist:
#            if i==0: i=1
#            b = res * np.int(np.round(np.log2(i)))
#            alle[b] += v
#    
#    
#for k,v in Hists.items():
#    HIST[k] = np.zeros(nBins)
#    for i,j in v:
#        if i==0: i=1
#        b = np.int(np.round(np.log2(i)))
#        HIST[k][b] += j
#
##    plt.step(hist[:,0]+1, np.cumsum(hist[:,1]))
##
##plt.xscale('log')
##plt.show()
#
#fig = plt.figure(**STY['figure_rect_med'])
#ax = fig.add_subplot(1,1,1)
#
#
#for i in [1, 60, 60*24, 60*24*7, 60*24*30, 60*24*365, 60*24*365*2]:
#    ax.axvline(i, color='lightgray')
#ax.axvline(61000, color='darkgray', linestyle='--') # modelling challenge
#
#
#ax.step(np.arange(nBins), np.cumsum(alle), label='all')
##ax.step(np.arange(nBins), np.cumsum(alle2), label='excl. SW01')
#
#
##dict([ (k, np.sum(v)) for k,v in  HIST.items() ])
#
#stacked = []
#lbls = []
#for swidd in [1,5,20,29,45]:
#    swid = "SW%02i" % swidd
#    #ax.fill_between(np.arange(nBins), np.cumsum(HIST[swid]), 0, label=swid)
#    stacked.append(np.cumsum(HIST[swid]))
#    lbls.append(swid)
#
#rstacked = np.row_stack(reversed(stacked))
#ax.stackplot(xx, rstacked, labels=reversed(lbls))
#
#
#
#
#handles, labels = ax.get_legend_handles_labels()
#ax.legend(handles[::-1], labels[::-1])
#
#
#ax.set_xlabel("Time since first model [min]")
#ax.set_ylabel("Total number of models [1]")
##ax.legend()
#
#ax.set_xscale('log')
#ax.set_yscale('log')
#
##ax.set_ylim([50,375])
#plt.tight_layout()
##plt.show()
#
#imgname = join(fpath, filename)
#plt.savefig(imgname, **STY['figure_save'])
#
#print users
#
#users_cleaned = {
#    u'Budgieye': 14,
#    u'Capella05': 47,
#    u'ElisabethB': 32,
#    u'KhalilaRedBird': 3,
#    u'Lucy': 26,
#    u'Phil': 6,
#    u'Tom Collett': 1,
#    u'c_cld': 183,
#    u'jasonjason': 13,
#    u'jon273': 2,
#    u'psaha': 23,
#    u'psrk': 2,
#    u'rafik': 3,
#    u'[anon]': 1
#}
#
#count = 0
#for k,v in users_cleaned.items():
#    if v >=5:
#        count += 1
#print "we got n major contributors:", count    
#    
#
##plt.close('all')
#

