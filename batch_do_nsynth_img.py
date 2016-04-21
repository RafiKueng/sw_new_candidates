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
mpl.use('Qt4Agg') 
import matplotlib.pyplot as plt
import matplotlib.widgets

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
    
    def __init__(self, x0=None,y0=None,x1=None,y1=None):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        
    def __repr__(self):
        return "RectCoords((%4i/%4i) to (%4i/%4i))" % (self.x0, self.y0, self.x1, self.y1)
        
    @property
    def as_array(self):
        return np.array([self.x0, self.y0, self.x1, self.y1])

    @property
    def xlim(self):
        return (self.x0, self.x1)

    @property
    def ylim(self):
        return (self.y0, self.y1)

    @property
    def ylim_r(self):
        return (self.y1, self.y0)
        
    @property
    def slice2D(self):
        y0=int(round(self.y0))
        y1=int(round(self.y1))
        x0=int(round(self.x0))
        x1=int(round(self.x1))
        
        xx0 = min(x0,x1)
        xx1 = max(x0,x1)
        yy0 = min(y0,y1)
        yy1 = max(y0,y1)
        
        return np.s_[yy0:yy1, xx0:xx1]

    @property
    def slice3D(self):
        s2d = self.slice2D
        return s2d + (np.s_[:],)
        
    @property
    def width(self):
        return abs(self.x1 - self.x0)

    @property
    def height(self):
        return abs(self.y1 - self.y0)

    @property
    def dx(self):
        return self.x1 - self.x0

    @property
    def dy(self):
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
        self.update_handler = []
        self.register(self.selfupdate)
        
        self.patch = None # holds the current rect
        self.c = None
        self.patchdata = {}

        self.patches = [] # holds a list of all tects
        
        self.add_rect()
        
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self.on_move)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)
        # self.ax.figure.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.ax.figure.canvas.mpl_connect('key_release_event', self.on_key_release)


    def register(self, h):
        self.update_handler.append(h)
        
    def update(self):
        log.debug("Masks update")
        for h in self.update_handler:
            h()

    def selfupdate(self):
        self.patch.set_width(self.c.dx)
        self.patch.set_height(self.c.dy)
        self.patch.set_xy((self.c.x0, self.c.y0))
        
        self.ax.figure.canvas.draw()
#        self.ax.draw_artist(self.patch)
#        for patch in self.patches:
#            print patch[1]
#            self.ax.draw_artist(patch[1])

    def save(self):
        D = []
        for c,p,d in self.patches:
            D.append((c.as_array, d))
        return D
        
    def load(self, D):
        
        for ca, d in D:
            self.add_rect(d['type'], RectCoords(*ca), d)
            
        self.selfupdate()
            

    def add_rect(self, t='incl', c=RectCoords(0,0,0,0), patchdata=None):

        # set edge color depending on type
        if t=='incl':
            ec = _rectspec_pos
        elif t=='excl':
            ec = _rectspec_neg
        
        self.c = c
        self.patch = mpl.patches.Rectangle((0,0), 1, 1, **ec)
        if patchdata:
            self.patchdata = patchdata
        else:
            self.patchdata = {'type':t}
        
        self.patches.append((self.c, self.patch, self.patchdata))
        self.ax.add_patch(self.patch)
        #self.selfupdate()

    def remove_rect(self):
        log.debug("removing last rect and selecting second last")
        c, patch, patchdata = self.patches.pop()
        patch.remove()
        del c, patchdata, patch
        
        if len(self.patches)>=1:
            self.c, self.patch, self.patchdata = self.patches[-1]
        else:
            self.add_rect()
        self.update()
        
    def select_rect(self, i):
        log.debug("selecting rect %i", i)
        if len(self.patches)>=i:
            self.c, self.patch, self.patchdata = self.patches[0]


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
                #self.update_patch()
                self.selfupdate()

    def on_release(self, event):
        log.debug( 'mouse btn release (%s %s %s)', event.inaxes, event.button, event.key)
#        if event.inaxes == self.ax:
#            self.update()

#
#_zoomrectspec = {
#    'edgecolor': 'y',
#    'facecolor': None,
#    'fill': False,
#    'linewidth': 1.0       
#}
#
#class ZoomHandler(object):
#    def __init__(self, ax1, ax2):
#        
#        self.ax1 = ax1 
#        self.ax2 = ax2 # the ax that shows the zoomed window
#        
#        log.debug( "ax1: %s ax2 %s", ax1, ax2)
#        
#        self.c = RectCoords()
#        
#        self.quadratic = False
#        
#        self.rect = mpl.patches.Rectangle((0,0), 1, 1, **_zoomrectspec)
#        self.ax1.add_patch(self.rect)
#        
#        self.ax1.figure.canvas.mpl_connect('button_press_event', self.on_press)
#        self.ax1.figure.canvas.mpl_connect('motion_notify_event', self.on_move)
#
#        self.ax1.figure.canvas.mpl_connect('scroll_event', self.on_scroll)
#
#        self.ax1.figure.canvas.mpl_connect('key_press_event', self.on_key_press)
#        self.ax1.figure.canvas.mpl_connect('key_release_event', self.on_key_release)
#
#
#    def update_rect(self):
#        self.rect.set_width(self.c.width)
#        self.rect.set_height(self.c.height)
#        self.rect.set_xy((self.c.x0, self.c.y0))
#        #self.ax1.figure.canvas.draw()
#        self.ax1.draw_artist(self.rect)
#        self.update_zoomed_view()
#
#    def update_zoomed_view(self):
#        self.ax2.set_xlim(self.c.xlim)
#        self.ax2.set_ylim(self.c.ylim)
#        self.ax2.figure.canvas.draw()
#
#    def on_key_press(self, event):
#        log.debug('keypress (%s)', event.key)
#        if event.inaxes == self.ax1:
#            if event.key == "control":
#                self.quadratic = True
#    
#    def on_key_release(self, event):
#        log.debug( 'keyrelease (%s)', event.key)
#        if event.inaxes == self.ax1:
#            if event.key == "control":
#                self.quadratic = False
#
#    def on_press(self, event):
#        log.debug( 'btn press (%s %s)', event.inaxes, event.button)
#        if event.inaxes == self.ax1:
#            if event.button == 1: #left: set middle
#                pass
#            
#            elif event.button == 3: # right button: draw area
#                self.c.x0 = event.xdata
#                self.c.y0 = event.ydata
#                
#    def on_move(self, event):
#        if event.inaxes == self.ax1:
#            ex = event.xdata
#            ey = event.ydata
#                
#            if event.button == 1: #left: set middle
#                log.debug( 'mouse move (%s %s %s)', event.inaxes, event.button, event.key)
#                if self.c.x0 is None:
#                    log.warn("use rightclick to first create a rect before moving it")
#                    return
#                self.c.shift_to(ex, ey)
#                self.update_rect()
#                
#            elif event.button == 3: # right button: draw area
#                log.debug( 'mouse move (%s %s %s)', event.inaxes, event.button, event.key)
#                if self.quadratic:
#                    dx = ex - self.c.x0
#                    dy = ey - self.c.y0
#                    dd = max(abs(dx),abs(dy))
#                    ex = self.c.x0 + dd * np.sign(dx)
#                    ey = self.c.y0 + dd * np.sign(dy)
#                self.c.x1 = ex
#                self.c.y1 = ey
#                self.update_rect()
#
#
#    def on_scroll(self, event):
#        log.debug('scroll (%s %s %s)', event.inaxes, event.button, event.key)
#        if event.inaxes == self.ax1:
#                
#            if event.button == 'up':
#                print "up"
#                self.c.zoom(0.1)
#                self.update_rect()
#                
#            elif event.button == 'down':
#                print "up"
#                self.c.zoom(-0.1)
#                self.update_rect()
#            

    
    
class RectangleZoomSelector(object):
    
    def __init__(self, ax1, ax2):
        self.ax1 = ax1
        self.ax2 = ax2
        self.c = RectCoords()
        self.update_handles = [self.selfupdate]

        self.rs = matplotlib.widgets.RectangleSelector(
            ax1, self.on_select,
            drawtype='box',
            minspanx=None,
            minspany=None,
            useblit=False,
            lineprops=None,
            rectprops=None,
            spancoords='data',
            button=None,
            maxdist=10,
            marker_props=None,
            interactive=True,
            #state_modifier_keys=None
        )
        
    def register(self, h):
        self.update_handles.append(h)
        
    def update(self):
        log.debug("RectangleZoomSelector update")
        for h in self.update_handles:
            h()
            
            
    def selfupdate(self):
        #self.ax2.figure.canvas.draw()
        pass

    def on_select(self, e_start, e_end):
        log.debug("RectangleZoomSelector on_select")
        self.c.x0 = e_start.xdata
        self.c.y0 = e_start.ydata
        self.c.x1 = e_end.xdata
        self.c.y1 = e_end.ydata
        print self.c
        print self.c.xlim
        print self.c.ylim
    
        self.ax2.set_xlim(self.c.xlim)
        self.ax2.set_ylim(self.c.ylim_r)
        self.update()
    


class ROIDisplay(object):
    
    def __init__(self, ax, size=[1,1], roi=None, patches=None):
        self.ax = ax
        self.size = size
        self.roi = roi
        self.patches = patches
        self.mask = np.zeros(size, dtype=np.uint8)
        
        self.imgObj = ax.imshow(self.mask, cmap='gray', interpolation="none")
 
        self.ax.figure.canvas.mpl_connect('key_release_event', self.on_key_release)
       
    def update(self):
        log.debug("ROI update")
        self.selfupdate()
        
    def selfupdate(self):
        log.debug("ROI selfupdate")
        x0,x1 = self.roi.xlim
        y0,y1 = self.roi.ylim
        
        incl = [c for c,p,d in self.patches if d['type']=='incl']
        excl = [c for c,p,d in self.patches if d['type']=='excl']

        print incl
        print excl
        
        self.mask[:,:] = 0
        
        # make sure to first include, then exclude again
        for coords, b in [(incl, 255),(excl, 128)]:
            for c in coords:
#                x0 = c.x0-self.roi.x0
#                if x0<=0: x0= 0
#                y0 = c.y0-self.roi.y0
#                if y0<=0: y0= 0
#                x1 = c.x1-self.roi.x0 if c.x1<self.roi.x1 else self.roi.width
#                y1 = c.y1-self.roi.x0 if c.y1<self.roi.y1 else self.roi.height
                self.mask[c.slice2D] = b
                
        self.imgObj.set_data(self.mask)
        self.ax.set_xlim(self.roi.xlim)
        self.ax.set_ylim(self.roi.ylim_r)
        
                
    def on_key_release(self, event):
        if event.key==" ":
            log.debug("ROI key release") 
            self.selfupdate()
            
            
    

for asw in data:
    
    orgimg_path = os.path.join(_path, _fn%asw)
    if not os.path.isfile(orgimg_path):
        DORG.download_from_spacewarps(asw)
    
    orgimg = sp.misc.imread(orgimg_path)
    
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 3, 1)
    ax2 = fig.add_subplot(1, 3, 2)
    ax3 = fig.add_subplot(1, 3, 3)

    mpl_img1 = ax1.imshow(orgimg, interpolation="none", origin='upper')
    mpl_img2 = ax2.imshow(orgimg, interpolation="none", origin='upper')
    tmp      = ax3.imshow(orgimg, interpolation="none", origin='upper')

    ax1.set_title("1. choose region of interest")
    ax2.set_title("2. add + / rem - mask")
    ax3.set_title("3. [space] to refresh pixel mask")
    

    if False:
        ax1.xaxis.set_visible(False)
        ax1.yaxis.set_visible(False)
        ax2.xaxis.set_visible(False)
        ax2.yaxis.set_visible(False)
    

    h_c = mpl.widgets.MultiCursor(fig.canvas, (ax1, ax2, ax3), color='r', lw=1, horizOn=True, vertOn=True,useblit=False)

    #h_z = ZoomHandler(ax1,ax2)
    zoomsel = RectangleZoomSelector(ax1,ax2)
    masksel = MasksHandler(ax2)
    maskshow = ROIDisplay(ax3, orgimg.shape, zoomsel.c, masksel.patches)

    zoomsel.register(masksel.update)
    #masksel.register(maskshow.update)
    
    
#    rectsel = matplotlib.widgets.RectangleSelector(
#        ax1, onselect,
#        drawtype='box',
#        minspanx=None,
#        minspany=None,
#        useblit=False,
#        lineprops=None,
#        rectprops=None,
#        spancoords='data',
#        button=None,
#        maxdist=10,
#        marker_props=None,
#        interactive=True,
#        #state_modifier_keys=None
#        )
    
    
    fig.show()
    
    #plt.show()
    


    #fig.close()

### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)
    
print_last_line(I)
