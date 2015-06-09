# -*- coding: utf-8 -*-
"""
gets the models mentioned in a thread on talk.spacewarps




Created on Wed May 27 17:20:02 2015

@author: rafik
"""

import requests as rq
import os
import cPickle as pickle

picklename = 'tmp_new_models.pickle'

data = {}
_models = []

def fetch_talk():
    print "get_new_models: fetch talk"

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
                            mdl = int(mdl)
                        elif len(mdl)>10:
                            mdl=''
                    if '***SW ID' in parts[1]:
                        sswid = parts[2].strip().split(" ")
                        for s in sswid:
                            if s.startswith('#'):
                                swid = "SW%02i" % int(s[3:])
                            if s.startswith('ASW'):
                                asw += s + ' '
                            if s.startswith('[ASW'):
                                asw = s.split('](')[0][1:]
            
            if not mdl=='':
                asw=asw.strip()
                usr = usr.strip(' \n')
                _models.append([mdl, asw, swid, usr])
                print "    comm", i
                print "       model:", mdl
                print "       usr  :", usr
                print "       swid :", swid
                print "       asw  :", asw
        page = page + 1

    #return _models



def save_csv():
    print "get_new_models: save_csv"
    with open('tmp_new_models.csv', 'w') as f:
        f.write(','.join(['model', 'asw', 'swid', 'user'])+'\n')
        for m in _models:
            m = [str(_) for _ in m]
            f.write(','.join(m)+'\n')
  

def save_pickle():
    print "get_new_models: save_pickle"
    
    for model in _models:
        mid = model[0]
        
        data[mid] = {
            'asw'  : model[1],
            'user' : model[3],
            'swid' : model[2],
            'mid'  : mid
        }
            
    with open(picklename, 'w') as f:
        pickle.dump(data, f, -1)
        



data = {}

def main():
    fetch_talk()
    save_csv()
    save_pickle()
    


if __name__ == "__main__":
    main()
else:
    if os.path.isfile(picklename):
        print "loaded new models from temp pickle"
        with open(picklename) as f:
            data = pickle.load(f)
    else:
        main()
        



    
    