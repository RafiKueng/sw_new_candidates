#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This is a cleaned up, all in one rewrite of lucys paramter fitting

needs glass to run.


Created on Sun Aug 21 22:15:26 2016

@author: rafik
"""


import os
from os.path import join

import settings as SET
reload(SET)
SET.set_mpl_rc()
STY = SET.styles
S = SET.settings

import numpy as np
#import matplotlib
#import matplotlib.pyplot as plt

import scipy.optimize as opt                #for the least squares fit


import create_data as CRDA
import parse_candidates as PACA

MODELS = CRDA.CLAUDE_MODELS

DBG = SET.DEBUG
DBG =True

itemname = "parameterized"
fpath = join(S['output_dir'], itemname)
filename = SET.filename_base % itemname

if not os.path.exists(fpath):
    os.makedirs(fpath)



    

"""ellip"""

"""This program imports the lens data and calculates the parameterised form of
the mass distribution for an isothermal ellipsoid from the functional form of 
the gravitational potential. It also defines N, R and maximgpos such that 
parameters are given in the correct units. For use with mass_ellip or readmass"""

#mname = 'for_paper/convincing/ASW0002asp/5EKMWWVJHL'

#fil = open(mname+'.pkl')
#chutney = pickle.load(fil) 

#ensem = chutney['grids']                                    #ensem = the ensemble of 200 free-form mass distributions for the lens
#pixrad = chutney['pixrad']                                  #pixrad = radius in number of pixels
#N = 2*pixrad+1
#R = chutney['maprad']                                       #maprad = radius from central point to central point of outer tile (in arcseconds)
#maximgpos = chutney['maximgpos']


# See eqns (33-35) from Keeton astro-ph/0102341
def poten_SIE(x,y,reinst,ell,ell_pa):                       #parameterised function for isothermal ellipsoid
    pa = (ell_pa+90)*np.pi/180
    q = np.sqrt((1-ell)/(1+ell))
    reinst *= np.sqrt((1+q*q)/(2*q*q))
    cs,sn = np.cos(pa),np.sin(pa)
    x,y = cs*x + sn*y, -sn*x + cs*y
    A = reinst*q/np.sqrt(1-q*q)
    B = np.sqrt((1-q*q)/(q*q*x*x + y*y + 1e-12))
    phix = A*np.arctan(B*x)
    phiy = A*np.arctanh(B*y)
    return x*phix + y*phiy


# kappa(zl=0.5,zs=1) = 0.4312*kappa_inf(zl=0.5)             #red shift fudge factor


def grid(params):
    reinst,ell,ell_pa = params[0],params[1],params[2]       #defining grav ptl as describing points on a 2D surface (not actually used unless you want graph of grav ptl)
    x = np.linspace(-R,R,N)
    X,Y = np.meshgrid(x,x)
    F = poten_SIE(X,Y,reinst,ell,ell_pa)
    return F


#calculate parameterised functional form of mass distribution
def profile(params):
    reinst,ell,ell_pa = params[0],params[1],params[2]       #parameters: Einstein radius, Ellipticity and Position angle of ellipticity
    S = 3
    r = R + 0.5*(1-1./S)*R/pixrad                           #oversampling, taking care about size of grid
    x = np.linspace(-r,r,N*S)
    X,Y = np.meshgrid(x,-x)                                 #flip y axis
    F = poten_SIE(X,Y,reinst,ell,ell_pa)
    M = 0*F
    M[1:-1,1:-1] = F[2:,1:-1] + F[:-2,1:-1] + F[1:-1,2:] + F[1:-1,:-2] \
                 - 4*F[1:-1,1:-1]                           #taking the second difference of the gravitational potential
    M = M*(pixrad/R)**2 / 2                                     #dividing by "delta(x)^2" to obtain grad^2 of potential i.e. mass distrib.
    K = np.ndarray(shape=(N,N))                             #undersampling again to go back to original grid size
    for i in range(N):
        for j in range(N):
            K[i,j] = np.sum(M[i*S:(i+1)*S,j*S:(j+1)*S])
    return K
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#
# main loop
#

DATA = {}

for swid, asw in sorted(CRDA.MAPS['swid2asw'].items()):
    
    #mid = CRDA.MAPS['swid2model'].get(swid, "")
    mid = CRDA.get_map(MODELS)['swid2model'].get(swid, "")
    aswobj = PACA.DATA[asw]

    print swid, asw, mid
    
    if not mid:
        print "   no mid, skipping"
        continue
    
    
    imgname = join(fpath, filename.format(_={'asw':asw, 'mid':mid,'swid':swid}))
    
    m = CRDA.ALL_MODELS[mid]

    ensem  = m['ensemble']       #ensem = the ensemble of 200 free-form mass distributions for the lens
    pixrad = m['pixrad']         #pixrad = radius in number of pixels
    R      = m['maprad']         #maprad = radius from central point to central point of outer tile (in arcseconds)

    maximgpos = max([ abs(_['pos']) for _ in m['images'] ])
    N = 2*pixrad+1


    # load correcting factors
    # ScaleCorrectionFactors
    px_scf = m['pixel_scale_fact']  # corrects wrong pixel scaling in old version [old_pxl -> arcsec]
    aa_scf = m['area_scale_fact']   # corrects areas due to wrong pixel scaling in old version [old_pxl**2 -> arcsec**2]
    # RedshiftCorrectionFactor
    r_rcf  = m['dis_fact']          # corrects lengths for wrong redshifts
    m_rcf  = m['sig_fact']          # corrects masses for wrong redshifts
    k_rcf  = m['kappa_fact']        # corrects kappa for wrong redshifts

    # m['kappa(<R)'] is actually kappa_infty!
    # kappa = D_ls / D_s * kappa_infty
    
    print "      ",px_scf, aa_scf, r_rcf, m_rcf, k_rcf

    # correct scaling
    R         = R         * px_scf * r_rcf
    maximgpos = maximgpos * px_scf * r_rcf
    

    #defining the data as describing N*N points on a 2D surface in the range -R to R
    x = np.linspace(-R,R,N)
    X,Y = np.meshgrid(x,-x)                     #y axis flipped
    
    
    #define red shift fudge factor
    # fudge = 0.4312
    fudge = k_rcf
    
    #*****************************
    """Calculate inertia tensor"""
    #*****************************
    
    #calculate mean of ensemble
    for m in range(len(ensem)):
        ensem1d = np.reshape(ensem[m],(N**2))   #reshape 2D array as 1D array 
        ensem1d = fudge*ensem1d                 #multiply by the fudge factor for red shift
        if m==0:    
            sum = ensem1d
        else:    
            sum = sum+ensem1d                   #sum elements in the ensemble
    mean = sum/len(ensem)                       #calculate mean
    
    
    #calculate moment of inertia tensor (a.k.a covariance matrix) and its eigenvectors and eigenvalues
    for m in range(len(ensem)):
        ensem1d = np.reshape(ensem[m],(N**2))   #reshape 2D array as 1D array
        ensem1d = fudge * ensem1d               #multiply by the fudge factor for red shift
        diff = ensem1d - mean                   #delta(k) = datum k - mean <k>
        out = np.outer(diff,diff)               #outer products of pairs of delta(k)
        if m==0:                                #create MoI tensor (outer products of pairs of values)
            outsum = out
        else:
            outsum = outsum + out
    outsum = outsum/len(ensem)                  #scale MoI by tensor size of ensemble (appears to make no difference to output)
    vals,vecs = np.linalg.eigh(outsum)          #find eigenvecs/vals of MoI tensor
    
    
    #*****************************************
    """Define parameterised functional form"""
    #*****************************************
    
    #define masking function for which selects only the data points that are inside the image of the lens
    mask = (1-np.sign(X*X+Y*Y-maximgpos*maximgpos))/2
    mask = np.reshape(mask,(N**2))
    
    
    #define residuals function: parameterised form - mean - projections along principle axes multiplied by the masking function
    def residuals(params):
        f = profile(params)                         #f = k(param)
        f = np.reshape(f,(N**2))                    #reshape f into 1D array
        clip = 2.5
                                      #set clip value to keep inside the region of the ensemble models (between 2 and 3 because Gaussian fit)
        f -= mean                                   #take away the mean
        for m in range(1,11):
            i = np.inner(f,vecs[:,-m])              #clip the principal components
            if i>clip:
                i = clip
            elif i<-clip:
                i = -clip
            f -= i*vecs[:,-m]                       #removing projections along principle axes
        return mask*f                               
    
    #**************************
    """Linear regression fit"""
    #**************************
    
    #set initial parameter values and perform linear regression fit of f to the ensemble
    ini = [1,0.1,0.1]                             #initial values for parameters
    #perform parameter optimisation on residuals
    sol = opt.leastsq(residuals,ini)
    lsq = sol[0]
    cov = sol[1]
    r = residuals(lsq)
    err = np.sum(r*r) / (N*N) * cov
    
    #Print out parameters
    param1 = lsq[0]
    param2 = lsq[1]
    param3 = lsq[2]
    #print 'Einstein radius = {0:.3}, Ellipticity = {1:.3}, Position angle of ellipticity = {2:.3}'.format(param1,param2,param3) #prints values of optimised parameters
    print ('Least squares parameters')
    print ('%.2f' %param1, '%.2f' %param2, '%.2f' %param3, '%.2f' %err)
    
    d = {'eR': param1, 'ellip': param2, "ell_angle": param3,
        "err": err}
    
    DATA[mid] = d

