# -*- coding: utf-8 -*-
"""
This corrects various things that are wrong in the raw data extracted
from the models / config files in `parse_state_and_config.py`



Created on Thu Oct 29 11:30:31 2015

@author: rafik
"""



import sys, os, csv
import cPickle as pickle

from os.path import join

from settings import settings as S

import parse_state_and_config as psac     # make sure this if first run in glass env..
import filter_models as fimo
import parse_candidates as paca

from stelmass.angdiam import sig_factor


NAME = os.path.basename(__file__)
I = NAME + ":"
INT = '    '


pickle_fn  = join(S['cache_dir'], 'sane_data.pickle')
csv_fn     = join(S['temp_dir'],  'sane_data.csv')
rawdata_fn = join(S['cache_dir'], 'parsed_state_and_config_files.pickle')


sane_data = {'0000':{'a':1}}
sane_data = {}
rawdata = {}


def sanitise():
    print I, "main start"
    
    sane_data.update(psac.stateconf_data)
    
    for mid in sane_data.keys():

        print I, "working on %s" % mid
        
        collect_data(mid)
        correct_scaling(mid)
        correct_mass(mid)
    

    
def collect_data(mid):
    print INT,'- collecting addidtional data',

    data = {}

    asw = fimo.filt_models[mid]['asw']
    data['asw'] = asw
    data['z_lens_meassured'] = paca.by['asw'][asw]['z_lens']
    
    print INT*2,"(",
    for k,v in data.items():
        print '%s: %s;' % (str(k), str(v)),
    print ')',
    
    sane_data[mid].update(data)
    print "DONE"
    
    
    
    

    
scale_fact = 440./500*0.187
def correct_scaling(mid):
    

    # version 3 and higher have correct scaling already applied
    if sane_data[mid]['gls_ver'] < 3 and sane_data[mid]['gls_ver'] >= 0:
        f = ( (scale_fact*100)**2 )
    else:
        f = 1

    print INT,'- correcting scaling f=%5.2f' % f
        
    sane_data[mid]['Mtot_ave_scaled'] = sane_data[mid]['Mtot_ave_uncorrected'] * f
    sane_data[mid]['Mtot_min_scaled'] = sane_data[mid]['Mtot_min_uncorrected'] * f
    sane_data[mid]['Mtot_max_scaled'] = sane_data[mid]['Mtot_max_uncorrected'] * f
        
  

model = {}
def correct_mass(mid):
    global model
    print INT,'- correcting mass for r'
    
    model = sane_data[mid]  # this is a "pointer", updates should change the orginal as well
    
#    try:
    zl_actual = model['z_lens_meassured']
    zs_actual = 2.0                 #!!!!!!!!! source redshifts not yet available, using estimate
    zl_used = model['z_lens_used']
    zs_used = model['z_src_used']

#    except KeyError:
#        print INT*2,"!!! redshifts not available !!!"
#        return
#        sys.exit(1)
    
       
    f_act = sig_factor(zl_actual,zs_actual)
    f_use = sig_factor(zl_used,zs_used)
    
    print INT*2,"> zl_act: %4.2f  zl_use: %4.2f  zs_act: %4.2f  zs_use: %4.2f  f1: %e  f2: %e" % (
        zl_actual,zl_used,zs_actual,zs_used,
        f_act, f_use
    )

    keys = ['Mtot_ave', 'Mtot_min', 'Mtot_max']
    
    if zl_actual * zs_actual * zl_used * zs_used > 0:
        for k in keys:
            org_mass = model[k+'_scaled']
            corr_mass = org_mass * f_act / f_use
            model[k+'_z_corrected'] = corr_mass
            print INT*2,'> %s: %e -> %e' % (k,model[k+'_scaled'], model[k+'_z_corrected'])
    else:
        for k in keys:
            model[k+'_z_corrected'] = None
        print INT*2,'> no data available!!'

    



##############################################################################

def save_pickle():
    print I, 'save data to cache (pickle)'
    with open(pickle_fn, 'wb') as f:
        pickle.dump(sane_data, f, -1)
        
def load_pickle():
    print I, 'load cached data from pickle'
    with open(pickle_fn, 'rb') as f:
        return pickle.load(f)

def save_csv():
    print I, 'save_csv'

    with open(csv_fn, 'w') as f:

        fieldnames = ['mid',] + sane_data.values()[0].keys()

        csvw = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        csvw.writeheader()
        
        for mid, v in sane_data.items():
            csvw.write(v.update({'mid':mid}))


### MAIN #####################################################################

if len(sys.argv)>1:

    if '-d' in sys.argv:
        print I,"deleting cache and quitting"
        try:
            os.remove(pickle_fn)
        except OSError:
            pass

       
    sys.exit()
        

#if os.path.isfile(pickle_fn):
#    sane_data = load_pickle()
#    save_csv()
#    
#else:
#    sanitise()
#    save_pickle()
#    save_csv()

sanitise()


