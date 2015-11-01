# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 23:24:40 2015

@author: rafik
"""

import os
from os.path import join

import numpy as np

from settings import settings as S, getI, INT

import get_spaghetti_images as GSIM
import plot_masses as PLMA

from create_data import ONLY_RECENT_MODELS as MODELS, LENS_CANDIDATES as LENSES
from parse_candidates import MAP as ASW2SWID, MAP as SWID2ASW


path     = join(S['output_dir'], 'tex', 'overview')
filename = 'overview.tex'

if not os.path.exists(path):
    os.makedirs(path)

path_massplots = join(path,'masses')
path_spaghetti = join(path,'spaghetti')

print path_massplots
print PLMA.path

if not os.path.exists(path_massplots):
    os.symlink(join('..','..','..',PLMA.path), path_massplots)
if not os.path.exists(path_spaghetti):
    os.symlink(join('..','..','..',GSIM.imgdir), path_spaghetti)

I = getI(__file__)


with open(join(path, filename), 'w') as tex:
    
    tex.write(r'''
\documentclass[a4paper]{article}

\usepackage{graphicx}
\usepackage{placeins}
\begin{document}

\section{Quick Overview}

''')

    w = 0.19
        
    for label, _ in sorted(PLMA.data.items()):
        swid = _['swid']
        asw = _['asw']
        mid = _['mid']
        
        tex.write('\n'+r"  \subsection{%s %s %s}" % (asw, swid, mid) + '\n')
        
        if os.path.exists(join(path_spaghetti, "%s_%s_img3_ipol.png" % (asw, mid))):
            i3n = "img3_ipol.png"
        else:
            i3n = "img3.png"
        
        for i, img in enumerate(['input.png', i3n, 'img1.png', 'img2.png']):
            p1 = join('spaghetti', "%s_%s_%s" % (asw, mid, img))
            tex.write(r"  \includegraphics[width=%s\linewidth]{%s}" % (w, p1) + '\n')

        p2 = join('masses', "%s_%s_%s_mstel_vs_mtot.png" % (swid, asw, mid))
        tex.write(r"  \includegraphics[width=%s\linewidth]{%s}" % (w, p2) + '\n')
        
        
    tex.write("""
\end{document}    
    """)
        
    