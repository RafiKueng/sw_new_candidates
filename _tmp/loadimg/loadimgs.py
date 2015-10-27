# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 08:53:59 2015

@author: rafik
"""

import cPickle as pickle
from os.path import join, isfile, isdir, islink, split, splitext
from os import symlink, makedirs
import sys
import requests as rq
from PIL import Image


with open('nicedata.pickle', 'rb') as f:
    nicedata = pickle.load(f)
    
with open('all_data.pickle', 'rb') as f:
    all_data = pickle.load(f)

by_swid = {}
by_asw = {}    

# only slect newest
if True:
    tmpp = {}
    for mid, adata in all_data.items():
        asw = adata['asw'] 
        dat = adata['created_on']
    
        if adata['Mtot_ens_ave_z_corrected'] == 0.0:
            continue
       
        if tmpp.has_key(asw):
            if tmpp[asw]['created_on'] < dat: # if current newer than previous
                tmpp[asw] = adata
        else:
            tmpp[asw] = adata
    
    selected_models = {}
    
    for asw, data in tmpp.items():
        selected_models[data['mid']] = data
        by_swid[data['swid']] = data
        by_asw[data['asw']] = data



for asw,v in nicedata['asw'].items():
    swid = v['swid']
    try:
        mid = by_asw[asw]['mid']
    except:
        print swid, asw, "has no mid assigned!!!"
        continue
    typ = by_asw[asw]['type']
    
    print "\n", swid, asw, mid, "... getting images:"
    
    imgdir = join("outp")
    
    if not isdir(imgdir):
        makedirs(imgdir)
    
    # get all the results
    
    
    for img in ['input.png', 'img3_ipol.png', 'img3.png', 'img1.png', 'img2.png']:
        print '   getting', mid, img,

        if typ == "new":
            url = "http://labs.spacewarps.org/media/spaghetti/%s/%s/%s" % (mid[0:2],mid[2:], img)
        elif typ == "old":
            url = 'http://mite.physik.uzh.ch/result/' + '%06i/' % int(mid) + img
        else:
            print "ERROR!!!!"
            continue

        path = join(imgdir, "%s_%s_%s" % (swid, mid, img))

        if isfile(path):
            print 'SKIPPING (already present)'
            continue

        r = rq.get(url, stream=True)
        
        if r.status_code >= 300: # reuqests takes care of redirects!
            print 'ERROR:', r.status_code
            continue

        if 'content-type' in r.headers and 'json' in r.headers['content-type']:
            print 'ERROR: no valid png file (json)' 
            continue

        with open(path, 'w') as f:
            for chunk in r.iter_content(1024*4):
                f.write(chunk)
        print 'written,',
        
        if not img == 'input.png' or True:
            i1 = Image.open(path)
            i1 = i1.crop([172, 62, 477+172, 477+62])
            i1.save(path)
            print "cut,",
        print 'done'


j = 0

with open(join(imgdir, 'list.tex'), 'w') as tex:

    t = r"""    
\documentclass[a4paper]{article}

\usepackage{graphicx}
\usepackage{placeins}
\begin{document} 
   
"""
    tex.write(t)
 
    for swid,v in sorted(nicedata['swid'].items()):
        asw = v['asw']
        try:
            mid = by_asw[asw]['mid']
        except:
            print swid, asw, "has no mid assigned!!!"
            continue
#        try:
#            mid = "%6i" % int(mid)
#        except:
#            pass
        typ = by_asw[asw]['type']
        
        t  = '\n' + swid + '\n'
        t += r"\begin{figure}[h]" + '\n'
        
        tex.write(t)

        for i, img in enumerate(['input.png', 'img3_ipol.png', 'img1.png', 'img2.png']):
            #print i
            #path = join('panels', "%s_%s_%s" % (swid, mid, img))
            path = "%s_%s_%s" % (swid, mid, img)
            fact = 0.19
            
            t = "  \includegraphics[width=%s\linewidth]{%s}\n" % (fact, path)
            
            tex.write(t)
        
        path = join("massplts", asw, "%s.png" % mid)
        t  = "  \includegraphics[width=%s\linewidth]{%s}\n" % (fact, path)
        t += r"\end{figure}\FloatBarrier" + '\n'
        
        if j>3:
            t += r'\newpage' +'\n'
            j = 0
        else:
            j += 1
        
        tex.write(t)
        
    
    t = r"""    
\end{document}    
"""
    tex.write(t)    




     
#crop = {
#    'input.png': [55, 20, 207, 172],
#    'img3_ipol.png': ,
#    'img3.png':,
#    'img1.png':      [55, 20, 207, 172],
#    'img2.png':      [55, 20, 207, 172],
#    }
#
#print "edit files":
#
#    s1 = "%06i_img1.png" % i
#    s2 = "%06i_img2.png" % i
#    s31 = "%06i_img3.png" % i
#    s32 = "%06i_img3_ipol.png" % i
#
#    if not path.isfile(s1):
#        continue
#    
#    print "working on %06i"%i
#
#    skip = False
#    if path.isfile(s32):
#        isnew = True
#        s3 = s32
#    elif path.isfile(s31):
#        isnew = False
#        s3 = s31
#    else:
#        skip = True
#
#    i1 = Image.open(s1)
#    i1 = i1.crop([55, 20, 207, 172])
#    i1.save(s1)
#
#    i2 = Image.open(s2)
#    if isnew:
#        i2 = i2.crop([55, 20, 207, 172])
#    else:
#        i2 = i2.crop([38, 20, 190, 172])
#    i2.save(s2)
#
#
#    if not skip:
#        i3 = Image.open(s3)
#        i3 = i3.crop([55, 20, 207, 172])
#        i3.save(s3)
#        

