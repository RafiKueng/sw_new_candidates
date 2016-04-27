# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 23:35:52 2016

@author: rafik
"""
import json
import numpy as np

with open('assets/models/AJIBCHQ6EM.cfg') as f:
    d = json.load(f)
    

# here we have the input values in pixels send from client to server:
j2 = json.loads(d['obj']['jsonStr'])
ui = j2['Sources'][0]
print ui

# we find the following pixel values that the user generated (on 500x500)
SAD0 = np.array([ui['x'], ui['y']])
MAX0 = np.array([ui['child1']['x'], ui['child1']['y']])
SAD1 = np.array([ui['child2']['x'], ui['child2']['y']])
MIN0 = np.array([ui['child2']['child1']['x'], ui['child2']['child1']['y']])
MIN1 = np.array([ui['child2']['child2']['x'], ui['child2']['child2']['y']])

# i used gimp to get these (on 440x440)
g_max0 = np.array([178,52])
g_sad0 = np.array([191, 65])
g_sad1 = np.array([153, 55])


# this is the glass file used to run glass (relative to center-> MAX)
print d['obj']['gls']

A = np.array([0.885, 5.242])   # MIN1
B = np.array([-4.211, -2.383]) # MIN0
C = np.array([-4.703, -0.266]) # SAD1
D = np.array([2.421, -2.094])  # SAD0


# we applied the following scaling relations from pixel to arcsec
# pxScale = orgPxScale / svgViewportSize * orgImgSize
# 0.16456 = 0.187 / 500 * 444
ops = d['obj']['orgPxScale']
vps = d['obj']['svgViewportSize']
ois = d['obj']['orgImgSize']
pxs = d['obj']['pxScale']


# do some sanity checks

# check scaling relation
assert np.abs(pxs - ( ops / vps * ois ) ) < 1e-6

# check sanity of input (compuare to manual messurement)
assert np.all( np.abs( (g_max0*1.0 / ois * vps) - MAX0)  < 2.0 ) # less than 2 pixel different 

# check input to glass in arcsec
assert np.all( np.abs((SAD1 - MAX0) * pxs) - np.abs(C) < 1e-3 )

# show the distances from the center
print 'dist to center (arcsec)', [np.sqrt(np.sum(_**2)) for _ in [A,B,C,D]]




state = loadstate('assets/models/AJIBCHQ6EM.state')
state.make_ensemble_average()
model = state.ensemble_average
obj, data = model['obj,data'][0]
