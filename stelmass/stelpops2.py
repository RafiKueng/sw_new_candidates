
import numpy as np
from numpy import ndarray, log10
from scipy.interpolate import interp1d
import matplotlib.pyplot as pl


zl = []
msjr = []
mssr = []

def bla(fnn = 'Rafael_salp.dat'):

    data_asw = {}
    data_sw = {}
    fil = open(fnn)
    lyst = fil.readlines()[13:]
    z = ndarray(shape=len(lyst))
    jr = 0*z
    sr = 0*z
    for i in range(len(lyst)):
        v = lyst[i].split()
        v = [float(s) for s in v]
        z[i] = v[0]
        jr[i] = v[3] - 2.5*log10(v[4])
        sr[i] = v[5] - 2.5*log10(v[6])
    
    magjr = interp1d(z,jr)
    magsr = interp1d(z,sr)
    
    with open('candidates.csv') as f:
        lyst = f.readlines()
    
    for lyne in lyst:
        v = lyne.strip().split('\t')
        id = v[0]
        zp = float(v[4])
        mag = float(v[5])
        asw = v[8]
        print asw,id,
        if zp !=0 and mag != 0:
            zl.append(zp)
            logm = (magjr(zp)-mag)*0.4
            msjr.append(10**(logm))
            logm = (magsr(zp)-mag)*0.4
            mssr.append(10**(logm))
            print msjr[-1],mssr[-1]
            a = msjr[-1]
            b = mssr[-1]
        else:
            print
            a = 0
            b = 0

        v = a+b / 2.0
        v_err_lo = a
        v_err_hi = b

        d = (v, v_err_lo, v_err_hi)        
        
        nid =  'SW%02i' % int(id[2:])
        asw = asw.strip()
        data_asw[asw] = d
        data_sw[nid] = d
        
    return data_asw, data_sw
        
        

def do_plot():
    # plot(z,magjr(z))
    # plot(z,magsr(z))
    pl.scatter(zl,msjr,c='g')
    pl.scatter(zl,mssr,c='r')
    pl.axes().set_yscale('log')
    pl.xlabel('redshift')
    pl.ylabel('stellar mass in $M_\odot$')
    pl.show()


