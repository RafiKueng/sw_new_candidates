#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""

copy & paste & adapt from glass


Created on Tue Jul 26 18:24:18 2016

@author: rafik
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def default_kw(R, kw={}):
    kw.setdefault('extent', [-R,R,-R,R])
    kw.setdefault('interpolation', 'nearest')
    kw.setdefault('aspect', 'equal')
    kw.setdefault('origin', 'upper')
    kw.setdefault('fignum', False)
    kw.setdefault('cmap', cm.bone)
    #if vmin is not None: kw['vmin'] = vmin
    #if vmax is not None: kw['vmax'] = vmax
    return kw


# env().arrival_plot(env().ensemble_average, only_contours=True, colors='magenta', clevels=40)

def arrival_plot(model, ax):

    # obj_index       = kwargs.pop('obj_index', None)
    #src_index       = kwargs.pop('src_index', None)
    clevels         = 40
    xlabel          = r'arcsec'
    ylabel          = r'arcsec'
    
    kwargs = {'colors': 'magenta', 'clevels':40}

    
    # data loaded
    source_indices = [_.index for _ in obj.sources]
    arrival_contour_levels = obj.basis.arrival_contour_levels(data)
    arrival_grid = obj.basis.arrival_grid(data)
    #subdivision = obj.basis.subdivision
    mapextent = obj.basis.mapextent

    source_indices = model['source_indices']
    arrival_contour_levels = model['arrival_contour_levels']
    arrival_grid = model['arrival_grid']
    #subdivision = model['subdivision']
    mapextent = model['mapextent']

    
    #obj_slice = slice(None) if obj_index is None else obj_index

    #obj_slice = index_to_slice(obj_index)
    # src_slice = index_to_slice(src_index)
    #if src_index is not None:
        #assert 0, 'arrival_plot: src_index not yet supported'


    def plot_one(src_index,g,lev,kw):
        matplotlib.rcParams['contour.negative_linestyle'] = 'solid'

        if 'cmap' in kw: kw.pop('cmap')
        if clevels:
            loglev=clevels
            #loglev = logspace(1, log(g.ptp()), clevels, base=math.e) + amin(g)
            #loglev = 1 / logspace(1/ log(amax(g)-amin(g)), 1, clevels, base=math.e) + amin(g)
            #loglev = 1 / logspace(1/ log10(amax(g)-amin(g)), 1, clevels) + amin(g)
            kw.update({'zorder':-1000})
            ax.contour(g, loglev, **kw)
        if lev:
            kw.update({'zorder':1000})
            kw.update({'colors': 'k', 'linewidths':2, 'cmap':None})
            #kw.update({'colors':system_color(src_index), 'linewidths':3, 'cmap':None})
            ax.contour(g, lev, **kw)

    # for obj,data = model['obj,data'][obj_slice]:
    #obj,data = model['obj,data'][0]

    #if not data: continue

    # print len(obj.sources[src_slice])
    #lev = obj.basis.arrival_contour_levels(data)
    #print len(lev)
    #arrival_grid = obj.basis.arrival_grid(data)
    #for i,src in enumerate(obj.sources[src_slice]):
    for src_index in source_indices:

        if arrival_contour_levels:
            levels = arrival_contour_levels[src_index]
        g = arrival_grid[src_index]

        # S = obj.basis.subdivision
        # R = obj.basis.mapextent
        kw = default_kw(mapextent, kwargs)
        kw.update(kwargs)
        kw.setdefault('colors', 'grey')
        kw.setdefault('linewidths', 1)
        kw.setdefault('cmap', None)

        plot_one(src_index,g,levels,kw)
        plt.xlim(-mapextent, mapextent)
        plt.ylim(-mapextent, mapextent)

    plt.gca().set_aspect('equal')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    
    
def overlay_input_points(model, ax):
    '''adds the input points (min, max, sad, pmass) ontop of existing plot'''
  
    overlay_ext_pot = True
    
    obj, data = model['obj,data'][0]

    # data to load
    source_images = [ {'parity': img.parity, 'pos': img.pos} for img in obj.sources[0].images ]
    extra_potentials = [ {'r': _.r} for _ in obj.extra_potentials if isinstance(_, glass.exmass.PointMass) ]

    source_images = model['source_images']
    extra_potentials = model['extra_potentials']


    if overlay_ext_pot:
        for epot in extra_potentials:
            ax.plot([epot['r'].real], [epot['r'].imag], 'sy')
  
    for img in source_images:
        #['min', 'sad', 'max', 'unk'].index(parity)
        tp = ['c', 'g', 'r', 'm'][img.parity]
        ax.plot([img.pos.real], [img.pos.imag], 'o'+tp)

    #mark origin
    ax.plot([0], [0], 'or')

