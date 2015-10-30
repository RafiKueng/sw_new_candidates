

import os, sys
from os.path import join

from numpy import ndarray, log10
from scipy.interpolate import interp1d

from settings import settings as S, INT, save_pickle, load_pickle, save_csv
from settings import print_first_line, print_last_line, getI, del_cache

import parse_candidates as paca


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
    
    
    for asw, lensdata in sorted(paca.DATA.items()):
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
        
        



### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)

pickle_fn  = join(S['cache_dir'], 'stellar_masses.pickle')
csv_fn     = join(S['temp_dir'],  'stellar_masses.csv')

if len(sys.argv)>1:
    if '-d' in sys.argv: del_cache(I,pickle_fn)
    print I,"DONE"
    sys.exit()
        

if os.path.isfile(pickle_fn):
    DATA = load_pickle(I, pickle_fn)
else:
    get_stellar_masses()
    save_pickle(I, pickle_fn, DATA)

save_csv(I, csv_fn, DATA, 'asw')
    
print_last_line(I,DATA)



