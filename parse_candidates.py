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

import os
from os.path import join
import cPickle as pickle

from settings import settings as S

NAME = os.path.basename(__file__)
I = NAME + ":"


input_fn  = join(S['input_dir'], 'candidates.tex')
pickle_fn = join(S['cache_dir'], 'candidates.pickle')
csv_fn    = join(S['temp_dir'],  'candidates.csv')


candidates = {}
_c_list = []


def load_tex():
    print I, 'load_tex'
    
    candidates['asw'] = {}
    candidates['swid'] = {}

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
        
        candidates['asw'][asw] = d
        candidates['swid'][swid] = d
        _c_list.append(tkns[:10]+[c1,c2])
        
        print '   loaded', asw, swid, d



def save_pickle():
    print I, 'save data to cache (pickle)'
    with open(pickle_fn, 'wb') as f:
        pickle.dump(candidates, f, -1)
        
def load_pickle():
    print I, 'load cached data from pickle'
    with open(pickle_fn, 'rb') as f:
        return pickle.load(f)

def save_csv():
    print I, 'save_csv'

    with open(csv_fn, 'w') as f:
        for tkns in _c_list:
            f.write(','.join(tkns)+'\n')

### MAIN #####################################################################

if os.path.isfile(pickle_fn):
    candidates = load_pickle()
    
else:
    load_tex()
    save_pickle()
    save_csv()

# nice shortcut.. if imported, use it like
#
by = candidates
get_swid = dict([(k,v['swid']) for  k,v in by['asw' ].items()])
get_asw =  dict([(k,v['asw' ]) for  k,v in by['swid'].items()])