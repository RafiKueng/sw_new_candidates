#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 06 14:11:53 2017

@author: rafik
"""


from __future__ import unicode_literals

import os
from os.path import join

import settings as SET
reload(SET)
SET.set_mpl_rc()
STY = SET.styles
S = SET.settings

#import numpy as np
#import matplotlib as mpl
#import matplotlib.pyplot as plt
#import matplotlib.colors
#import matplotlib.transforms as transforms

import create_data as CRDA
import parse_candidates as PACA


#MODELS, MAPS = CRDA.get_dataset_data()
MODELS, MAPS = CRDA.get_dataset_data('all_models')


DBG = SET.DEBUG
DBG = True
DBG_swid=02


fpath = join(S['output_dir'], "supplement")
#filename = SET.filename_base % "kappa_map_interpol"

if not os.path.exists(fpath):
    os.makedirs(fpath)



#if DBG:
#    swidallmid = {
#        'a1' : ["m1%i" % _ for _ in range(3)],
#        'a2' : ["m2%i" % _ for _ in range(3)],
#        'a3' : ["m3%i" % _ for _ in range(3)],
#        'a4' : ["m4%i" % _ for _ in range(3)],
#    }
#    ALLMOD = {}
#    for swid, midlist in swidallmid.items():
#        for mid in midlist:
#            print swid, mid
#            ALLMOD[mid] = {'swid':swid,'parent':''}
#            
#    ALLMOD['m11']['parent'] = 'm10'
#    ALLMOD['m12']['parent'] = 'm11'
#    ALLMOD['m21']['parent'] = 'm20'
#    ALLMOD['m22']['parent'] = 'm20'


def getRoot(mid, path):
    ''' gets the root model and the path to there for each model'''

    path.append(mid)
#    if DBG:
#        m = ALLMOD[mid]
    m = CRDA.ALL_MODELS[mid]

    if 'parent' in m and not m['parent'] == "":
        root, path = getRoot(m['parent'], path)
        return root, path
    else:
        return mid, path

def populateTree(path, loc):
#        print path, '--', loc, '--',
    if len(path)==0:
        return
    e = path.pop()
#        print e
    if e in loc and loc[e]:
        populateTree(path, loc[e])
    else:
        loc[e] = {}
        populateTree(path, loc[e])


TREE = {}

    


for swid, mids in MAPS['swid2mids'].items():
#for swid, mid_list_o in swidallmid.items():
#    asw = CRDA.MAPS['swid2asw']
#    aswobj = PACA.DATA[asw]
    
#    print swid, asw, len(mid_list_o)
    print swid, len(mids)

#    mid_list = mid_list_o.copy()
    mid_list = list(mids)
    swidtree = {}
    TREE[swid] = swidtree
    
    for mid in mid_list:
        print mid
        # problemcase: 007953
#        if DBG and mid in ['007959', '007953',"008009", "007961"]:
#            continue
        
        root, path = getRoot(mid,[])
        print "mid; %s root: %s path: %s" % (mid, root, path)
        populateTree(path, swidtree)



def printElem(elem, lvl):
#    print "  ITEM:", " "*lvl, "element", mid, lvl
    D = {
        'lvl': lvl,
        'mid': elem,
        '_'  : " "*lvl,
    }

    print "  <div class='mid lvl{lvl}'>ITEM: {_} element {mid}, {lvl} </div>".format(**D)

def printSWID(swid):
#    print "ELEMENT:", swid    
    print "<div class='swid'>{swid}</div>".format(**{'swid':swid})    
    

def walkTree(tree, lvl):
    
    for mid, children in tree.items():
        
        #print " "*lvl, "element", mid, lvl
        printElem(mid, lvl)

        if len(children) > 0:
            walkTree(children, lvl+1)


print "output of tree"
for swid, tree in sorted(TREE.items()):
    printSWID(swid)
    walkTree(tree, 0)
            




#
#for swid, asw in sorted(CRDA.MAPS['swid2asw'].items()):
#    
#    mid = MAPS['swid2mid'].get(swid, "")
#
#    print swid, asw, mid
#    
#    if not mid:
#        print "   no mid, skipping"
#        continue
#    
#    if DBG and not swid==DBG_swid: continue
#    
#    #imgname = join(fpath, "%s_%s_kappa_encl.png" % (asw, mid))
#    imgname = join(fpath, filename.format(_={'asw':asw, 'mid':mid,'swid':swid}))
#    
#    m = CRDA.ALL_MODELS[mid]
#    aswobj = PACA.DATA[asw]
#
#
#
#for swid, asw in sorted(CRDA.MAPS['swid2asw'].items()):
#    
#    print swid, asw
#    
#    #mid = CRDA.MAPS['swid2model'].get(swid, "")
#    mid = MAPS['swid2mid'].get(swid, "")
#    
#    if not mid:
#        print "   no mid, skipping"
#        continue
#
#    m = CRDA.ALL_MODELS[mid]
#    aswobj = PACA.DATA[asw]
#
#
