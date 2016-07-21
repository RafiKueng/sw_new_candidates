# -*- coding: utf-8 -*-
"""
Gives access to the candidates list from the paper

if needed, parse the tex file and save it as a csv and pickle.
if pickle already exists, use the pickle instead..

importable, use it like:

import candidates
candidates.by['swid']

candidates.by['swid'][swid][prop]

Created on Mon Jun  8 02:38:54 2015

@author: rafik
"""

import os, sys
from os.path import join

from settings import settings as S, INT, save_pickle, load_pickle, save_csv
from settings import print_first_line, print_last_line, getI, del_cache


DATA = {}
MAP = {}
_c_list = []


def load_tex():
    print I, 'load_tex'
    
    with open(input_fn) as f:
        lns = f.readlines()
        
    for line in lns:
        line = line.strip().strip('\\')
        line = line.replace('\,', ' ')
        line = line.replace('$-$', '-')
        line = line.replace('$+$', '+')
        tkns = line.split('&') 
        tkns = [_.strip() for _ in tkns]
        tkns[0] = "SW%02i" % int(tkns[0][2:])
        #candidates.append(tkns)

        asw = tkns[8]
        swid = tkns[0]
        
        c1, c2 = tkns[10].split(',')
        
        d = {
            'swid':   str(tkns[0]),
            'name':   str(tkns[1]),
            'RA':     float(tkns[2]),
            'dec':    float(tkns[3]),
            'z_lens': float(tkns[4]),
            'm_i':    float(tkns[5]),
            'R_E':    float(tkns[6]),
            'G':      float(tkns[7]),
            'asw':    str(tkns[8]),
            'P':      float(tkns[9]),
            'comments1': str(c1),
            'comments2': str(c2)
        }
        
        DATA[asw] = d
        MAP[swid] = asw
        MAP[asw] = swid
        
        print INT,'loaded', asw, swid #, d
    
    print I,"Status: parsed %i candidates" % len(DATA.keys())



def load_corrections():
    print I, 'load_corrections'
    
    with open(corrections_fn) as f:
        lns = f.readlines()
        
    for l in lns:
        if len(l)<=0 or l.strip().startswith('#'):
            continue
        es = l.split(',')
        es = [_.strip() for _ in es]
        if len(es)>3 or len(es)<2:
            continue
        swid = es[0]
        zlens = float(es[1] or 0)
        zsrc  = float(es[2] or 0)

        asw = MAP[swid]
        
        DATA[asw].update({
            'z_lens': float(zlens),
            'z_src':  float(zsrc),
        })
        print I, "applied correction for ", asw
  





### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)

input_fn  = join(S['input_dir'], 'candidates.tex')
corrections_fn  = join(S['input_dir'], 'corrected_redshifts.txt')
pickle_fn = join(S['cache_dir'], 'candidates.pickle')
csv_fn    = join(S['temp_dir'],  'candidates.csv')


if len(sys.argv)>1:
    if '-d' in sys.argv: del_cache(I,pickle_fn)
    print I,"DONE"
    sys.exit()
        

if os.path.isfile(pickle_fn):
    DATA,MAP = load_pickle(I, pickle_fn)
else:
    load_tex()
    load_corrections()
    save_pickle(I, pickle_fn, (DATA,MAP))

save_csv(I, csv_fn, DATA, 'asw')
    
print_last_line(I, DATA)

