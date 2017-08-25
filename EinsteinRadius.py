#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 18:01:49 2017

@author: rafik
"""

import numpy as np
from scipy import optimize, interpolate


def getEinsteinR(x, y):
    # poly = interpolate.PiecewisePolynomial(x,y[:,np.newaxis])
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
