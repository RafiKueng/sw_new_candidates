#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 21:14:31 2016

@author: rafik
"""

import os
from os.path import join

import settings as SET
reload(SET)
SET.set_mpl_rc()
STY = SET.styles
S = SET.settings


import create_data as CRDA
import parse_candidates as PACA


MODELS, MAPS = CRDA.get_dataset_data('selected_models')
ALL_MODELS = CRDA.ALL_MODELS

DBG = SET.DEBUG
#DBG =True

itemname = "data"
fpath = join(S['output_dir'])
filename = "model_assignment.tex"

if not os.path.exists(fpath):
    os.makedirs(fpath)


s1 = ""
s2 = "% Look up table, SWID -> Index:\n"
for swid, asw in sorted(MAPS['swid2asw'].items()):

    mids = MAPS['swid2mids'].get(swid, [])
    
    print swid, asw, mids
    
    if not len(mids)==1:
        print "   to many/little mids??, skipping", len(mids)
        #raise Exception("too many mids")
        continue

    mid = mids[0]
    
    fn = SET.filename_base.format(_={'asw':asw, 'mid':mid,'swid':swid})
    fn = fn[:-7]
    cmd = r"\includegraphics[width=\pwidth]{img/#1/%s_#1}" % (fn,)
    
    swidalph = chr(ord('A')+int(swid[2:3])) + chr(ord('A')+int(swid[3:4]))
    s1 += r"\newcommand{\incl%s}[1]{%s}" % (swidalph, cmd) + "\n"
    s2 += "%% %s %s\n" % (swid[2:4], swidalph )
    
s1 += r"""
\newcommand{\inclGrid}[1]{ %
\inclFI{#1} \inclCI{#1} \inclFH{#1}
\inclAF{#1} \inclEC{#1} \inclBJ{#1}
\inclAJ{#1} \inclCJ{#1} \inclAC{#1}
}
"""
fname = join(fpath, filename)
with open(fname, 'w') as f:
    f.write(s2+"\n"+s1)
    
    
    
    