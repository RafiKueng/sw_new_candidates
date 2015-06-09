# -*- coding: utf-8 -*-
"""

Created on Wed May 27 17:20:02 2015

@author: rafik
"""

import requests as rq
import os


new_models = []
    
def fetch_talk():

    models = []
    
    page = 1
    acomms = {}
    
    while True:

        print "scanning pg", page
        url = "https://api.zooniverse.org/projects/spacewarp/talk/boards/BSW0000006/discussions/DSW0000eo1?page=%i" % page
        
        acomms[page] = {}
        
        resp = rq.get(url)
        
        try:
            comms = resp.json()['comments']
        except KeyError:
            break

        if len(comms) < 1:
            break
        
        print ".. found n comments:", len(comms)
        
        for i, comm in enumerate(comms):
            acomms[page][i]=comm
            txt = comm['body']
            lines = txt.split('\n')
            
            mdl = ''
            swid = ''
            asw = ''
            usr = comm['user_name']
            
            for line in lines:
                parts = line.split('-')
                if len(parts) == 3:
                    if '***Revised' in parts[1]:
                        mdl = parts[2].strip()
                        if len(mdl.split(']('))>1:
                            mdl = mdl.split('](')[0][1:]
                        if len(mdl)<10:
                            mdl = '%06i' % int(mdl)
                        elif len(mdl)>10:
                            mdl=''
                    if '***SW ID' in parts[1]:
                        sswid = parts[2].strip().split(" ")
                        for s in sswid:
                            if s.startswith('#'):
                                swid = s[1:]
                            if s.startswith('ASW'):
                                asw += s + ' '
                            if s.startswith('[ASW'):
                                asw = s.split('](')[0][1:]
            
            if not mdl=='':
                asw=asw.strip()
                usr = usr.strip(' \n')
                models.append([mdl, asw, swid, usr])
                print "    comm", i
                print "       model:", mdl
                print "       usr  :", usr
                print "       swid :", swid
                print "       asw  :", asw
        page = page + 1

    new_models = models
    return models, acomms



def write_models():
    models = new_models
    with open('tmp1_new_models.csv', 'w') as f:
        for m in models:
            f.write(','.join(m)+'\n')
  



def collect_all_models():
    
    tmp = []
    models = []
    
    with open('tmp0_old_models.csv') as f:
        lns = f.readlines()
    for ln in lns:
        tmp.append(ln.strip())

    with open('tmp1_new_models.csv') as f:
        lns = f.readlines()
    for ln in lns:
        tmp.append(ln.strip())
        
    for t in tmp:
        _ = t.split(',')
        if _[0].startswith('0'):
            typ = 'old'
        else:
            typ = 'new'
        
        for i in range(8-len(_)): #fill up empty columns
            _ = _ + ['',]
            
        print typ, _
        models.append([_[0],typ] + _[1:])

    with open('tmp2_all_models.csv', 'w') as f:
        for _ in models:
            f.write(','.join(_)+'\n')


    
    
    