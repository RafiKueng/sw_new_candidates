# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 18:10:52 2016

@author: rafik
"""

import os
from os.path import join
import glob
import pickle

# reminder: settings before mpl
import settings as SET
reload(SET)
SET.set_mpl_rc()
STY = SET.styles # for better reload() in ipython
S = SET.settings
# from settings import getI, INT


import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

import scipy.interpolate as interpolate
import scipy.optimize as optimize

#import create_data as CRDA
#import parse_candidates as PACA

#from stelmass.angdiam import sig_factor, dis_factor, kappa_factor
from stelmass.angdiam import kappa_factor


DBG = SET.DEBUG
# DBG= True

fpath     = join(S['output_dir'], 'hires_comparison')
filename = "{_[asw]}_{_[mid]}_{_[mode]}_hires_comparison." + SET.imgext


# txt data of simulations
sims_dir = join(S['input_dir'], 'hires/systems')
pckl_dir = join(S['input_dir'], 'hires/pickles')

# rE text label position
rEpos = 0.5 # in axes coordinates
t_dx = 0.0
t_dy = 0.1




SIMS = {}
DATA = {}


if not os.path.exists(fpath):
    os.makedirs(fpath)


def fetch_sims_data():

    paths = glob.glob(os.path.join(sims_dir, '*.txt' ))
    for path in paths:

        with open(path, 'r') as f:
            lines = f.readlines()
        
        name = os.path.basename(path)[:-4] # strip .txt
        
        xvals = []
        yvals = []
        
        for line in lines:
            #print line
            try:    
                x, _, y = line.strip().split(' ')
            except:
                print 'split not possible' 
                continue
            xvals.append(x)
            yvals.append(y)
        
        vals = {
            'x': np.array(xvals, dtype=np.float32),
            'y': np.array(yvals, dtype=np.float32),
        }
        SIMS[name] = vals



# load the generated data
# data is generated using the repro rerun_hires!
def load_data_from_pickles():
    
    paths = glob.glob(os.path.join(pckl_dir, '*.pickle' ))

    for ppath in paths:
        _tmp = ppath.split('/')[-1].split('.')[0].split('_')
        mid, hr_rad, hr_lev = map(int, _tmp[1:4])
        
        
        if os.path.isfile(ppath):
            print "   pickle file loading: ", mid, hr_rad, hr_lev
            with open(ppath, 'r') as f:
                d = pickle.load(f)
            if not mid in DATA.keys():
                DATA[mid] = {}
            DATA[mid][hr_rad*10 + hr_lev] = d
                
        else:
            print "    !!!pickle file not found!!!", ppath




def getEinsteinR(x, y):
    #poly = interp.PiecewisePolynomial(x,y[:,np.newaxis])
    poly = interpolate.BPoly.from_derivatives(x,y[:,np.newaxis])
    
    
    def one(x):
        return poly(x)-1
    
    x_min = np.min(x)
    x_max = np.max(x)
    x_mid = poly(x[len(x)/2])
    
    rE,infodict,ier,mesg = optimize.fsolve(one, x_mid, full_output=True)
    
    #print rE,infodict,ier,mesg
    
    if (ier==1 or ier==5) and x_min<rE<x_max and len(rE)==1:
      return rE[0]
    elif len(rE)>1:
      for r in rE:
        if x_min<r<x_max:
          return r
    else:
      return False









fetch_sims_data()
load_data_from_pickles()


MAP = {
    
}


for coll in DATA.values():
    for mode, dd in coll.items():
    
        mid = dd['mid']
        asw = dd['asw']
    
        print asw, mid, mode
        
        if not mid:
            print "   no mid, skipping"
            continue
        
        #imgname = join(fpath, "%s_%s_kappa_encl.png" % (asw, mid))
        imgname = join(fpath, filename.format(_={'asw':asw, 'mid':mid, 'mode':mode }))
        
        m = dd
    
        # load correcting factors
        zl_actual = 1.0
        zs_actual = 2.0
        zl_used   = m['z_lens_used']          # from PSAC: the parsed config file
        zs_used   = m['z_src_used']           # same here
        

        s_cf = 1
        k_cf = 1

        s_cf = 440. / 500 * 100  # rescale to original 440 pixels
        k_cf = kappa_factor(zl_used, zs_used)
    
        # m['kappa(<R)'] is actually kappa_infty!
        # kappa = D_ls / D_s * kappa_infty
        
        print "      ",s_cf, k_cf
        
        rr = m['R']['data']         * s_cf
        da = m['kappa(<R)']['data'] * k_cf
        mn = m['kappa(<R)']['min']  * k_cf
        mx = m['kappa(<R)']['max']  * k_cf
        
        for img in m['images']:
            img['pos'] = np.abs(img['pos']) * s_cf
               
        xmax = np.max(rr)
        xmin = 0.0
        ymin = np.min(mn)
        ymax = np.max(mx)
    
        fig = plt.figure(**STY['figure_rect'])
        ax = fig.add_subplot(1,1,1)
    
        # the x coords of this transformation are data, and the
        # y coord are axes
        trans = transforms.blended_transform_factory(
            ax.transData, ax.transAxes)
    
        
        ax.plot(rr, da, **STY['fg_line1'])
        ax.fill_between(rr, mx, mn, **STY['fg_area1'])
    

        xx = SIMS[asw]['x']
        yy = SIMS[asw]['y']
        ax.plot(xx, yy, **STY['fg_line2'])


        ax.axhline(1, **STY['bg_line'])

        
        rE_mean = getEinsteinR(rr, da)
        rE_min  = getEinsteinR(rr, mn)
        rE_max  = getEinsteinR(rr, mx)
        
        print_rE = True
        if not rE_mean:
            # print "ALERT!!!! did not found an rE.. we should handle this.."
            # rE_mean = xmax/2
            print_rE = False
    
        if print_rE:
            #rE_pos = max(round(ymax*0.75), 3)
            
            ax.axvline(rE_mean, 0, rEpos, **STY['fg_line3'])
            
            if rE_mean > 0.75*xmax:
                ha = "right" 
            elif rE_mean < 0.5*xmax:
                ha = "left"
            else:
                ha = "center" 
            
            lbl = r'$\Theta_\mathrm{E} = {%4.2f} \; {} ' % rE_mean
            if rE_min:
                lbl += r'_{{} - {%4.2f}} ' % (rE_mean-rE_min)
            else:
                lbl += r'_{?}'
    
            if rE_max:
                lbl += r'^{+ {%4.2f}}' % (rE_max-rE_mean)
            else:
                lbl += r'^{?}'
                
            lbl += r'$'
    
            # print lbl
            ax.text(
                rE_mean+t_dx, rEpos,
                lbl,
                transform=trans,
                horizontalalignment=ha,
                **STY['text']
            )
    
        
        #append the max in 0/0
        #m['images'].append({'pos':0+0j, 'type':'max', 'angle':0})
        SET.plot_image_positions(ax, m['images'] + [{'pos':0,'type':'max'},] )

        kw1 = dict(STY['bigtickslabel'])
        kw1.update({
            'top': False
        })
        kw2 = dict(STY['smallticks'])
        kw2.update({
            'labelleft': True
        })
        ax.tick_params(axis='both', **kw1)
        ax.tick_params(axis='both', **kw2)
    
        #plt.tight_layout()
        ax.set_ylim(bottom=0.51, top=7.9)
        ax.set_yscale('log')    
        
        ddxx = np.max(rr) * 0.05
        ax.set_xlim(left=-ddxx, right=np.max(rr)+ddxx)
        
    
        plt.xlabel(r'image radius [px]', **STY['label'])
        plt.ylabel(r'$\kappa_{<R}$ [1]', **STY['label'])
    
        formatter = mpl.ticker.FuncFormatter(
            lambda x, p: str(int(round(x))) if x>=1 else str(round(x,1))
        )
        ax.yaxis.set_major_formatter(formatter)
        ax.yaxis.set_minor_formatter(formatter)
    
        plt.tight_layout()
        
        if DBG:
            plt.show()
            break
        
        plt.savefig(imgname, **STY['figure_save'])
        
        plt.close()

    if DBG:
        break





