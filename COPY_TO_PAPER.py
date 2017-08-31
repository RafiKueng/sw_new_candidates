#!/bin/env python2
# -*- coding: utf-8 -*-

import os
from os.path import join

import settings as SET
reload(SET)
S = SET.settings

import create_data as CRDA


filename = SET.filename_base % "kappa_encl"

MODELS, MAPS = CRDA.get_dataset_data()


path_paper = "../paper2"


imgstypes = [
    'arrival_spaghetti',
    'kappa_encl',
    'kappa_map_interpol',
    'spl-input',
    'nsynth'
    ]
    
selected_swids = ['05', '42', '28', '58', '02','19','09','29','57']

selected_swids = [ 'SW'+_ for _ in selected_swids]


files = []

for imgtype in imgstypes:
    
    filename = SET.filename_base % imgtype
    fpathdest = join("img",imgtype)

    for swid in selected_swids:
        
        asw = MAPS['swid2asw'][swid]
        mid = MAPS['swid2mids'][swid][0]

        fn = filename.format(_={'asw':asw, 'mid':mid,'swid':swid})

        files.append((imgtype, fn, fpathdest, fn))


# hires_comparison
for nr in ['11','13','33']:
    dirorg  = 'hires_comparison'
    dirdest = join('img','hires_comparison')
    fn      = 'ASW000102p_6941_%s_hires_comparison.png' % nr

    files.append((dirorg, fn, dirdest, fn))

files.extend([
# rE comp
    (
     "rE_comp",
     "rE_comp.png",
     "img/rE_comp",
     "rE_comp.png"
     ) ,
# mstel_vs_mtot_one
    (
     "mlens_vs_mstel",
     "mlens_vs_mstel.png",
     "img/mlens_vs_mstel",
     "mlens_vs_mstel.png"
     ),
# timelapse
    (
     "timelapse",
     "timelapse3.png",
     "img",
     "timelapse3.png"
     ),
# model_assignment.tex
    (
     "",
     "model_assignment.tex",
     "img",
     "model_assignment.tex"
     ),
# table.tex
    (
     "",
     "table.tex",
     "parts",
     "table.tex"
     ),
# table.tex
    (
     "",
     "table_1.csv",
     "supplemental_material",
     "table_1.csv" 
     )
 ])


for dirorg, fnorg, dirdest, fndest in files:
    if len(dirorg)>0:
        dirorg = join(S['output_dir'], dirorg)
    else:
        dirorg = S['output_dir']
        
    dirdest = join(path_paper, dirdest)
    
    org  = join(dirorg, fnorg)
    dest = join(dirdest, fndest)

    if not os.path.exists(dirdest):
        os.makedirs(dirdest)


    print org, dest 
    ret = os.system("cp %s %s" % (org, dest))
    if not ret == 0:
        print "file not found"
        break



#
#
#single_items = [
## rE comp
#    "output/rE_comp/rE_comp.png %s/img/rE_comp/rE_comp.png" % (path_paper),
## mstel_vs_mtot_one
#    "output/mstel_vs_mtot_one/mstel_vs_mtot_one.png %s/img/mstel_vs_mtot_one/mstel_vs_mtot_one.png" % (path_paper),
## timelapse
#    "output/timelapse/timelapse3.png %s/img/timelapse3.png" % (path_paper),
## model_assignment.tex
#    "cp output/model_assignment.tex %s/img/model_assignment.tex" % (path_paper),
## table.tex
#    "output/table.tex %s/parts/table.tex" % (path_paper),
## table.tex
#    "output/table_1.csv %s/supplemental_material/table_1.csv" % (path_paper),
#]
#
#for s in single_items:
#    print s
#    #os.system("cp "+s)
#
#
#
#
#
#
