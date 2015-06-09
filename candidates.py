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
import cPickle as pickle

pickle_filename = 'candidates.pickle'
csv_filename = 'candidates.csv'

candidates = {}
_c_list = []

def load_tex():
    print 'candidates.py: load_tex'

    candidates['asw'] = {}
    candidates['swid'] = {}

    with open('candidates.tex') as f:
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
    print 'candidates.py: save_pickle'
    with open('candidates.pickle', 'w') as f:
        pickle.dump(candidates, f, -1)
        
def load_pickle():
    print 'candidates.py: load_pickle'
    with open('candidates.pickle') as f:
        return pickle.load(f)

def save_csv():
    print 'candidates.py: save_csv'

    with open('candidates.csv', 'w') as f:
        for tkns in _c_list:
            f.write(','.join(tkns)+'\n')

### MAIN #####################################################################

if os.path.isfile(pickle_filename):
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