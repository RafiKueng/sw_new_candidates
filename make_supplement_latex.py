#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 06 14:11:53 2017

@author: rafik
"""


from __future__ import unicode_literals

import os
import sys
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
ALL_MODELS = CRDA.ALL_MODELS
from create_data import LENS_CANDIDATES as LENSES


DBG = SET.DEBUG
DBG = True
DBG_swid = "SW02"


fpath = join(S['output_dir'], "supplement_latex")
fpath2 = join(S['output_dir'])
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


from itertools import tee, islice, chain, izip

# http://stackoverflow.com/questions/1011938/python-previous-and-next-values-inside-a-loop
def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return izip(prevs, items, nexts)


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
TREEdepth = 0


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
        if TREEdepth < len(path)-1: TREEdepth = len(path)-1
        populateTree(path, swidtree)



#
#def printElemOpen(elem, lvl, FH, swid):
##    print "  ITEM:", " "*lvl, "element", mid, lvl
#
#    asw = MAPS['swid2asw'][swid]
#
#    D = {
#        'lvl'  : lvl,
#        'mid'  : elem,
#        'swid' : swid,
#        'asw'  : asw,
#        '_'    : " "*lvl,
#    }
#
#    print "  <div class='mid lvl{lvl}'>ITEM: {_} element {mid}, {lvl} </div>".format(**D)
#    FH.write("""
#<div class="tree lvl{lvl}">
#<span class='mid lvl{lvl}'>
#<span class='elem'>
#<span class="midcap">{mid}</span>
#<a href="spl-input/{swid}_{asw}_{mid}_spl-input.png">
#    <img class="sqimg" src="spl-input/{swid}_{asw}_{mid}_spl-input.png" alt=""/>
#</a>
#<a href="arrival_spaghetti/{swid}_{asw}_{mid}_arrival_spaghetti.png">
#    <img class="sqimg" src="arrival_spaghetti/{swid}_{asw}_{mid}_arrival_spaghetti.png" alt=""/>
#</a>
#</div>
#</div>
#""".format(**D))
#    
#
#def printElemClose(elem, lvl, FH, swid):
#
#    FH.write("""
#</div>
#""")
#    
    

    
    
#
#def printSWID(swid, FH):
##    print "ELEMENT:", swid    
#    print "<div class='swid'>{swid}</div>".format(**{'swid':swid})    
#    
#    D = {
#        'swid': swid,
#    }
#    
#    FH.write("""
#<h1>Lens Candidate {swid}</h1>
#    """.format(**D))
#
#
#
#strTreeOpen = """
#{_}<ul>
#"""
#
#strTreeClose = """{_}</ul>
#"""
#
#strElemOpen = """
#  <li class=''>
#    <div class=''>
#      <span class='midelem'>
#        <span class='midcapt lvl{lvl}'>
#          {mid}<br>
#          <span class='small'>
#            r<sub>pix</sub>: {pixrad}; n<sub>models</sub>: {nmod}<br>
#            user: {user}
#          </span>
#        </span>
#        <span class="mainimgs">
#          <a href="spl-input/{swid}_{asw}_{mid}_spl-input.png"><img class="sqimg" src="thumb/{swid}_{asw}_{mid}_spl-input.png" alt=""></img></a>
#        </span>
#      </span>
#      <span class='midelem details'>
#        <span class="detaillbl">&#x25BE; details &#x25BE;</span>
#        <span class="detailimgs">
#          <a href="kappa_map_interpol/{swid}_{asw}_{mid}_kappa_map_interpol.png"><img class="sqimg" src="thumb/{swid}_{asw}_{mid}_kappa_map_interpol.png" alt=""></img></a>
#          <a href="arrival_spaghetti/{swid}_{asw}_{mid}_arrival_spaghetti.png"><img class="sqimg" src="thumb/{swid}_{asw}_{mid}_arrival_spaghetti.png" alt=""/></a>
#          <a href="kappa_encl/{swid}_{asw}_{mid}_kappa_encl.png"><img class="sqimg" src="thumb/{swid}_{asw}_{mid}_kappa_encl.png" alt=""></img></a>
#        </span>
#      </span>
#    </div>
#"""
#
#strElemClose = """{_}  </li>
#"""
#
#
#def walkTree(tree, lvl, FH, swid):
#
#    
#    D = {
#        'swid' : swid,
#        'asw'  : MAPS['swid2asw'][swid],
#        'lvl'  : lvl,
#        '_'    : "    "*lvl,  # intend
#    }
#    
#    FH.write(strTreeOpen.format(**D))
#
#    
#    for mid, children in tree.items():
#        
#        m = CRDA.ALL_MODELS[mid]
#        D.update({
#            'mid':mid,
#            'pixrad': m['pixrad'],
#            'nmod'  : m['n_models'],
#            'user'  : m['user'],
#        })
#        
#        I = "\n".join( [D['_'] + _ for _ in strElemOpen.split('\n')])
#        FH.write(I.format(**D))
#        
#        #print " "*lvl, "element", mid, lvl
#        #printElemOpen(mid, lvl, FH, swid)
#
#        if len(children) > 0:
#            walkTree(children, lvl+1, FH, swid)
#        # printElemClose(mid, lvl, FH, swid)
#
#        FH.write(strElemClose.format(**D))
#    
#    FH.write(strTreeClose.format(**D))
#        
#






print "output of tree"

#with open(join(fpath2, 'index.html'), 'w') as FH:
#
#    dx = 20 # has to be the same as li margin left and li div padding-left
#    
#    sty = ""
#    for l in range(TREEdepth+1):
#        E = {
#            'lvl': l,
#            'ml': l*dx,
#            'mr': (TREEdepth - l+1)*dx + 200,
#        }
#        sty += ".midcapt.lvl{lvl} {{min-width:{mr}px;}}\n".format(**E)
#    
#    script = r"""
#$( document ).ready(function() {
#  $(".detaillbl").each(function() {
#    $(this).click(function() {
#      $this = $(this);
#      $elem = $this.next()
#      
#      $elem.toggle();
#      
#      console.log("click");
#    });
#  });    
#});
#"""
#    
#    FH.write("""<html>
#<head>
#<style>
#
#ul {{
#    padding: 0;
#    margin: 0;
#    list-style-type: none;
#    position: relative;
#}}
#
#li {{
#    list-style-type: none;
#    border-left: 2px solid #000;
#    margin-left: 20px;
#}}
#
#li div {{
#    padding-left: 20px;
#    position: relative;
#}}
#
#li div::before {{
#    content: '';
#    position: absolute;
#    top: 0;
#    left: -2px;
#    bottom: 50%;
#    width: 0.75em;
#    border: 2px solid #000;
#    border-top: 0 none transparent;
#    border-right: 0 none transparent;
#}}
#
#ul > li:last-child {{
#    border-left: 2px solid transparent;
#}}
#
#
#.midelem {{
#    border: 2px solid #ccc;
#    border-radius: 2em 2em 0 0;
#    display: block;
#    padding: 0.25em;
#    padding-right: 1.0em;
#    background-color: #ccc;
#}}
#
#
#.details {{
#    border-color: #999;
#    border-radius: 0 0 2em 0;
#    border-top: none;
#    margin-bottom: 0.25em;
#    background-color: #999;
#}}
#
#
#.midcapt {{
#    width: 48%;
#    display: inline-block;
#    margin: 0 0 0 0.75em;
#    font-size: 2em;
#    vertical-align: middle;
#}}
#
#.mainimgs {{
#    display: inline-block;
#    width: 48%;
#    text-align: right;
#}}
#
#.sqimg {{
#    display: inline-block;
#    height: 10em;
#    vertical-align: middle;
#}}
#
#.small {{
#    font-size: 0.66em;
#}}
#
#.detaillbl {{
#    display: block;
#    text-align: center;
#}}
#
#.detailsec {{
#    display: hidden;
#}}
#
#.detailimgs {{
#    display: none;
#    margin: auto;
#    width: 100%;
#    text-align: center;
#
#}}
#
#/*
#{lvlstyle}
#*/
#
#</style>
#
#<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
#
#<script>
#{script}
#</script>
#
#</head>
#<body>
#""".format(**{'lvlstyle': sty, 'script':script}))
#    
#    for swid, tree in sorted(TREE.items()):
#        printSWID(swid,FH)
#        walkTree(tree, 0, FH, swid)
#            
#    FH.write("""
#</body>
#</html>
#""")
#
#



"""
\clearpage

\subsection*{Model EUTVAVV6XI}
\label{mod:bb}

\nav
  {\hyperref[mod:aa]{parent}}
  {\cancel{first child}}
  {\hyperref[index]{prev sibling}}
  {\hyperref[index]{next sibling}}


\subsubsection*{Figures}
\begin{figure}[H]
  \centering
  \includegraphics[width=\figlength, keepaspectratio=true]{../output/arrival_spaghetti/SW01_ASW0004dv8_EUTVAVV6XJ_arrival_spaghetti} 
  \includegraphics[width=\figlength, keepaspectratio=true]{../output/arrival_spaghetti/SW01_ASW0004dv8_EUTVAVV6XJ_arrival_spaghetti} 
  \includegraphics[width=\figlength, keepaspectratio=true]{../output/arrival_spaghetti/SW01_ASW0004dv8_EUTVAVV6XJ_arrival_spaghetti} 
  \includegraphics[width=\figlength, keepaspectratio=true]{../output/arrival_spaghetti/SW01_ASW0004dv8_EUTVAVV6XJ_arrival_spaghetti} 
  \includegraphics[width=\figlength, keepaspectratio=true]{../output/arrival_spaghetti/SW01_ASW0004dv8_EUTVAVV6XJ_arrival_spaghetti} 
  \includegraphics[width=\figlength, keepaspectratio=true]{../output/arrival_spaghetti/SW01_ASW0004dv8_EUTVAVV6XJ_arrival_spaghetti} 
\end{figure}


\subsubsection*{Data}
\begin{center}
\begin{tabular}{rd{3.2}cl}
Stellar Mass & 3.245 & $ \cdot 10^{23} $ & $M_\text{sun}$ \\
Halo Mass  & 3.2 & $\cdot 10^{23}$ & \\
\end{tabular}
\end{center}
"""




def printSWID(swid, FH):
    FH.write("""
\section*{%s - Tree of models}
\label{index%s}
""" % (swid, swid) )
    
    
def walkTreeMenu(tree, lvl, FH, swid):
    for mid, children in tree.items():
        FH.write(r"%s \hyperref[mod:%s]{%s}" % ("&"*(lvl+1),mid,mid))
        FH.write("\n")
        if len(children) > 0:
            walkTreeMenu(children, lvl+1, FH, swid)
        


def walkTreeMain(tree, lvl, FH, swid, parent=None):
    
    for prev, curr, nxxt in previous_and_next(tree.items()):
        mid, children = curr
        asw = MAPS['swid2asw'][swid]
        M   = ALL_MODELS[mid]
        

        FH.write(r"""
\clearpage

\subsection*{Model %s}
\label{mod:%s}
""" % (mid,mid) )
        
        #print "!!", prev, curr, nxxt
        pa = r"\hyperref[mod:%s]{parent}"%parent if parent else r"\cancel{parent}"
        fc = r"\hyperref[mod:%s]{first child}" %children.keys()[0] if len(children) > 0 else r"\cancel{first child}"
        ps = r"\hyperref[mod:%s]{prev sibling}" % prev[0] if prev else r"\cancel{prev sibling}"
        ns = r"\hyperref[mod:%s]{next sibling}" % nxxt[0] if nxxt else r"\cancel{next sibling}"
        ix = r"index%s"%swid
        
        FH.write(r"""
\nav{%s}{%s}{%s}{%s}{%s}
""" % (pa, fc, ps, ns, ix))

        
        
        FH.write(r"""
\subsubsection*{Figures}
\begin{figure}[H]
  \centering
""")

        for fg in ["spl-input", "arrival_spaghetti","kappa_map_interpol", "kappa_encl", ]:
            figpath = "../" + fg
            figfn   = "%s_%s_%s_%s" % (swid, asw, mid, fg)
            FH.write(r"""  \includegraphics[width=\figlength, keepaspectratio=true]{%s/%s} 
""" % (figpath, figfn))

#  \includegraphics[width=\figlength, keepaspectratio=true]{../output/arrival_spaghetti/SW01_ASW0004dv8_EUTVAVV6XJ_arrival_spaghetti} 
#  \includegraphics[width=\figlength, keepaspectratio=true]{../output/arrival_spaghetti/SW01_ASW0004dv8_EUTVAVV6XJ_arrival_spaghetti} 
#  \includegraphics[width=\figlength, keepaspectratio=true]{../output/arrival_spaghetti/SW01_ASW0004dv8_EUTVAVV6XJ_arrival_spaghetti} 
#  \includegraphics[width=\figlength, keepaspectratio=true]{../output/arrival_spaghetti/SW01_ASW0004dv8_EUTVAVV6XJ_arrival_spaghetti} 
#  \includegraphics[width=\figlength, keepaspectratio=true]{../output/arrival_spaghetti/SW01_ASW0004dv8_EUTVAVV6XJ_arrival_spaghetti} 

        FH.write(r"""\end{figure}
""")
        


        fdata = []
        fdata.append(r"GLASS pixel radius & %s & & px" % M['pixrad'])
        fdata.append(r"GLASS number of models & %s & & px" % M['n_models'])
        try:
            x = M['z_lens_measured']
            if x == 0: raise ValueError
            x = r"Lens redshift & %.2f & & " % (x)
            fdata.append(x)
            x = 2 # M['z_src_used']
            x = r"Source redshift (assumed) & %.2f & & " % (x)
            fdata.append(x)
        except:
            pass
        try:
            x = LENSES[asw]['m_s_geom']
            x  = ("%.2e" % x).split('e')
            x = r"Stellar Mass & %s & $ \cdot 10^{%s} $ & $\Msun$" % (x[0], int(x[1]))
            fdata.append(x)
        except:
            pass
        try:
            x = M['M(<R)']['data'][-1]
            x  = ("%.2e" % x).split('e')
            x = r"Total Mass & %s & $ \cdot 10^{%s} $ & $\Msun$" % (x[0], int(x[1]))
            fdata.append(x)
        except:
            pass

#        fdata = [
#            r"Stellar Mass & 3.245 & $ \cdot 10^{23} $ & $M_\text{sun}$",
#            r"Stellar Mass & 3.245 & $ \cdot 10^{23} $ & $M_\text{sun}$",
#        ]

        FH.write(r"""
\subsubsection*{Data}
\begin{center}
\begin{tabular}{rd{3.2}cl}
""")   
        for d in fdata: 
            FH.write("  " + d + "\\\\\n")
        
        FH.write(r"""\end{tabular}
\end{center}
 """)
       
        
        #FH.write("%s\n" % mid)
        if len(children) > 0:
            walkTreeMain(children, lvl+1, FH, swid, mid)



with open(join(S['tmpl_dir'], "osup_header.tex"), 'r') as f:
    HEADER = f.read()
with open(join(S['tmpl_dir'], "osup_footer.tex"), 'r') as f:
    FOOTER = f.read()



for swid, tree in sorted(TREE.items()):
    with open(join(fpath, 'osupp_%s.tex'%(swid)), 'w') as FH:
#        FH = sys.stdout
        print "\n\n"+"="*80
        FH.write(HEADER)
        
        
        printSWID(swid,FH)
        FH.write(r"""
\begin{easylist}[itemize]
\ListProperties(Hide=100, Hang=true, Progressive=3ex, Style*={-- })
""")
        walkTreeMenu(tree, 0, FH, swid)
        FH.write(r"\end{easylist}" + "\n")


        walkTreeMain(tree, 0, FH, swid)
       
        FH.write(FOOTER)

