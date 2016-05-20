# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 10:22:51 2016

@author: rafik
"""

import pyperclip
import create_data as CRDA
from create_data import ALL_MODELS as MODELS, LENS_CANDIDATES as LENSES
import parse_candidates as PACA


with open('input/eval.txt', 'r') as f:
    lns = f.readlines()

dd = {}    
for l in lns:
    if l.startswith('SW'):
        _ = l[:-1].split(',') # remove \n
        d = [x.strip(' *') for x in _[1:]] # remove review marker and white space used for formating
        for i, j in enumerate(d):
            if j.startswith('y'):
                d[i] = '\OK'
            elif j.startswith("n"):
                d[i] = '\NO'
        if len(d)>=6:
            dd[_[0]] = d
        else:
            print "%s: no complete record found" % (_[0],)
            dd[_[0]] = ['']*6

ss = r"""
\begin{tabular}{c c c | c c | c c c | c c c}
  \hline
  SWID & ASW id & model id
  
    & \rot{$z_\text{lens}$}

    & \rot{\shortstack[l]{image\\morphology}}
    
    & \multicolumn{1}{|l|}{\rot{\shortstack[l]{unblended\\images}}}
    & \rot{\shortstack[l]{all images\\discernible}}
    & \rot{\shortstack[l]{isolated\\ lens}}
    
    & \rot{\shortstack[l]{synthetic image\\ reasonable}}
    & \rot{\shortstack[l]{mass map\\ reasonable}}
    & \rot{\shortstack[l]{total vs stellar\\ mass ratio}}
  \\ \hline
"""

for swid, asw in sorted(CRDA.MAPS['swid2asw'].items()):
    
    mid = CRDA.MAPS['swid2model'].get(swid, "")
    
    aswobj = PACA.DATA[asw]
    #CRDA.ALL_MODELS[mid]
    
    
    name = aswobj['name'].split(' ')[1]

    zL = ""    
    
    if mid:
        m_stellar = LENSES[asw].get('m_s_geom', None)
        m_lens = MODELS[mid]['Mtot_ave_z_corrected']

        zL = "%s" % MODELS[mid]['z_lens_meassured']
        
        if m_stellar is not None:
            r = m_lens / m_stellar
            if r<99.:
                m_ratio = '%i'%r
            else:
                m_ratio = '%.1e'%r
        else:
            m_ratio = ""
    else:
        m_ratio = ""

    
    m = {
        'asw':    asw,
        'swid':   swid,
        #'mid':    mid,
        'coords': name,
        'm_ratio': m_ratio,
        'zL' : zL,
        'd0' : dd[swid][0],
        'd1' : dd[swid][1],
        'd2' : dd[swid][2],
        'd3' : dd[swid][3],
        'd4' : dd[swid][4],
        'd5' : dd[swid][5],

    }
    
    s = """  {swid} & {asw} & {coords} & {zL}
    & {d0}
    & {d1} & {d2} & {d3}
    & {d4} & {d5} & {m_ratio} \\\\
    
""".format(**m)

    #print s
    ss += s

ss += """

  \hline

\end{tabular}
"""    
pyperclip.copy(ss)

with open("output/table.tex", "w") as f:
    f.write(ss)

