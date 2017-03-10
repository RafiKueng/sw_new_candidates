# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 21:51:21 2015

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
from matplotlib.patches import Rectangle

from moster import moster


DBG = SET.DEBUG
#DBG = True


path     = join(S['output_dir'], 'mlens_vs_mstel_one')
filename = 'mstel_vs_mtot_one.png'
overwrite = True

#areastyle = styles['forbiddenarea']
#fgmarker = styles['hilight_marker']
#bgmarker = styles['background_marker']

if not os.path.exists(path):
    os.makedirs(path)

#from create_data import ONLY_RECENT_MODELS as MODELS, LENS_CANDIDATES as LENSES
from create_data import LENS_CANDIDATES as LENSES
import create_data as CRDA
from parse_candidates import MAP as ASW2SWID   #, MAP as SWID2ASW


SUBSET_MODELS, MAPS = CRDA.get_dataset_data('selected_models')
ALL_MODELS = CRDA.ALL_MODELS

I = getI(__file__)

# create lookup dict asw -> mid
# ASW2MID = dict( (str(v['asw']),k) for k,v in ALL_MODELS.items() )
ALL_MODELS_ASWS = set(sorted([str(__['asw']) for _, __ in ALL_MODELS.items()]))

# get all asw of the models (as set)
models_asws = ALL_MODELS_ASWS #set( ASW2MID.keys() )
# all asw of the candidates
lenses_asws = set( LENSES.keys())

# get an overview of how much data is missing
union     = models_asws | lenses_asws   # aka OR (in a or in b)
intersect = models_asws & lenses_asws   # aka AND (in A and B)
symdiff   = models_asws ^ lenses_asws   # aka XOR (in a or in b but not in both)

print I,"status: total element:  %i / all data available for: %i" %(len(union), len(intersect))
print INT,"missing:"
for asw in symdiff:
    print INT,'-',asw
    
if DBG:
    intersect = ['ASW0007k4r','ASW0008swn']


# collect data
M_stellar = []
M_lens = []
Label = []

data = {}

for asw in intersect:

    swid = ASW2SWID[asw]
    mids = MAPS['swid2mids'].get(swid, "")  # hack we only want the first entry of the list
    
    if not len(mids) > 0:
        print "did not find", asw, swid
        continue
    mid = mids[0]
    _m   = ALL_MODELS[mid]
    
    try:
        m_stellar  = LENSES[asw]['m_s_geom']
        m_lens     = _m['M(<R)']['data'][-1]
        m_lens_max = _m['M(<R)']['max'][-1]
        m_lens_min = _m['M(<R)']['min'][-1]
        m_rcf      = _m['sig_fact']          # corrects masses for wrong redshifts

    except KeyError:
        print "data for %s not found !!!!!" % asw
        exit(1)
    
    label = '%s (%s)' % (swid, asw)
    
    data[label] = {
        'm_stellar':  m_stellar,
        'm_lens':     m_lens     * m_rcf,
        'm_lens_max': m_lens_max * m_rcf,
        'm_lens_min': m_lens_min * m_rcf
    }

    data[label].update(LENSES[asw])
    data[label].update(ALL_MODELS[mid])
    
    

print I,"begin plotting"

    
#print INT,"(%3.0f%%) plotting %s..." % (100.0*i/len(data.keys()), label),

# filename
ffn = join(path, filename)
if os.path.exists(ffn) and not overwrite:
    print "exists, skipping (%s)" % ffn
    #continue

# setup plot
fig = plt.figure(**STY['figure_sq_big'])
ax = fig.add_subplot(111)

# plot range for additional stuff
# make sure it's outside the plot range
rng_max = 1e15
rng_min = 1e7
rng_n = 50
rng = np.array([rng_min,rng_max])
rng_lin = np.linspace(rng_min, rng_max, rng_n)
rng_log = np.logspace(np.log10(rng_min), np.log10(rng_max), rng_n)

# plot moster area
most = moster(rng_log)
ax.fill_between(most, rng_log, rng_max, **STY['bg_area'])
#ax.plot(most, rng_log,'k:')

# black line
#ax.plot(rng,rng,'k:')
ax.fill_between(rng_log, rng_log, rng_min, **STY['bg_area2'])


# brackground points
kw={}
kw.update(STY['fg_marker2'])
kw.pop('facecolor', None)
#ax.plot(M_stellar, M_lens, **kw)
 
   
for i, _ in enumerate(data.items()):
    label, _ = _
    swid = _['swid']
    #if swid[2:4] in ['05', '42', '28', '58', '02','19','09','29','57']: continue
    if swid in SET.HILIGHT_SWID: continue


    m_stellar = _['m_stellar']
    m_stellar_min = _['m_s_jr']
    m_stellar_max = _['m_s_sr']
    m_lens = _['m_lens']
    m_lens_max = _['m_lens_max']
    m_lens_min = _['m_lens_min'] 

    # draw rectangle as error area
    lowleft = (m_stellar_min, m_lens_min)
    width   = m_stellar_max-m_stellar_min
    height  = m_lens_max-m_lens_min
    ax.add_patch(Rectangle(lowleft, width, height, **STY['err_area2']))

    
for i, _ in enumerate(data.items()):
    label, _ = _
    swid = _['swid']
    #if swid[2:4] not in ['05', '42', '28', '58', '02','19','09','29','57']: continue
    if swid not in SET.HILIGHT_SWID: continue

    m_stellar = _['m_stellar']
    m_stellar_min = _['m_s_jr']
    m_stellar_max = _['m_s_sr']
    m_lens = _['m_lens']
    m_lens_max = _['m_lens_max']
    m_lens_min = _['m_lens_min']

    # coloured point
    #ax.plot(m_stellar, m_lens, **fgmarker)
    
#    yerr = np.array([[m_lens-m_lens_min], [m_lens_max-m_lens]])
#    if DBG:
#        yerr = 5*yerr
#    STY['fg_marker1'].pop('facecolor', None)
#    ax.errorbar(m_stellar, m_lens, yerr=yerr, **STY['fg_marker1'])

    # draw rectangle as error area
    lowleft = (m_stellar_min, m_lens_min)
    width   = m_stellar_max-m_stellar_min
    height  = m_lens_max-m_lens_min
    ax.add_patch(Rectangle(lowleft, width, height, **STY['err_area1']))
    
    
    #ax.annotate('%s' % swid, xy=(m_stellar,m_lens), textcoords='data', size="x-small")
    ax.annotate('%s' % swid,
                xy=(m_stellar,m_lens),
                ha='center',
                va='center',
                #xytext=(3,1),
                #textcoords='offset points',
                #size="x-small",
                zorder=100)
    
#plt.title("Stellar vs Lensing Mass")
#plt.title(label)
#ax.set_xlabel('Stellar Mass $M_{stel}$ [ $\log ( 10^{-10} M_{\odot} )$ ]', **STY['label'])
#ax.set_ylabel('Lensing Mass $M_{lens}$ [ $\log ( 10^{-10} M_{\odot} )$ ]', **STY['label'])
#ax.set_xlabel('Stellar Mass $M_{stel}$ [ $10^{10} M_{\odot}$ ]', **STY['label'])
#ax.set_ylabel('Lensing Mass $M_{lens}$ [ $10^{12} M_{\odot}$ ]', **STY['label'])
ax.set_xlabel('Stellar Mass $M_{stel}$ [ $M_{\odot}$ ]', **STY['label'])
ax.set_ylabel('Lensing Mass $M_{lens}$ [ $M_{\odot}$ ]', **STY['label'])

#axis limits
ax.set_xlim(xmin=2.5e8, xmax=9.5e11)
ax.set_ylim(ymin=2.5e10, ymax=9.5e13)

ax.set_xscale("log", nonposx='clip')
ax.set_yscale("log", nonposy='clip')


# recale the ticks
scalex = 10**10
scaley = 10**12
#ticks_rescaled = mpl.ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(np.log10(x/scale)))
#ticks_rescaledx = mpl.ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x/scalex))
#ticks_rescaledy = mpl.ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x/scaley))
ticks_rescaledx = mpl.ticker.FuncFormatter(lambda _, pos: '$10^{{{0:g}}}$'.format(np.log10(_)))
ticks_rescaledy = mpl.ticker.FuncFormatter(lambda _, pos: '$10^{{{0:g}}}$'.format(np.log10(_)))
ax.xaxis.set_major_formatter(ticks_rescaledx)
ax.yaxis.set_major_formatter(ticks_rescaledy)


ax.tick_params(**STY['big_majorticks'])
ax.tick_params(**STY['big_minorticks'])

plt.tight_layout()
fig.savefig(ffn, **STY['figure_save'])

if DBG:
    plt.show()

plt.clf()
plt.close(fig)

print "Done"
plt.close('all')

print I,"OVER AND OUT"

