# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 20:37:05 2016

@author: rafik
"""

import os
import sys
import logging
import cPickle as pickle

import numpy as np
import scipy as sp
import scipy.misc
import matplotlib as mpl
mpl.use('Qt4Agg') # the default Qt5Agg is really buggy at the moment
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

plt.ioff()

#CRDA.ONLY_RECENT_MODELS
#CRDA.ALL_MODELS

_path = _S.sworg_path
_fn = "%s.png" # placeholder is asw name, should be the same as in DORG!


data = ['ASW0007k4r']

swid2asw = dict((v['swid'], k) for k, v in PACA.DATA.items())
swid2model = dict(((m['swid'], k) for k,m in CRDA.ONLY_RECENT_MODELS.items()))
asw2model = dict(((m['asw'], k) for k,m in CRDA.ALL_MODELS.items() if m.get('asw')))

swidAswMid = [(swid, asw, asw2model[asw]) for swid, asw in swid2asw.items() if asw2model.get(asw)]

# this would be a one to many..
#rawasw = sorted([(m['asw'], k) for k,m in CRDA.ALL_MODELS.items() if m.get('asw')])
#asw2model = {}
#for asw,mid in rawasw:
#    asw2model.setdefault(asw, []).append(mid)
    


class RectCoords(object):
    
    def __init__(self, x0=None,y0=None,x1=None,y1=None):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        
    def __str__(self):
        return "RectCoords((%4i/%4i) to (%4i/%4i))" % (self.x0, self.y0, self.x1, self.y1)

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
    def tuple(self):
        return (self.xy0, self.xy1)

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
        


_rectspec = {
    'edgecolor': None,
    'facecolor': None,
    'alpha' : 0.5,
    'fill': False,
    'linewidth': 3.0
}
_rectspec_pos = {}
_rectspec_pos.update(_rectspec)
_rectspec_pos.update({
    'edgecolor': 'g',
    'facecolor': None,
    'fill': False,
})
_rectspec_neg = {}
_rectspec_neg.update(_rectspec)
_rectspec_neg.update({
    'edgecolor': 'r',
    'facecolor': "r",
    'fill'     : True
})


class RectMask(RectCoords):
    def __init__(self, xy0, xy1=None, kind=None):

        if xy1 is None:
            xy1 = (xy0[0]+1, xy0[1]+1)
        # super(RectMask, self).__init__(x0,y0,x1,y1)

        # init patch first, the other setters need it..
        self.patch = mpl.patches.Rectangle((0,0), 1, 1, **_rectspec_pos) # real size will be set when assiging xy01
        
        if kind is None:
            kind = '+'
        self.kind = kind # '+': inclusive, '-' exclusive
        
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
    @property
    def tuple(self):
        return (self.xy0, self.xy1, self.kind)

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
    
    def __init__(self, ax=None, image=None, zoomH=None):

        self.ax = ax if ax is not None else plt.gca()
        self.image = image        
        self.zoomH = zoomH
        
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
        log.debug("redraw canvas")
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
            

    def add_mask(self, xy0, xy1=None, mode=None):
        
        if mode is None:
            mode = self.mode # can be over wridden for automatic loading
            
        if xy1 is None:
            xy1 = (xy0[0]+1, xy0[1]+1)
        log.debug("add mask %s xy0=%s xy1=%s", mode, xy0, xy1)
        
        mask = RectMask(xy0, xy1, mode)
        
        self.masks.append(mask)
        self.selected_mask = mask
        self.ax.add_patch(mask.patch)
        
        self.selfupdate()


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
            
        self.selfupdate()
            
            
    def set_center(self, xy):
        log.debug("set center %s", xy)
        self.center = xy
        if self.cxl is None:
            self.cxl = self.ax.axvline(xy[0], color="y")
            self.cyl = self.ax.axhline(xy[1], color="y")
        else:
            self.cxl.set_xdata(xy[0])
            self.cyl.set_ydata(xy[1])
            
        self.selfupdate()
        
        
    def find_center(self):
        # only consider red and green channel
        l=list(self.zoomH.c.slice3D)
        l[2] = np.s_[0:3]
        rg = np.sum(self.image[l],axis=2)
        rg = sp.ndimage.gaussian_filter(rg,3)
        ox, oy = np.unravel_index(np.argmax(rg),rg.shape)
        xx = ox+zoomH.c.x0
        yy = ox+zoomH.c.y0
        xy = (xx,yy)
        log.debug("found center in %s", xy)
        self.set_center(xy)
        

    def switch_mode(self, mode):
        log.debug("switching mode to %s", mode)
        # mode = {'+':'mask+','-':'mask-','.':'center'}[smode]
        self.mode = mode
        
        if mode=="+":
            self.selected_mask.kind = '+'

        elif mode=="-":
            self.selected_mask.kind = '-'

        elif mode==".":
            self.find_center()
        
        self.selfupdate()
        


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
        
            self.selfupdate()


    def on_mouse_move(self, event):
        
        if event.inaxes == self.ax:

            if event.button==1:
                log.debug( 'mouse move (%s %s %s)', event.inaxes, event.button, event.key)
                
                #if self.c.x0 is None:
                #    log.warn("use rightclick to first create a rect before moving it")
                #    return
                    
                self.selected_mask.x1 = event.xdata
                self.selected_mask.y1 = event.ydata
                self.selfupdate()


    def on_mouse_release(self, event):
        log.debug( 'mouse btn release (%s %s %s)', event.inaxes, event.button, event.key)
#        if event.inaxes == self.ax:
#            self.update()
        self.selfupdate()


    
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
            useblit=True,
            #lineprops=None,
            #rectprops=None,
            spancoords='data',
            button=None,
            maxdist=10,
            #marker_props=None,
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
        self.ax1.figure.canvas.draw()
        
    def set_zoom(self, xy0, xy1):
        self.c.x0 = xy0[0]
        self.c.y0 = xy0[1]
        self.c.x1 = xy1[0]
        self.c.y1 = xy1[1]
    
        self.ax2.set_xlim(self.c.xlim)
        self.ax2.set_ylim(self.c.ylim_r)
        self.update()
        


    def on_select(self, e_start, e_end):
        log.debug("RectangleZoomSelector on_select")
        self.set_zoom((e_start.xdata, e_start.ydata),(e_end.xdata, e_end.ydata))
    


class ROIDisplay(object):
    
    def __init__(self, ax, img, size=[1,1], roi=None, masks=None):
        self.ax = ax
        self.img = img
        if len(size)==3:
            size = size[0:2]
        self.size = size
        self.roi = roi
        self.masks = masks
        self.maskimg = np.zeros(size+(3,), dtype=np.uint8)
        self.binary_mask = np.zeros(size, dtype=np.bool)
        
        self.imgObj = ax.imshow(self.maskimg, cmap='gray', interpolation="none")
 
        self.ax.figure.canvas.mpl_connect('key_release_event', self.on_key_release)

        
    def register(self, fnc):
        pass
    
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
        
        self.maskimg[:,:] = 0
        
        # make sure to first include, then exclude again
        for masks, v in [(incl, True),(excl, False)]:
            for mask in masks:
                log.debug("ROI drawing, %s %s", v, mask)

                if v:
                    self.maskimg[mask.slice2D] = self.img[mask.slice2D]
                    self.binary_mask[mask.slice2D] = True
                else:
                    self.maskimg[mask.slice2D] = 64
                    self.binary_mask[mask.slice2D] = False

                    
                
        self.imgObj.set_data(self.maskimg)
        self.ax.set_xlim(self.roi.xlim)
        self.ax.set_ylim(self.roi.ylim_r)

        self.ax.figure.canvas.draw()        
                
    def on_key_release(self, event):
        if event.key==" ":
            log.debug("ROI key release") 
            self.selfupdate()
            


glass_basis('glass.basis.pixels', solver=None)
exclude_all_priors()

class Analysis(object):

    def __init__(self, orgimg, state_fn, zoomH, maskH, roiH, axSynthImg, axSrcImg=None, axSrcImgGray=None, axCount=None, axDiff=None):
        
        self.orgimg = orgimg
        self.state_fn = state_fn
        
        self.zoomH = zoomH
        self.maskH = maskH # yea thats not good coding, but a lot faster than fixing all the things..
        self.roiH = roiH
        
        self.axSynthImg = axSynthImg
        self.axSrcImg = axSrcImg
        self.axSrcImgGray = axSrcImgGray
        self.axCount = axCount
        self.axDiff = axDiff
        
        self.mask = None # just set it when we know its ready
        self.center = None

        self.synimg = orgimg * 0

        self.axSynthImg.figure.canvas.mpl_connect('key_release_event', self.on_key_release)

    def px2arcs(self, coords, pxsize = 0.187):
    
        x = coords[1]
        y = -coords[0]
    
        cx, cy = self.center
    
        x = ( x-cx ) * pxsize
        y = ( y-cy ) * pxsize
        
        return x+1j*y


    def update(self):
        s2d = self.zoomH.c.slice2D
        s3d = self.zoomH.c.slice3D
        
        self.orgimg_c = self.orgimg[s3d]
        self.mask = self.roiH.binary_mask[s2d]
        self.center = self.maskH.center
        if self.center is None:
            log.warn("no center selected, aborting !!!!!!!!!!!!!!!!!!!!!!!!!!!")
            return
        
        self.run()

        
    def run(self):
        
        state = loadstate(self.state_fn)
        state.make_ensemble_average()
        
        model = state.ensemble_average
        
        obj_index = 0
        obj, ps = model['obj,data'][obj_index]

        src_index = 0
        src = ps['src'][src_index]

        zcap = obj.sources[src_index].zcap
        
        def delta_beta(theta):
            return src - theta + obj.basis.deflect(theta, ps) / zcap
        
        # get Pixel Indices in X/Y direction where mask is true
        pix, piy = np.where(self.mask==True)
        pixel = np.array((pix, piy)).T # merge the two lists and reformate
        
        theta = [self.px2arcs(p) for p in pixel]
        d_source = np.array(map(delta_beta, theta))
        
        # range of grid on sourceplane
        r = max(np.max(np.abs(d_source.real)), np.max(np.abs(d_source.imag)))
        
        # number of gridpoints on sourceplane (2M+1)
        M = 20
        
        X = np.int32(np.floor(M*(1+d_source.real/r)+.5))
        Y = np.int32(np.floor(M*(1+d_source.imag/r)+.5))
        
        pxllist = np.zeros((2*M+1,2*M+1), dtype=list)
        srcimg  = np.zeros((2*M+1,2*M+1,3), dtype=np.uint8)
        srcimg_gray = np.zeros((2*M+1,2*M+1), dtype=np.uint8)
        cntimg  = np.zeros((2*M+1,2*M+1), dtype=np.uint8)
        
        for (x,y), value in np.ndenumerate(pxllist):
            pxllist[x,y] = []
            
        for i, pnt in enumerate(d_source):
            x,y = (X[i], Y[i])
            pxllist[x,y].append(i)
        
        
        self.synimg = self.orgimg_c * 0
        
        for (x,y), lst in np.ndenumerate(pxllist):
            n = len(lst)    
            if n>0:
                summ = np.array([0,0,0], dtype=np.int32)
                for i in lst:
                    ix,iy = pixel[i]
                    summ += self.orgimg_c[ix,iy]
                pxlave = np.uint8(np.clip((summ / n), 0, 255))
        
                srcimg[x,y] = pxlave
                srcimg_gray[x,y] = np.average(pxlave)
        
                cntimg[x,y] = n
                
                for i in lst:
                    ix,iy = pixel[i]
                    self.synimg[ix,iy] = pxlave
        
        log.debug("showing result of analysis")
        self.axSynthImg.imshow(self.synimg)
        #self.axSynthImg.set_xlim(self.roiH.ax.get_xlim())
        #self.axSynthImg.set_ylim(self.roiH.ax.get_ylim())
        self.axSynthImg.figure.canvas.draw()
        
    def on_key_release(self, event):
        log.debug("analysis key release, %s", event.key)

        if event.key=="enter":
            self.update()

            

swidAswMid = [("sw00", 'ASW0007k4r', "012402")]

for swid, asw, mid in swidAswMid:
    
    log.info("working on %s %s %s", swid, asw, mid)
    
    orgimg_path = os.path.join(_path, _fn%asw)
    if not os.path.isfile(orgimg_path):
        DORG.download_from_spacewarps(asw)
    state_path = os.path.join(_S.state_path, _S.state_fn%mid)
    
    orgimg = sp.misc.imread(orgimg_path)
    
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 4, 1)
    ax2 = fig.add_subplot(1, 4, 2)
    ax3 = fig.add_subplot(1, 4, 3)
    ax4 = fig.add_subplot(1, 4, 4)

    mpl_img1 = ax1.imshow(orgimg, interpolation="none", origin='upper')
    mpl_img2 = ax2.imshow(orgimg, interpolation="none", origin='upper')
    tmp      = ax3.imshow(orgimg, interpolation="none", origin='upper')

    ax1.set_title("1. choose region of interest")
    ax2.set_title("2. add + / rem - mask; right clk to set center")
    ax3.set_title("3. [space] to refresh pixel mask")
    ax3.set_title("4. [enter] to get synth img")
    

    if False:
        ax1.xaxis.set_visible(False)
        ax1.yaxis.set_visible(False)
        ax2.xaxis.set_visible(False)
        ax2.yaxis.set_visible(False)
    
    hotkeysHandle = GlobalHotkeyHandler(fig)
    multiCursorHandle = mpl.widgets.MultiCursor(fig.canvas, (ax1, ax2, ax3, ax4), color='r', lw=1, horizOn=True, vertOn=True,useblit=True)

    #h_z = ZoomHandler(ax1,ax2)
    zoomH = RectangleZoomSelector(ax1,ax2)
    maskH = MasksHandler(ax2, orgimg, zoomH)
    roiH  = ROIDisplay(ax3, orgimg, orgimg.shape, zoomH.c, maskH.masks)
    analH = Analysis(orgimg, state_path, zoomH, maskH, roiH, ax4)

    # tell the next step in the pipeline to update automatically
    zoomH.register(maskH.update)
    roiH.register(analH.update)
    
    # load data if available
    fn = '%s_%s_regions.pickle'%(asw,mid)
    if os.path.isfile(fn):
        with open(fn, 'rb') as f:
            p = pickle.load(f)
        
        zoomH.set_zoom(*p['zoom'])
        maskH.set_center(p['center'])
        for m in p['masks']:
            maskH.add_mask(*m)

        p['masks']
        
    
    #fig.show()
    
    #plt.show()
    plt.close()
    
    d = {
        'zoom'  : zoomH.c.tuple,
        'center': maskH.center,
        'masks' : [m.tuple for m in maskH.masks]
    }
    if True:
        with open(fn, 'wb') as f:
            pickle.dump(d,f)


    #fig.close()

### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)
    
print_last_line(I)