# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 20:37:05 2016

@author: rafik
"""

import os
import sys
import logging

import numpy as np
import scipy as sp
import scipy.misc
import matplotlib as mpl
import matplotlib.pyplot as plt

import parse_candidates as PACA
import create_data as CRDA
import get_state_and_config as GSAC # import will trigger download!
import download_orginals as DORG # import triggers download

_ = GSAC.I + DORG.I
del _

import settings as _S
from settings import settings as S, INT, save_pickle, load_pickle, save_csv
from settings import print_first_line, print_last_line, getI, del_cache


log = logging.getLogger(__name__)
if len(log.handlers) ==0:
    log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

log.debug("init logging")

CRDA.ONLY_RECENT_MODELS
CRDA.ALL_MODELS

_path = _S.sworg_path
_fn = "%s.png" # placeholder is asw name, should be the same as in DORG!


data = ['ASW0007k4r']




class RectCoords(object):
    
    def __init__(self):
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        
    @property
    def xlim(self):
        return (self.x1, self.x0)

    @property
    def ylim(self):
        return (self.y0, self.y1)
        
    @property
    def width(self):
        return self.x1 - self.x0

    @property
    def height(self):
        return self.y1 - self.y0

    def shift_to(self, x, y):
        cx = (self.x0 + self.x1)/2.
        cy = (self.y0 + self.y1)/2.
        
        dx = x-cx
        dy = y-cy
        
        self.x0 += dx
        self.y0 += dy
        self.x1 += dx
        self.y1 += dy
        
    def zoom(self, f):
        dx = self.width  * f
        dy = self.height * f
        self.x0 -= dx
        self.y0 -= dy
        self.x1 += dx
        self.y1 += dy
        


_rectspec_pos = {
    'edgecolor': 'g',
    'facecolor': None,
    'fill': False,
    'linewidth': 3.0       
}
_rectspec_neg = {
    'edgecolor': 'r',
    'facecolor': "r",
    'alpha' : 0.5,
    'linewidth': 3.0       
}

class MasksHandler(object):
    
    def __init__(self, ax=None):

        self.ax = ax if ax is not None else plt.gca()
        
        self.patch = None # holds the current rect
        self.c = None
        self.patchdata = {}

        self.patches = [] # holds a list of all tects
        
        self.add_rect()
        
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self.on_move)
        # self.ax.figure.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.ax.figure.canvas.mpl_connect('key_release_event', self.on_key_release)


    def add_rect(self, t='incl'):

        # set edge color depending on type
        if t=='incl':
            ec = _rectspec_pos
        elif t=='excl':
            ec = _rectspec_neg
        
        self.c = RectCoords()
        self.patch = mpl.patches.Rectangle((0,0), 1, 1, **ec)
        self.patchdata = {'type':t}
        
        self.patches.append((self.c, self.patch, self.patchdata))
        self.ax.add_patch(self.patch)
        self.ax.figure.canvas.draw()

    def remove_rect(self):
        log.debug("removing last rect and selecting second last")
        c, patch, patchdata = self.patches.pop()
        patch.remove()
        del c, patchdata, patch
        
        if len(self.patches)>=1:
            self.c, self.patch, self.patchdata = self.patches[-1]
        else:
            self.add_rect()
        self.ax.figure.canvas.draw()
        
    def select_rect(self, i):
        log.debug("selecting rect %i", i)
        if len(self.patches)>=i:
            self.c, self.patch, self.patchdata = self.patches[0]

    def update_patch(self):
        self.patch.set_width(self.c.width)
        self.patch.set_height(self.c.height)
        self.patch.set_xy((self.c.x0, self.c.y0))
        self.ax.figure.canvas.draw()


    def on_key_release(self, event):
        log.debug('keypress (%s)', event.key)
        
        if event.key=="+":
            self.add_rect('incl')

        elif event.key=="-":
            self.add_rect('excl')
        
        elif event.key=="enter":
            self.remove_rect()
        
        else:
            try:
                i = int(event.key)
            except:
                return
            self.select_rect(i)
            
        

    def on_press(self, event):
        log.debug( 'mouse btn press (%s %s %s)', event.inaxes, event.button, event.key)
        if event.inaxes == self.ax:
            if event.button == 1:
                self.c.x0 = event.xdata
                self.c.y0 = event.ydata


    def on_move(self, event):
        if event.inaxes == self.ax:
            
            if event.button==1:
                log.debug( 'mouse move (%s %s %s)', event.inaxes, event.button, event.key)
                if self.c.x0 is None:
                    log.warn("use rightclick to first create a rect before moving it")
                    return

                self.c.x1 = event.xdata
                self.c.y1 = event.ydata
                self.update_patch()



_zoomrectspec = {
    'edgecolor': 'y',
    'facecolor': None,
    'fill': False,
    'linewidth': 1.0       
}

class ZoomHandler(object):
    def __init__(self, ax1, ax2):
        
        self.ax1 = ax1 
        self.ax2 = ax2 # the ax that shows the zoomed window
        
        log.debug( "ax1: %s ax2 %s", ax1, ax2)
        
        self.c = RectCoords()
        
        self.quadratic = False
        
        self.rect = mpl.patches.Rectangle((0,0), 1, 1, **_zoomrectspec)
        self.ax1.add_patch(self.rect)
        
        self.ax1.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.ax1.figure.canvas.mpl_connect('motion_notify_event', self.on_move)

        self.ax1.figure.canvas.mpl_connect('scroll_event', self.on_scroll)

        self.ax1.figure.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.ax1.figure.canvas.mpl_connect('key_release_event', self.on_key_release)


    def update_rect(self):
        self.rect.set_width(self.c.width)
        self.rect.set_height(self.c.height)
        self.rect.set_xy((self.c.x0, self.c.y0))
        self.ax1.figure.canvas.draw()
        self.update_zoomed_view()

    def update_zoomed_view(self):
        self.ax2.set_xlim(self.c.xlim)
        self.ax2.set_ylim(self.c.ylim)
        self.ax2.figure.canvas.draw()

    def on_key_press(self, event):
        log.debug('keypress (%s)', event.key)
        if event.inaxes == self.ax1:
            if event.key == "control":
                self.quadratic = True
    
    def on_key_release(self, event):
        log.debug( 'keyrelease (%s)', event.key)
        if event.inaxes == self.ax1:
            if event.key == "control":
                self.quadratic = False

    def on_press(self, event):
        log.debug( 'btn press (%s %s)', event.inaxes, event.button)
        if event.inaxes == self.ax1:
            if event.button == 1: #left: set middle
                pass
            
            elif event.button == 3: # right button: draw area
                self.c.x0 = event.xdata
                self.c.y0 = event.ydata
                
    def on_move(self, event):
        if event.inaxes == self.ax1:
            ex = event.xdata
            ey = event.ydata
                
            if event.button == 1: #left: set middle
                log.debug( 'mouse move (%s %s %s)', event.inaxes, event.button, event.key)
                if self.c.x0 is None:
                    log.warn("use rightclick to first create a rect before moving it")
                    return
                self.c.shift_to(ex, ey)
                self.update_rect()
                
            elif event.button == 3: # right button: draw area
                log.debug( 'mouse move (%s %s %s)', event.inaxes, event.button, event.key)
                if self.quadratic:
                    dx = ex - self.c.x0
                    dy = ey - self.c.y0
                    dd = max(abs(dx),abs(dy))
                    ex = self.c.x0 + dd * np.sign(dx)
                    ey = self.c.y0 + dd * np.sign(dy)
                self.c.x1 = ex
                self.c.y1 = ey
                self.update_rect()


    def on_scroll(self, event):
        log.debug('scroll (%s %s %s)', event.inaxes, event.button, event.key)
        if event.inaxes == self.ax1:
                
            if event.button == 'up':
                print "up"
                self.c.zoom(0.1)
                self.update_rect()
                
            elif event.button == 'down':
                print "up"
                self.c.zoom(-0.1)
                self.update_rect()
            



for asw in data:
    
    orgimg_path = os.path.join(_path, _fn%asw)
    if not os.path.isfile(orgimg_path):
        DORG.download_from_spacewarps(asw)
    
    orgimg = sp.misc.imread(orgimg_path)
    
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 3, 1)
    ax2 = fig.add_subplot(1, 3, 2)
    ax3 = fig.add_subplot(1, 3, 3)

    mpl_img1 = ax1.imshow(orgimg)
    mpl_img2 = ax2.imshow(orgimg)
    
    h_z = ZoomHandler(ax1,ax2)
    h_a = MasksHandler(ax2)
    fig.show()
    
    fig.canvas.draw()


    #fig.close()

### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)
    
print_last_line(I)
