

import os, sys, csv
import cPickle as pickle

#import numpy as np
from numpy import ndarray, log10
from scipy.interpolate import interp1d
#import matplotlib.pyplot as pl

from os.path import join

from settings import settings as S, INT

from parse_candidates import DATA as candidates


NAME = os.path.basename(__file__)
I = NAME + ":"


pickle_fn  = join(S['cache_dir'], 'stellar_masses.pickle')
csv_fn     = join(S['temp_dir'],  'stellar_masses.csv')

input_fn   = join(S['input_dir'], 'Rafael_salp.dat')


DATA = {}

zl = []
msjr = []
mssr = []

def get_stellar_masses(input_fn=input_fn):
    
    print I,'generating stellar masses'

    with open(input_fn) as fil:
        lyst = fil.readlines()[13:]

    z = ndarray(shape=len(lyst))
    jr = 0*z
    sr = 0*z

    for i in range(len(lyst)):
        v = lyst[i].split()
        v = [float(s) for s in v]
        z[i] = v[0]
        jr[i] = v[3] - 2.5*log10(v[4])
        sr[i] = v[5] - 2.5*log10(v[6])
    
    magjr = interp1d(z,jr)
    magsr = interp1d(z,sr)
    
    
    for asw, lensdata in sorted(candidates['asw'].items()):
        swid = lensdata['swid']
        zp = lensdata['z_lens']
        mag = lensdata['m_i']
        
        print INT,"%10s (%s):   " % (asw,swid),

        if zp !=0 and mag != 0:
            zl.append(zp)
            logm = (magjr(zp)-mag)*0.4
            msjr = 10**(logm)
            logm = (magsr(zp)-mag)*0.4
            mssr = 10**(logm)

        else:
            print "SKIP (missing values; zlens:%8.2e mag:%8.2e)" % (zp,mag)
            continue

        v = (msjr * mssr)**0.5 # geom.mean

        DATA[asw] = {
            'm_s_geom': v,
            'm_s_jr'  : msjr,
            'm_s_sr'  : mssr,        
        }
        
        print "DONE",
        print '(%9.2e %9.2e)' % (msjr,mssr)
        
    print I,"got %i lenses" % len(DATA.keys())
        
    return
        
        


##############################################################################


def save_pickle():
    print I, 'save data to cache (pickle)',
    with open(pickle_fn, 'wb') as f:
        pickle.dump(DATA, f, -1)
    print "DONE"
        
def load_pickle():
    print I, 'load cached data from pickle',
    with open(pickle_fn, 'rb') as f:
        p = pickle.load(f)
    print "DONE"
    return p

def save_csv(pkey_n = 'asw'):
    print I, 'save_csv',

    with open(csv_fn, 'w') as f:
        
        # get all available keys
        keys = set([pkey_n])
        for v in DATA.values():
            keys.update(v.keys())

        # write output
        csvw = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        csvw.writeheader()
        for pkey, v in DATA.items():
            d=dict()
            d.update({pkey_n:pkey})
            d.update(v)
            csvw.writerow(d)

    print "DONE"


### MAIN #####################################################################

print I, "START\n"

if len(sys.argv)>1:

    if '-d' in sys.argv:
        print I,"deleting cache and quitting"
        try:
            os.remove(pickle_fn)
        except OSError:
            pass

    print I,"DONE"
    sys.exit()
        

if os.path.isfile(pickle_fn):
    DATA = load_pickle()
    save_csv()
    
else:
    get_stellar_masses()
    save_pickle()
    save_csv()

print '\n',I, "FINISHED\n\n" + '-'*80 + '\n'

