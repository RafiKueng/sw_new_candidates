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
        
    def __str__(self):
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


class RectMask(RectCoords):
    def __init__(self, xy0, xy1=None, kind=None):

        if xy1 is None:
            xy1 = (xy0[0]+1, xy0[1]+1)
        # super(RectMask, self).__init__(x0,y0,x1,y1)

        # init patch first, the other setters need it..
        self.patch = mpl.patches.Rectangle((0,0), 1, 1, **_rectspec_pos) # real size will be set when assiging xy01
        
        if kind is None:
            kind = '+'
        self._kind = kind # '+': inclusive, '-' exclusive
        
        # set the corrdinates, that also sets the patch
        self.xy0 = xy0
        self.xy1 = xy1


    def __str__(self):
        return "RectMask%s (%4i/%4i to %4i/%4i)" % (self.kind, self.x0, self.y0, self.x1, self.y1)
        
    @property
    def x0(self):
        return self._x0

    @x0.setter
    def x0(self, v):
        self._x0 = v
        self.patch.set_x(v)
        self.update()

    @property
    def y0(self):
        return self._y0

    @y0.setter
    def y0(self, v):
        self._y0 = v
        self.patch.set_y(v)
        self.update()

    @property
    def x1(self):
        return self._x1

    @x1.setter
    def x1(self, v):
        self._x1 = v
        self.patch.set_width(self.dx)
        self.update()

    @property
    def y1(self):
        return self._y1

    @y1.setter
    def y1(self, v):
        self._y1 = v
        self.patch.set_height(self.dy)
        self.update()

    @property
    def xy0(self):
        return (self.x0, self.y0)

    @property
    def xy1(self):
        return (self.x1, self.y1)

    @xy0.setter
    def xy0(self, v):
        self.x0 = v[0]
        self.y0 = v[1]

    @xy1.setter
    def xy1(self, v):
        self.x1 = v[0]
        self.y1 = v[1]

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, v):
        if v == '+':
            self._kind = '+'
            self.patch.set(**_rectspec_pos)
        elif v == '-':
            self._kind = '-'
            self.patch.set(**_rectspec_neg)
        
    def update(self):
        pass
    
    def switch_kind(self):
        if self.kind == '+':
            self.kind = '-'
        else:
            self.kind = '+'



class GlobalHotkeyHandler(object):
    
    def __init__(self, fig):
        self.fig = fig
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('key_release_event', self.on_key_release)
    
    def on_key_press(self, event):
        log.debug("key press global '%s'", event.key)
    
    def on_key_release(self, event):
        log.debug("key release global '%s'", event.key)
        
        if event.key == "escape":
            plt.close(self.fig)
        


        

class MasksHandler(object):
    
    def __init__(self, ax=None):

        self.ax = ax if ax is not None else plt.gca()
        self.update_handler = []
        self.register(self.selfupdate)
        self.mode = '+' # are we masking in [+], masking out [-] or setting the center[.]
        # update: selecting the center can be done al the time using right click
        
        self.masks = []
        self.selected_mask = None

        self.center = None        
        self.cxl = None # center x line
        self.cyl = None
        
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_mouse_click)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        # self.ax.figure.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.ax.figure.canvas.mpl_connect('key_release_event', self.on_key_release)


    def register(self, h):
        self.update_handler.append(h)
        
    def update(self):
        log.debug("Masks update")
        for h in self.update_handler:
            h()

    def selfupdate(self):
        self.ax.figure.canvas.draw()


    def save(self):
        D = []
        for c,p,d in self.patches:
            D.append((c.as_array, d))
        return D
        
    def load(self, D):
        
        for ca, d in D:
            self.add_rect(d['type'], RectCoords(*ca), d)
            
        self.selfupdate()
            

    def add_mask(self, xy0, xy1=None):
        if xy1 is None:
            xy1 = (xy0[0]+1, xy0[1]+1)
        log.debug("add mask xy0=%s xy1=%s", xy0, xy1)
        
        mask = RectMask(xy0, xy1, self.mode)
        
        self.masks.append(mask)
        self.selected_mask = mask

        self.ax.add_patch(mask.patch)
        self.ax.draw_artist(mask.patch)


    def remove_mask(self, i=None):
        log.debug("removing mask index: %s", i)

        if i is None:
            mask = self.selected_mask
        else:
            mask = self.masks[i]
            

        self.masks.remove(mask)
        
        mask.patch.remove()
        del mask
        
        if len(self.masks)>0:
            self.selected_mask = self.masks[-1]
        else:
            self.selected_mask = None
            
            
    def set_center(self, xy):
        log.debug("set center %s", xy)
        self.center = xy
        if self.cxl is None:
            self.cxl = self.ax.axvline(xy[0], color="y")
            self.cyl = self.ax.axhline(xy[1], color="y")
        else:
            self.cxl.set_xdata(xy[0])
            self.cyl.set_ydata(xy[1])


    def switch_mode(self, mode):
        log.debug("switching mode to %s", mode)
        # mode = {'+':'mask+','-':'mask-','.':'center'}[smode]
        self.mode = mode
        
        if mode=="+":
            self.selected_mask.kind = '+'

        elif mode=="-":
            self.selected_mask.kind = '-'

        elif mode==".":
            pass
        


    def on_key_release(self, event):
        log.debug('key release (%s)', event.key)
        
        if event.key in ['+', '-', '.']:
            self.switch_mode(event.key)

        elif event.key=="insert":
            self.add_mask()
        
        elif event.key=="delete":
            self.remove_mask()
            
        else:
            try:
                i = int(event.key)
            except:
                return
            if i>=len(self.masks):
                i = len(self.masks)
            self.selected_mask = self.masks[i]
        

    def on_mouse_click(self, event):
        log.debug( 'mouse click (%s %s %s)', event.inaxes, event.button, event.key)

        if event.inaxes == self.ax:
            e_xy = (event.xdata, event.ydata)

            if event.button == 1:
                if event.key == "shift": # use shift to edit existing
                    self.selected_mask.xy0 = e_xy
                else:
                    self.add_mask(e_xy)

            elif event.button == 2:
                self.remove_mask()

            elif event.button == 3:
                self.set_center(e_xy)
                pass


    def on_mouse_move(self, event):
        
        if event.inaxes == self.ax:

            if event.button==1:
                log.debug( 'mouse move (%s %s %s)', event.inaxes, event.button, event.key)
                
                #if self.c.x0 is None:
                #    log.warn("use rightclick to first create a rect before moving it")
                #    return
                    
                self.selected_mask.x1 = event.xdata
                self.selected_mask.y1 = event.ydata

                self.ax.draw_artist(self.selected_mask.patch)


    def on_mouse_release(self, event):
        log.debug( 'mouse btn release (%s %s %s)', event.inaxes, event.button, event.key)
#        if event.inaxes == self.ax:
#            self.update()


    
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
    
    def __init__(self, ax, size=[1,1], roi=None, masks=None):
        self.ax = ax
        self.size = size
        self.roi = roi
        self.masks = masks
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
        
        incl = [m for m in self.masks if m.kind == '+']
        excl = [m for m in self.masks if m.kind == '-']
#        incl = [c for c,p,d in self.patches if d['type']=='incl']
#        excl = [c for c,p,d in self.patches if d['type']=='excl']

        print incl
        print excl
        
        self.mask[:,:] = 0
        
        # make sure to first include, then exclude again
        for masks, v in [(incl, 255),(excl, 128)]:
            for mask in masks:
                log.debug("ROI drawing, %s %s", v, mask)
                self.mask[mask.slice2D] = v
                
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
    
    hotkeys = GlobalHotkeyHandler(fig)
    h_c = mpl.widgets.MultiCursor(fig.canvas, (ax1, ax2, ax3), color='r', lw=1, horizOn=True, vertOn=True,useblit=False)

    #h_z = ZoomHandler(ax1,ax2)
    zoomsel = RectangleZoomSelector(ax1,ax2)
    masksel = MasksHandler(ax2)
    maskshow = ROIDisplay(ax3, orgimg.shape, zoomsel.c, masksel.masks)

    zoomsel.register(masksel.update)
    #masksel.register(maskshow.update)
    
    
    fig.show()
    
    #plt.show()
    


    #fig.close()

### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)
    
print_last_line(I)
