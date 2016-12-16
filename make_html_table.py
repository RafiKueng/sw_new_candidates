#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 16:01:30 2016

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
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm

import create_data as CRDA
import parse_candidates as PACA


MODELS = CRDA.CLAUDE_MODELS
mn = "claude"

MODELS = CRDA.ONLY_RECENT_MODELS
mn = "most_recent"

MODELS = CRDA.ALL_MODELS
mn = "all_models"


DBG = SET.DEBUG



itemname = "html_tables"
fpath = join(S['output_dir'], "images")
filename = "%s.html"


#
# main loop
#

imgname = join(S['output_dir'], filename%mn)
print imgname
with open(imgname, 'w') as f:
    
    f.write("""
<html>
<head>
<style>
img {
    height: 200px;
}

</style>
</head>
<body>
<h1>%s</h1>
<table>
""" % mn)
        
    for swid, asw in sorted(CRDA.MAPS['swid2asw'].items()):
        
        #mid = CRDA.MAPS['swid2model'].get(swid, "")
        
        mid = CRDA.get_map(MODELS)['swid2model'].get(swid, "")
        aswobj = PACA.DATA[asw]
    
        print swid, asw, mid
        
        if not mid:
            print "   no mid, skipping"
            continue
    
        m = CRDA.ALL_MODELS[mid]
        
        row = """
<tr>
<td>{_[swid]} {_[asw]}<br>{_[mid]}</td>
<td><img src="images/spaghetti/{_[asw]}_{_[mid]}_input.png" /></td>
<td><img src="images/spaghetti/{_[asw]}_{_[mid]}_img1.png" /></td>
<td><img src="images/spaghetti/{_[asw]}_{_[mid]}_img2.png" /></td>
<td><img src="images/spaghetti/{_[asw]}_{_[mid]}_img3_ipol.png" /></td>
</tr>"""
        row = row.format(_={'asw':asw, 'mid':mid,'swid':swid})
    
        print row
        f.write(row)
    
    f.write("""
</table></body></html>
""")