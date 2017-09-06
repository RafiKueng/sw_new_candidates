# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 23:04:17 2015

@author: rafik
"""

import os, csv
from os.path import join
import cPickle as pickle

import numpy as np
import matplotlib as mpl
import matplotlib.transforms as transforms

DEBUG = False
#DEBUG = True


PrintAll = False
PrintAll = True

if PrintAll:
    DATASET_TO_USE = "all_models"
#    PRINT_MID = True
else:
    DATASET_TO_USE = "selected_models"
#    PRINT_MID = False
    
PRINT_MID = False
    


HILIGHT_SWID = ['05', '42', '28', '58', '02','19','09','29','57']
HILIGHT_SWID = ["SW"+_ for _ in HILIGHT_SWID]


def set_mpl_rc():
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.size'] = 20

    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['text.latex.unicode'] = True

    mpl.rcParams['mathtext.fontset'] = 'custom'
    mpl.rcParams['mathtext.fontset'] = 'cm'
    mpl.rcParams['mathtext.default'] = "regular"
    
    #mpl.rcParams['mathtext.rm'] = 'Bitstream Vera Sans'
    #mpl.rcParams['mathtext.it'] = 'Bitstream Vera Sans:italic'
    #mpl.rcParams['mathtext.bf'] = 'Bitstream Vera Sans:bold'


# define colors
# http://matplotlib.org/examples/color/named_colors.html

imgext = "png"
filename_base = "{_[swid]}_{_[asw]}_{_[mid]}_%s." + imgext

colors = { # http://colorbrewer2.org/
    'hilight1' : "#ff7f00",
    'hilight2' : "#377eb8",
    'hilight3' : "#984ea3",
    'bg_elem'  : "dimgrey",

    'fg_area1' : "#fed9a6",
    'fg_area2' : "#b3cde3",
    'fg_area3' : "#decbe4",
    'bg_area'  : "lightgrey",
    'bg_area2'  : "darkgrey",

    'min': "dodgerblue",
    'sad': "green",
    'max': "red"
}

sizes = { # define them relative
#    'small'   : 'small',
#    'regular' : 'medium',
#    'big'     : 'large,'
    'small'   : 'medium',
    'regular' : 'large',
    'big'     : 'x-large',
    'huge'    : 'xx-large',
}

# linewidth
lw_fg = 2.0
lw_bg = 1.0

#misc settings
dpi = 150

cm = 0.393701  # cm / inch, so write values in
               # cm like:  5 * CM
cm *= 3   # add a general scale factor (to minimize the effect of borders ect..)

styles = {

#    'figure_sq' : {
#        'figsize' : (6,6),
#        'dpi'     : dpi,
#    },
#
#    'figure_rect' : {
#        'figsize' : (8,5),
#        'dpi'     : dpi,
#    },

        
    # define figure sizes in cm
    # small: 3 per pagewidth
    # med: two per pagewidth (one columnwidth)
    # big: full pagewidth size plot
    
    'figure_sq_small' : {
        'figsize' : (5.5*cm, 5.5*cm),
        'dpi'     : dpi,
    },

    'figure_sq_med' : {
        'figsize' : (8*cm, 8*cm),
        'dpi'     : dpi,
    },

    'figure_sq_big' : {
        'figsize' : (15*cm, 15*cm),
        'dpi'     : dpi,
    },

    'figure_rect_big' : {
        'figsize' : (15*cm, 10*cm),
        'dpi'     : dpi,
    },

    'figure_rect_med' : {
        'figsize' : (8*cm, 5.5*cm),
        'dpi'     : dpi,
    },

    
    'figure_save' : {
        'dpi'       : dpi,
        'facecolor' : 'w',
        'edgecolor' : 'w',
    },
   
    'fg_marker1' : {
        'marker'    : 'o',
        'color'     : colors['hilight1'],
        'facecolor' : colors['hilight1'],
        'markeredgecolor' : colors['hilight1'],
        'markeredgewidth' : 3.0 ,
        'markersize' : 10.0,
        #'fillstyle' : 'full',
        #'linestyle' : 'none',
    },

    'fg_marker2' : {
        'marker'    : '+',
        'color'     : colors['hilight2'],
        'facecolor' : colors['hilight2'],
        'markeredgecolor' : colors['hilight2'],
        'markeredgewidth' : 3.0 ,
        'markersize' : 10.0,
       #'fillstyle' : 'full',
        'linestyle' : 'none',
    },

    'fg_marker3' : {
        'marker'    : 'o',
        'color'     : colors['hilight3'],
        'facecolor' : colors['hilight3'],
        'markeredgecolor' : colors['hilight3'],
        #'fillstyle' : 'full',
        #'linestyle' : 'none',
    },
    
    'bg_marker' : {
        'marker'    : '+',
        'color'     : colors['bg_elem'],
        'facecolor' : colors['bg_elem'],
#        'markersize' : 55.0
        #DEL 'fillstyle' : 'full',
    },

    'fg_line1' : {
        'color'           : colors['hilight1'], 
        'linestyle'       : "solid",
        'linewidth'       : lw_fg,
#        'marker'          : None,
#        'markeredgecolor' : '',
#        'markeredgewidth' : '',
#        'markerfacecolor' : '',
#        'markersize'      : '',
    },

    'fg_line2' : {
        'color'           : colors['hilight2'], 
        'linestyle'       : "dashed",
        'linewidth'       : lw_fg,
#        'marker'          : 'none',
#        'markeredgecolor' : '',
#        'markeredgewidth' : '',
#        'markerfacecolor' : '',
#        'markersize'      : '',
    },

    'fg_line3' : {
        'color'           : colors['hilight3'], 
        'linestyle'       : "dashed",
        'linewidth'       : lw_fg,
#        'marker'          : 'none',
#        'markeredgecolor' : '',
#        'markeredgewidth' : '',
#        'markerfacecolor' : '',
#        'markersize'      : '',
    },

    'bg_line' : {
        'color'           : colors['bg_elem'], 
        'linestyle'       : "dotted",
        'linewidth'       : lw_fg,
#        'marker'          : 'none',
#        'markeredgecolor' : '',
#        'markeredgewidth' : '',
#        'markerfacecolor' : '',
#        'markersize'      : '',
    },

    # used for arrival time and kappa plots 
    'fg_contour': {
        'linewidth'     : lw_fg,
        'colors'        : [colors['hilight1'],],
        'cmap'          : None,
        'interpolation' : 'nearest',
        'aspect'        : 'equal',
        'origin'        : 'upper',
        'antialiased'   : True,
        'linestyles'    : 'solid',
    },

    'bg_contour': {
        'linewidth'     : lw_bg,
        'colors'        : [colors['hilight2'],],
        'cmap'          : None,
        'interpolation' : 'nearest',
        'aspect'        : 'equal',
        'origin'        : 'upper',
        'antialiased'   : True,
        'linestyles'    : [(5,(3,3)),],
    },

    'main_contour': {
        'linewidth'     : lw_fg,
        'colors'        : 'black',
        'cmap'          : None,
        'interpolation' : 'nearest',
        'aspect'        : 'equal',
        'origin'        : 'upper',
        'antialiased'   : True,
        'linestyles'    : [(5,(3,3)),],
    },

    'filled_contours': {
        'cmap'          : "coolwarm",
        'interpolation' : 'nearest',
        'aspect'        : 'equal',
        'origin'        : 'upper',
        'antialiased'   : True,
        'extend'        : 'both',
    },

    
    
    'fg_area1' : {
        'facecolor': colors['fg_area1'],
        'edgecolors': 'none',
        'linewidths': None
    },

    'bg_area' : {
        'facecolor': colors['bg_area'],
        'edgecolors': 'none',
        'linewidths': None,
        #'linestyle': u':', 
        #'color'    : None,
    },

    'bg_area2' : {
        'facecolor': colors['bg_area2'],
        'edgecolors': 'none',
        'linewidths': None,
        #'linestyle': u':', 
        #'color'    : None,
    },

    'err_area1' : {
        'facecolor': colors['hilight1'],
        'edgecolor': 'none',
        'linewidth': None,
        'alpha'    : 0.8,
        'zorder'   : 99,
    },

    'err_area2' : {
        'facecolor': colors['hilight2'],
        'edgecolor': 'none',
        'linewidth': None,
        'alpha'    : 0.4,
        'zorder'   : 98,
    },

    
    'text': {
        'ha':'left',
        'va':'bottom',
        'size': sizes['regular'],
    },
    
    'label' : {
        'fontsize' : sizes['regular']
    },
    
    'toplabel_bright': {
        'fontsize' : 36,
        'color'    : 'black',
        'backgroundcolor': "none",
        'family': 'sans-serif',
        'zorder': 999,
        'bbox' : {
                  'boxstyle':'round,pad=0.3',
#                  'color':'white',
                  'facecolor':'white',
                  'edgecolor':'none',
#                  'pad':7,
                  'alpha':0.75,
                  'zorder': 998,
                  },
    },

    'sublabel_bright': {
        'fontsize' : 26,
        'color'    : 'black',
        'backgroundcolor': "none",
        'family': 'sans-serif',
        'zorder': 989,
        'bbox' : {
                  'boxstyle':'round,pad=0.3',
#                  'color':'white',
                  'facecolor':'white',
                  'edgecolor':'none',
#                  'pad':3,
                  'alpha':0.75,
                  'zorder': 988,
                  },
    },



    'toplabel_dark': {
        'fontsize' : 36,
        'color'    : 'white',
        'backgroundcolor': "none",
        'family': 'sans-serif',
        'zorder': 999,
        'bbox' : {
                  'boxstyle':'round,pad=0.3',
#                  'color':'white',
                  'facecolor':'black',
                  'edgecolor':'none',
#                  'pad':7,
                  'alpha':0.75,
                  'zorder': 998,
                  },
    },

    'sublabel_dark': {
        'fontsize' : 26,
        'color'    : 'white',
        'backgroundcolor': "none",
        'family': 'sans-serif',
        'zorder': 989,
        'bbox' : {
                  'boxstyle':'round,pad=0.3',
#                  'color':'white',
                  'facecolor':'black',
                  'edgecolor':'none',
#                  'pad':3,
                  'alpha':0.75,
                  'zorder': 988,
                  },
    },






    
#    'inplot_caption_text_bright':{
#        'size'     : 36,
#        'color'    : 'black',
#        'backgroundcolor': "none",
#        'family': 'sans-serif',
#        'zorder': 99,
#        'bbox' : {
#                  'color':'white',
##                  'facecolor':'none',
##                  'edgecolor':'none',
#                  'pad':7,
#                  'alpha':0.75,
#                  'zorder': 99,
#                  },
#    },
#
#    'inplot_caption_text_dark':{
#        'size'     : 36,
#        'color'    : 'white',
#        'backgroundcolor': "none",
#        'family': 'sans-serif',
#        'zorder': 99,
#        'bbox' : {
#                  'color':'black',
##                  'facecolor':'none',
##                  'edgecolor':'none',
#                  'pad':7,
#                  'alpha':0.75,
#                  'zorder': 99,
#                  },
#    },
                
    'scalebar' : {
        'loc'      : 4,
        'alpha'    : 0.75,
        'pad'      : 0.5,   # padding around fraction of font size
        'borderpad': 1,     # distance to the border (fraction of font size)
        'sep'      : 5,     # separation between scalebar and number (in points)
        'frameon'  : True   # draw background
    },

# ax.tick_params

    'ticks_bottom_left' : {
        'axis' : 'both',
        'which' : 'both',
        'bottom' : True,
        'top': False,
        'left': True,
        'right': False
    },

    'no_ticks' : {
        'axis' : 'both',
        'which' : 'both',
        'bottom' : False,
        'top': False,
        'left': False,
        'right': False
    },

    
    'big_majorticks' : {
        'axis'  : 'both',
        'which' : 'major',
        'width': 3,
        'length': 6,
        #'labelsize': sizes['small'],
        #'labelbottom' : False,
        #'labeltop': False,
        #'labelleft': False,
        #'labelright': False
    },
    'big_minorticks' : {
        'axis': 'both',
        'which' : 'minor',
        'width':  3 ,# * 0.5,
        'length': 6 ,#* 0.5,
#        'labelsize': sizes['small'],
#        'labelbottom' : False,
#        'labeltop': False,
#        'labelleft': False,
#        'labelright': False
    },



    'no_labels': {
#        'axis':'x',          # changes apply to the x-axis
#        'which':'both',      # both major and minor ticks are affected
        'labelbottom' : False,
        'labeltop': False,
        'labelleft': False,
        'labelright': False
                               
    },
    'labels_bottom_left': {
        'labelbottom' : True,
        'labeltop': False,
        'labelleft': True,
        'labelright': False
    },
    
    
    'EXTPNT' : {
        'names'  : ["min", "sad", "max"],
        'colors' : [colors['min'],colors['sad'],colors['max']],
        'markers': ['v', '_', '^'],
        'offsets': [(0,3),(1,3),(2,3)], # draw every (start, offset)
        'linewidth': lw_fg,
    },

}



# Image marker postitions
# coordinates relative to plot!
#iypos = 0.875 # general y postion of the image marker line
#dy = 0.066  # length of the line 
#oy = 0.015   # offset between lines

iypos = 0.90 # general y postion of the image marker line
dy = 0.060  # length of the line 
oy = 0.000   # vertical offset between lines / types of points


def plot_image_positions(ax, imgs):
    
    trans = transforms.blended_transform_factory(
        ax.transData, ax.transAxes)
    
    for img in imgs:
        
        xpos = np.abs(img['pos'])
        i = styles['EXTPNT']['names'].index(img['type'])
        c = styles['EXTPNT']['colors'][i]
        m = styles['EXTPNT']['markers'][i] # assign marker style
        # http://matplotlib.org/examples/lines_bars_and_markers/marker_reference.html
        de = styles['EXTPNT']['offsets'][i] # draw every (start, offset)
        lw = styles['EXTPNT']['linewidth']

        sy = oy * i
        #plt.axvline(xpos, iypos+sy, iypos+dy+sy, color="k" )
        
        #_, iypt=  ax.transData.transform_point((0, iypos+dy+sy))
        #_, iypb=  ax.transData.transform_point((0, iypos+sy))
        #print iypt, iypb
        ax.plot([xpos, xpos, xpos], [iypos+sy, iypos+dy/2.+sy, iypos+dy+sy],
                 color=c,
                 linewidth=lw,
                 marker=m,
                 markevery=de,
                 markeredgecolor=c,
                 markerfacecoloralt=c,
                 transform=trans)




settings = {

# setup directories
    'asset_dir': 'assets', # use for external, static files that should not change (downloads)
    'cache_dir': 'cache',  # use for internal, possibly changing files (pickles)
    'input_dir': 'input', # input / data files generated manually, used here
    'output_dir': 'output', # where the calculated data is stored
    'temp_dir': 'temp', # use this dir to create temp files, like csv versions of pickle files for checking
    'tmpl_dir': 'templates', # templatesdir



    
}

_=settings

# where to store all the state and config files (uses gigabytes!)
state_path = join(_['asset_dir'], 'models')
cfg_path = join(_['asset_dir'], 'models')
sworg_path = join(_['asset_dir'], 'spacewarps_orginals')
splinp_path = join(_['asset_dir'], 'spl-input')
splorgs_path = join(_['asset_dir'], 'splorgs')
spllog_path = join(_['asset_dir'], 'logfiles')

# where to store the processed state file pickles
stateconf_cache_path = join(_['cache_dir'], 'stateconf')

# how to name the config and state files..
state_fn = "%s.state"
cfg_fn = "%s.cfg"



# make sure the folders exist
for k,v in settings.items():
    if k.endswith('_dir') and not os.path.exists(v):
        os.makedirs(v)

for p in [
        state_path,
        cfg_path,
        sworg_path,
        stateconf_cache_path
    ]:
    if not os.path.exists(p):
        os.makedirs(p)

# cosmetics
INT = ' '*4 # default 1 level intentsion







def save_pickle(I, fn, data):
    print I, 'save data to cache (pickle)',
    with open(fn, 'wb') as f:
        pickle.dump(data, f, -1)
    print "DONE"
        
def load_pickle(I, fn):
    print I, 'load cached data from pickle',
    with open(fn, 'rb') as f:
        p = pickle.load(f)
    print "DONE"
    return p

def save_csv(I, fn, data, pkey_n):
    print I, 'save_csv',

    with open(fn, 'w') as f:
        
        # get all available keys
        keys = set()
        for v in data.values():
            keys.update(v.keys())
        keys = [pkey_n,]+list(keys)

        # write output
        csvw = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        csvw.writeheader()
        for pkey, v in data.items():
            d=dict()
            d.update({pkey_n:pkey})
            d.update(v)
            csvw.writerow(d)

    print "DONE"


def getI(f):
    return os.path.basename(f)+':'

def print_first_line(I):
    print '\n',I,"STARTING\n"
    
def print_last_line(I, data=None):
    s=" (got %i entries)" % len(data) if data else ""
    print '\n',I, "FINISHED%s\n" % s
    print '-'*80

def del_cache(I,fn):
    print I,"deleting cache and quitting"
    try:
        os.remove(fn)
    except OSError:
        pass


from mpl_toolkits.axes_grid.anchored_artists import AnchoredText
from matplotlib.text import Text

#def add_inline_label(ax, t, loc=2, color="bright"):
#    fp = styles['inplot_caption_text_'+color]
#    at = AnchoredText(t, loc=loc, prop=fp, frameon=False) #, zorder=999)
#    at.zorder = 999
#    ax.add_artist(at)
#    return at
#


def add_inline_toplabel(ax, text="", color="bright"):

    fp = styles['toplabel_'+color]

    tx = ax.text(0.95, 0.95,
                 text,
                 verticalalignment='top',
                 horizontalalignment='right',
                 transform=ax.transAxes,
                 **fp
                 )

    return tx

def add_inline_sublabel(ax, text="", color="bright"):

    fp = styles['sublabel_'+color]

    tx = ax.text(0.95, 0.8,
                 text,
                 verticalalignment='top',
                 horizontalalignment='right',
                 transform=ax.transAxes,
                 **fp
                 )

    return tx



def add_caption_swid(ax, text, color="bright"):
    add_inline_toplabel(ax, text=text, color=color)
    
def add_caption_mid(ax, text, color="bright"):
    if PRINT_MID:
        add_inline_sublabel(ax, text=text, color=color)
    
    
    
from mpl_toolkits.axes_grid.anchored_artists import AnchoredSizeBar
import matplotlib.colors as colors

def add_size_bar(ax, text, length=1,
                 height=None,
                 heightIsInPx = True,   # the height is given in arb unit, not plotting units
                 loc=4,
                 theme = "bright",
                 barcol = "white", txtcol = "white", bgcol = "black", # theme overrides color
                 alpha = 0.5,
                 pad = 0.5,       # padding around fraction of font size
                 borderpad = 1,   # distance to the border (fraction of font size)
                 sep = 5,         # separation between scalebar and number (in points)
                 frameon=False    # draw background
                 ):

    try:
        if theme=="bright":
            barcol = "black"
            txtcol = "black"
            bgcol = "white"
        elif theme=="dark":
            barcol = "white"
            txtcol = "white"
            bgcol = "black"
        else:
            barcol = "black"
            txtcol = "black"
            bgcol = "white"
            
    except NameError:
        pass
        
    if height and heightIsInPx:
        scale = 1
        height = height * scale
        
    kw = {
        'loc'          : loc,
        'pad': pad, 'borderpad': borderpad, 'sep': sep,
        'prop': mpl.font_manager.FontProperties(
                    size=sizes['big'],
                    weight = 'extra bold', #‘ultralight’, ‘light’, ‘normal’, ‘regular’, ‘book’, ‘medium’, ‘roman’, ‘semibold’, ‘demibold’, ‘demi’, ‘bold’, ‘heavy’, ‘extra bold’, ‘black’
                ),
#        'color'        : txtcol,
        'frameon'      : frameon
    }
    
    if height:
        kw.update({'size_vertical': height})

    
    if heightIsInPx:
        trans = transforms.blended_transform_factory(
                ax.transData, ax.transAxes)
    else:
        trans = ax.transData

    asb = AnchoredSizeBar(trans,
                          length,
                          text,
                          **kw)

    
    # color the actual scalebar (override)
    rect = asb.size_bar.get_children()[0]
    rect.set_fill(True)
    rect.set_facecolor(barcol)
    rect.set_edgecolor(barcol)
    
    # modify text
    txtarea = asb.txt_label
    txtelem = txtarea.get_children()[0]
    txtelem.set_color(txtcol)
    #txtelem.set_fontsize()
    
    # color the background
    asb._drawFrame = frameon
    col = bgcol
    alp = alpha
    col = tuple(list(colors.to_rgba(col))[:3] + [alp,])
       
    asb.patch.set_facecolor(col)
    asb.patch.set_edgecolor(tuple(list(colors.to_rgba(col))[:3] + [0,])) # increase alpha for border around
    

    ax.add_artist(asb)

    return asb

