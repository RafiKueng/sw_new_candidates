# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 21:51:21 2015

@author: rafik
"""

import os
from os.path import join

import numpy as np
import matplotlib as mpl

mpl.rc('font', family='serif')
mpl.rc('text', usetex=True)

import matplotlib.pyplot as plt

from settings import settings as S, getI, INT

path     = join(S['output_dir'], 'plots')
filename = '{_[swid]}_{_[asw]}_{_[mid]}_mstel_vs_mtot.png'

if not os.path.exists(path):
    os.makedirs(path)

from create_data import ONLY_RECENT_MODELS as MODELS, LENS_CANDIDATES as LENSES
from parse_candidates import MAP as ASW2SWID, MAP as SWID2ASW

I = getI(__file__)

# create lookup dict asw -> mid
ASW2MID = dict( (str(v['asw']),k) for k,v in MODELS.items() )

# get all asw of the models (as set)
models_asws = set( ASW2MID.keys() )
# all asw of the candidates
lenses_asws = set( LENSES.keys())

# get an overview of how much data is missing
union = models_asws | lenses_asws     # aka OR (in a or in b)
intersect = models_asws & lenses_asws # aka AND (in A and B)
symdiff = models_asws ^ lenses_asws   # aka XOR (in a or in b but not in both)

print I,"status: total element:  %i / all data available for: %i" %(len(union), len(intersect))
print INT,"missing:"
for asw in symdiff:
    print INT,'-',asw
    

# collect data
M_stellar = []
M_lens = []
Label = []

data = {}

for asw in intersect:

    mid = ASW2MID[asw]
    swid = ASW2SWID[asw]
    
    m_stellar = LENSES[asw]['m_s_geom']
    m_lens = MODELS[mid]['Mtot_ave_z_corrected']
    m_lens_max = MODELS[ASW2MID[asw]]['Mtot_max_z_corrected']
    m_lens_min = MODELS[ASW2MID[asw]]['Mtot_min_z_corrected']
    
    label = '%s (%s)' % (swid, asw)
    
    M_stellar.append(m_stellar)
    M_lens.append(m_lens)
    Label.append(label)
    
    data[label] = {
        'm_stellar':m_stellar,
        'm_lens':m_lens,
    }

    data[label].update(LENSES[asw])
    data[label].update(MODELS[mid])
    
    
    

# make numpy arrays    
M_stellar = np.array(M_stellar)
M_lens = np.array(M_lens)
Label = np.array(Label)

print I,"begin plotting"

for i, _ in enumerate(data.items()):
    label, _ = _
    m_stellar = _['m_stellar']
    m_lens = _['m_lens']
    
    print INT,"(%3.0f%%) plotting %s..." % (100.0*i/len(data.keys()), label),
    
    # filename
    ffn = join(path, filename.format(_=_))
    if os.path.exists(ffn):
        print "exists, skipping (%s)" % ffn
        continue
    
    # setup plot
    fig = plt.figure(figsize=(4,4), dpi=200)
    ax = fig.add_subplot(111)
    
    # black line
    ax.plot([1e7,1e15],[1e7,1e15],'k:')
    ax.plot([1e7,1e15],[1e7,1e15],'k:')
    
    # brackground points
    g = 0.3 # gray
    ax.scatter(M_stellar, M_lens, c=(g,g,g), marker='+')
    
    # coloured point
    ax.plot(m_stellar, m_lens, 'or')
    
    #plt.title("Stellar vs Lensing Mass")
    plt.title(label)
    ax.set_xlabel('Stellar Mass $\mathrm{M_{\odot}}$')
    ax.set_ylabel('Lensing Mass $\mathrm{M_{lens}}$')
    
    #axis limits
    ax.set_xlim(xmin=2e8, xmax=1e12)
    ax.set_ylim(ymin=2e10, ymax=1e14)
    ax.set_xscale("log", nonposx='clip')
    ax.set_yscale("log", nonposy='clip')
    
    plt.tight_layout()
    fig.savefig(ffn, dpi=200)
    #plt.show()
    #break
    plt.clf()
    plt.close(fig)
    
    print "Done"
plt.close('all')

print I,"OVER AND OUT"

