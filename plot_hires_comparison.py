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
from settings import getI, INT


import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

import scipy.interpolate as interp
import scipy.optimize as optimize

#import create_data as CRDA
import parse_candidates as PACA


DBG = SET.DEBUG

fpath     = join(S['output_dir'], 'hires_comparison')
filename = "{_[asw]}_{_[mid]}_hires_comparison_{_[mode]}." + SET.imgext


# txt data of simulations
sims_dir = join(S['input_dir'], 'hires/systems')
pckl_dir = join(S['input_dir'], 'hires/pickles')

# rE text label position
rEpos = 0.68 # in axes coordinates
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












def draw_multiple_models(elems):




    plt.close("all")
  
    plot_rE = True
    print_rE = True
    prnt = False
    show = False
   
    mid = elems[11]['mid']
    asw = elems[11]['asw']
    user = elems[11]['author']

    save_fig_path = os.path.join(moddir, '%06i'%mid)
      
    if prnt:
        print '...drawing modelling result', mid, asw, user
    else:
        print '> drawing modres %06i'%mid,
  

    try:
        sims[asw]
    except KeyError:
        print '\n!! missing sims data for', mid, asw
        return

    if plot_rE or print_rE:
#        rE_mean = getEinsteinR(elems['x'], elem['y'])
        #rE_max = spg.getEinsteinR(elem['x'], elem['err_p'])
        #rE_min = spg.getEinsteinR(elem['x'], elem['err_m'])
        rE_data = getEinsteinR(sims[asw]['x'], sims[asw]['y'])

    # plotting settings
    ############################

    #where (y val) to start plotting the extr points markers
    #mmax = np.max([np.max(elem['err_p']), np.max(sims[name]['y'])])
    #ofs = max(round(mmax*0.5), 2) 
    #rE_pos = max(round(mmax*0.75), 3) # there to draw the einsteinradius text
    
    # yvals_extr = np.logspace(np.log10(3.5),np.log10(1),8)
    ypos_theta = np.logspace(np.log10(7),np.log10(5),4)

    # yvals_extr = np.logspace(np.log10(3),np.log10(0.7),8)
    ypos_theta = np.logspace(np.log10(5),np.log10(3.5),4)
    
    # text offsets and properties
    t_dx = 0.0
        

    fig = plt.figure(**kw.kappaenc.figure)
    ax = fig.add_subplot(1,1,1, **kw.kappaenc.addsub)

#    for yd, el in elem.items():

    x    = elems[11]['x_edge']
    # y    = elem['y']
    # yp = elem['err_p']
    # ym = elem['err_m']
    
    # get interpolated values
    # x_ip    = np.linspace(np.min(x), np.max(x), 1000)
    # y_ip    = np.interp(x_ip, x, y)
    # yp_ip = np.interp(x_ip, x, yp)
    # ym_ip = np.interp(x_ip, x, ym)
    
    # genrate mask, only values between the extr. points
    # pnts_x = [_['d'] for _ in elem['pnts'] ]
    # mask = (x_ip > np.min(pnts_x)) & (x_ip < np.max(pnts_x))
    
    #plot the model values
    #plt.plot(elem['x'], elem['err_p'], **kw.kappaenc.model)
    #plt.plot(elem['x'], elem['err_m'], **kw.kappaenc.model)
    
    for yd, ele in elems.items():
        param = defaults.copyAD(kw.kappaenc.model)
        i = yd // 10
        j = yd % 10
        ds = np.array([4,1,] + [1,1] * i + [4,1] + [1,1] * j) * 2
        param.update({'color': 'blue' , 'dashes':ds })
        plt.plot(ele['x_edge'], ele['kRe_med'], **param)

    # plt.fill_between(x_ip[mask], yp_ip[mask], ym_ip[mask], **kw.kappaenc.modelface)

    #plot vertical lines for point location
#    for jj, p in enumerate(sorted(elem['pnts'])):
#        plt.plot( [p['d'], p['d']], [0.01,yvals_extr[jj]], **kw.kappaenc[p['t']] )
#        plt.text( p['d'] + t_dx, yvals_extr[jj], r'$\text{%s}$' % p['t'], **kw.kappaenc.text )

    # plot simulation parameter data
    plt.plot(sims[asw]['x'], sims[asw]['y'], **kw.kappaenc.sim)
    plt.plot([0.01,np.max(x)], [1,1], **kw.kappaenc.unity)    
    
       
    # plot einsteinradius
    if plot_rE:

        # a_re_mean = np.array([rE_mean, rE_mean])
        a_re_data = np.array([rE_data, rE_data])
        
        # new placement due to logscale
        # plt.plot(a_re_mean, [0.001,ypos_theta[2]], **kw.kappaenc.rEmod)
        # plt.text(rE_mean+t_dx, ypos_theta[2], r'$\Theta _\text{E,rec} = %4.2f$'%(rE_mean), **kw.kappaenc.text)

        # new placement due to log scale
        plt.plot(a_re_data, [0.001,ypos_theta[0]], **kw.kappaenc.rEsim)
        plt.text(rE_data+t_dx, ypos_theta[0], r'$\Theta_\text{E,act} = %4.2f$'%(rE_data), **kw.kappaenc.text)

    
    plt.xlabel(r'image radius [pixels]', **kw.kappaenc.label)
    plt.ylabel(r'mean convergance [1]', **kw.kappaenc.label)
    
    plt.tick_params(axis='both', which='both', **kw.kappaenc.ticklabel)
    plt.tight_layout()
    
    plt.xlim([0,np.max(x)])
#    plt.xlim([0,15])
    plt.ylim([0.7,14])
    formatter = mpl.ticker.FuncFormatter(lambda x, p: '$'+str(int(round(x)))+'$' if x>=1 else '$'+str(round(x,1))+'$')
    
    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.set_minor_formatter(formatter)
    
    if show:
        plt.show()

    else:
        # new style direct image names \figs_new\mod\001234_kappa_encl.ext
        # save as png and pdf anyways
        imgname = ('_kappa_encl.%s'%repr(exts)) #only for debug message print on screen

        for ext in exts:
            imgname1 = ('_kappa_encl.%s'%ext)
            plt.savefig(os.path.join(save_fig_path + imgname1), **kw.kappaenc.savefig)
        pass

    print ' ... DONE.'
    print '    - %s' % imgname








def getEinsteinR(x, y):
    poly = interp.PiecewisePolynomial(x,y[:,np.newaxis])
    
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

#for mode, dd in DATA.values()[0].items():
for i in range(1):

    mode = 11
    dd = DATA.values()[0][mode]
    
    mid = dd['mid']
    asw = dd['asw']

    print asw, mid
    
    if not mid:
        print "   no mid, skipping"
        continue
    
    #imgname = join(fpath, "%s_%s_kappa_encl.png" % (asw, mid))
    imgname = join(fpath, filename.format(_={'asw':asw, 'mid':mid, 'mode':mode }))
    
    m = dd
    
    # load correcting factors
    try:
        s_cf = m['scale_fact'] # corrects wrong pixel scaling
        m_cf = m['sig_fact']   # corrects masses for wrong redshifts
        r_cf = m['dis_fact']   # corrects lengths for wrong redshifts
        k_cf = m['kappa_fact']
    except:
        s_cf, m_cf, r_cf, k_cf = [1,1,1,1]

    # m['kappa(<R)'] is actually kappa_infty!
    # kappa = D_ls / D_s * kappa_infty
    
    print "      ",s_cf, m_cf, r_cf, k_cf
    
    if not m_cf:
        print "   no redshifts given, skipping"
        continue

    rr = m['R']['data']
    da = m['kappa(<R)']['data'] * k_cf
    mn = m['kappa(<R)']['min']  * k_cf
    mx = m['kappa(<R)']['max']  * k_cf
    
    xmax = np.max(rr)
    xmin = 0.0
    ymin = np.min(mn)
    ymax = np.max(mx)

    fig = plt.figure(**STY['figure_sq'])
    ax = fig.add_subplot(1,1,1)

    # the x coords of this transformation are data, and the
    # y coord are axes
    trans = transforms.blended_transform_factory(
        ax.transData, ax.transAxes)

    
    #ax.plot(rr, mn, 'b')
    #ax.plot(rr, mx, 'b')
    ax.plot(rr, da, **STY['fg_line1'])
    ax.fill_between(rr, mx, mn, **STY['fg_area1'])


    #plt.plot([xmin,xmax], [1,1], 'k:')  
    ax.axhline(1, **STY['bg_line'])

    rE_mean = getEinsteinR(rr, da)
    rE_min  = getEinsteinR(rr, mn)
    rE_max  = getEinsteinR(rr, mx)
    #a_re_mean = np.array([rE_mean, rE_mean])
    
    print_rE = True
    if not rE_mean:
        # print "ALERT!!!! did not found an rE.. we should handle this.."
        # rE_mean = xmax/2
        print_rE = False

    if print_rE:
        rE_pos = max(round(ymax*0.75), 3)
        
        #plt.plot(np.array([rE_mean, rE_mean]), [0,rE_pos], '--', color=(0,0.5,0))
        ax.axvline(rE_mean, 0, rEpos, **STY['fg_line2'])
        
        if rE_mean > 0.75*xmax:
            ha = "right" 
        elif rE_mean < 0.25*xmax:
            ha = "left"
        else:
            ha = "center" 
        
        lbl = r'$r_{\Theta} = {%4.2f} \; {} ' % rE_mean
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
            **STY['text'])

    
    #append the max in 0/0
    #m['images'].append({'pos':0+0j, 'type':'max', 'angle':0})
    
    SET.plot_image_positions(ax, m['images'] + [{'pos':0,'type':'max'},] )


    ax.tick_params(axis='both', which='both', **STY['ticks'])


    #plt.tight_layout()
    ax.set_ylim(bottom=0.5, top=8)
    ax.set_yscale('log')    
    
    ddxx = np.max(rr) * 0.05
    ax.set_xlim(left=-ddxx, right=np.max(rr)+ddxx)
    

    plt.xlabel(r'image radius [arcsec]', **STY['label'])
    plt.ylabel(r'$\kappa_{<R}$ [1]', **STY['label'])

    formatter = mpl.ticker.FuncFormatter(
        lambda x, p: str(int(round(x))) if x>=1 else str(round(x,1))
    )
    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.set_minor_formatter(formatter)

    plt.tight_layout()
    
    plt.savefig(imgname, **STY['figure_save'])

    if DBG:
        plt.show()
        break
    
    plt.close()





