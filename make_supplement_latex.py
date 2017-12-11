#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 06 14:11:53 2017

@author: rafik
"""


from __future__ import unicode_literals

from contextlib import contextmanager
import subprocess as SP
import glob
import os
import sys
from os.path import join
import PIL

import settings as SET
reload(SET)
SET.set_mpl_rc()
STY = SET.styles
S = SET.settings


import create_data as CRDA
import parse_candidates as PACA

from EinsteinRadius import getEinsteinR

import Image


#MODELS, MAPS = CRDA.get_dataset_data()
MODELS, MAPS = CRDA.get_dataset_data('all_models')
ALL_MODELS = CRDA.ALL_MODELS
from create_data import LENS_CANDIDATES as LENSES


DBG = SET.DEBUG
#DBG = True
#DBG_swid = "SW02"


imgstypes = [
    'spl-input',
    "org_synth_img",
    'arrival_spaghetti',
    'kappa_map_interpol',
    'kappa_encl',
    ]

OUTDIR = join('output','supplement_latex')
LATEXTMPEXTS = ['log',
                'aux',
                'out',
                #'synctex.gz'
                ]

fpath = join(S['output_dir'], "supplement_latex")
imgssubpath = "imgs"
imgpath = join(S['output_dir'], "supplement_latex", imgssubpath)
#fpath2 = join(S['output_dir'])
#filename = SET.filename_base % "kappa_map_interpol"

if not os.path.exists(fpath):
    os.makedirs(fpath)
if not os.path.exists(imgpath):
    os.makedirs(imgpath)


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

from itertools import tee, islice, chain, izip


def clean_tmplatex():
    for ext in LATEXTMPEXTS:
        files = glob.glob(join(OUTDIR, '*.%s' % ext))
        for f in files:
            SP.call(['rm', f])

def clean_pdf():
    for ext in ['pdf']:
        files = glob.glob(join(OUTDIR, '*.%s' % ext))
        for f in files:
            SP.call(['rm', f])

stout = ""
sterr = ""
def create_pdf(cleanup=True):
    global stout, sterr
    with cd(OUTDIR):
        files = glob.glob('*.tex')
        for f in sorted(files):
            print f
            # run it twiche because of the labels
            # SP.call(['pdflatex', '-interaction=nonstopmode', f])
            with open(os.devnull, "w") as null:
                SP.call(['pdflatex', '-interaction=nonstopmode', f], stdout=null)
            p = SP.Popen(['pdflatex', '-interaction=nonstopmode', f],
                         stdin=SP.PIPE, stdout=SP.PIPE, stderr=SP.PIPE)
            stout, sterr = p.communicate()
            lines = stout.split('\n')
            for l in lines:
                if "! LaTeX Error" in l:
                    print l

            #return lines
            if cleanup:
                #print "cleaning up latex temp files"
                for ext in LATEXTMPEXTS:
                    SP.call(['rm', f[:-3]+ext])
                #break
            
        # additional compression
        print "additional compression"
        for swid in []: # ["SW01",]:
            print swid
            SP.call(['gs',
                     '-sDEVICE=pdfwrite',
                     '-dCompatibilityLevel=1.4',
                     '-dPDFSETTINGS=/ebook',
                     '-dNOPAUSE',
                     '-dQUIET',
                     '-dBATCH',
                     '-sOutputFile=osupp_%s_.pdf'%swid,
                     'osupp_%s.pdf'%swid])

size = 512,512
def create_imgs():
    #imgpath
    for cat in imgstypes:
        files = None
        with cd(join(S['output_dir'], cat)):
            #print cat
            fls = '*.' + SET.imgext
            files = glob.glob(fls)
            #print fls, files
        for f in files:
            infile = join(S['output_dir'],cat,f)
            outfile = join(imgpath,f[:-3]+'jpeg')
            print infile, outfile
            im = PIL.Image.open(infile)
            im.thumbnail(size, Image.ANTIALIAS)
            im.convert("RGB").save(outfile, "JPEG")  # convert from RGBA to RGB for jpeg
            #break

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
    print swid, len(mids)

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


print "output of tree"


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
        


def splitexp(x):
    return tuple(("%.2e" % x).split('e'))

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

        for fg in imgstypes:
#            figpath = "../" + fg
#            figfn   = "%s_%s_%s_%s" % (swid, asw, mid, fg)
#            FH.write(r"""  \includegraphics[width=\figlength, keepaspectratio=true]{%s/%s} 
#""" % (figpath, figfn))
            figpath = imgssubpath
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
        

        m_rcf = M['sig_fact']
        k_rcf  = M['kappa_fact']

        fdata = []
        fdata.append(r"GLASS pixel radius & %s & & px" % M['pixrad'])
        fdata.append(r"GLASS number of models & %s & &" % M['n_models'])
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
            m_stel = LENSES[asw]['m_s_geom']
            m_stel_jr = LENSES[asw]['m_s_jr']
            m_stel_sr = LENSES[asw]['m_s_sr']
            
#            print m_stel, splitexp(m_stel)
#            print r"Stellar Mass & %s & $ \cdot 10^{%s} $ & $\Msun$" % (splitexp(m_stel))
            
            fdata.append(r"Stellar Mass & %s & $ \cdot 10^{%s} $ & $\Msun$" % (splitexp(m_stel)))
            fdata.append(r"Stellar Mass (young) & %s & $ \cdot 10^{%s} $ & $\Msun$" % (splitexp(m_stel_jr)))
            fdata.append(r"Stellar Mass (old) & %s & $ \cdot 10^{%s} $ & $\Msun$" % (splitexp(m_stel_sr)))

        except KeyError:
            pass
        except:
            raise
        try:
#            x = M['M(<R)']['data'][-1]
#            x  = ("%.2e" % x).split('e')
#            x = r"Total Mass & %s & $ \cdot 10^{%s} $ & $\Msun$" % (x[0], int(x[1]))
#            fdata.append(x)

            m_lens = M['M(<R)']['data'][-1] * m_rcf # usually called m_lens in the pipeline
            m_lens_max = M['M(<R)']['max'][-1] * m_rcf
            m_lens_min = M['M(<R)']['min'][-1] * m_rcf

            fdata.append( r"Total Mass & %s & $ \cdot 10^{%s} $ & $\Msun$" % (splitexp(m_lens)))
            fdata.append( r"Total Mass (max) & %s & $ \cdot 10^{%s} $ & $\Msun$" % (splitexp(m_lens_max) ))
            fdata.append( r"Total Mass (min) & %s & $ \cdot 10^{%s} $ & $\Msun$" % (splitexp(m_lens_min) ))

        except:
            raise

        try:
            if M['z_corrected']:
                
    
                m_lens = M['M(<R)']['data'][-1] * m_rcf # usually called m_lens in the pipeline
                m_lens_max = M['M(<R)']['max'][-1] * m_rcf
                m_lens_min = M['M(<R)']['min'][-1] * m_rcf
                
                rr = M['R']['data']
                da = M['kappa(<R)']['data'] * k_rcf
                rE = "%.2f" % getEinsteinR(rr, da)

                x = r"Einstein Radius $r_\text{E}$ & %s & & arcsec" % (rE)
                fdata.append(x)
        except:
            pass

        
        if M['type']=='old':
            lnk = "http://mite.physik.uzh.ch/data/%s" % mid
        else:
            lnk = "http://labs.spacewarps.org/spaghetti/model/%s" % mid
        fdata.append(r"\multicolumn{4}{c}{\href{%s}{see orginal}}" % lnk)

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


#create_imgs()
#create_pdf()


