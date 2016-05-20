# -*- coding: utf-8 -*-
"""
This corrects various things that are wrong in the raw data extracted
from the models / config files in `parse_state_and_config.py`


data basis is what was parsed from the config files
additions should be made from other data sources


Created on Thu Oct 29 11:30:31 2015

@author: rafik
"""



import sys, os
from os.path import join

from settings import settings as S, INT, save_pickle, load_pickle, save_csv
from settings import print_first_line, print_last_line, getI, del_cache

import filter_models as FIMO
import parse_candidates as PACA
import parse_state_and_config as PSAC       # make sure:
                                            # 1) this if first run in glass env..
                                            # 2) load this last of all modules

from stelmass.angdiam import sig_factor, dis_factor, z_to_D


DATA = {}


def sanitise():
    print I,"main start"
    
    DATA.update(PSAC.DATA)
    
    for mid in DATA.keys():

        print INT,"working on %s" % mid
        
        collect_data(mid)
        correct_scaling(mid)
        correct_mass(mid)
 


    
def collect_data(mid):
    '''
    add data collected from other sources
    (like the model listings from the server, aka gom and gnm aka FIMO)
    '''
    print INT*2,'- collecting addidtional data',

    data = {}

    # add the mid.. sometimes it's useful if youo know your name ;)
    data['mid'] = mid

    # add the asw id from FIMO
    asw = FIMO.DATA[mid]['asw']
    data['asw'] = asw
    
    # add the real/messured redshift of the lens from PACA (candidates.tex)
    data['z_lens_meassured'] = PACA.DATA[asw]['z_lens']
    
    # add the created_on time for old models from the server (it's not in the
    # config, and thus not in PSAC)
    if not DATA[mid]['created_on']: # of None
        data['created_on'] = FIMO.DATA[mid]['created_on']
    
    if False:
        print INT*3,"(",
        for k,v in data.items():
            print '%s: %s;' % (str(k), str(v)),
        print ')',
    
    DATA[mid].update(data)
    print "DONE"
    
    
    
    

    
scale_fact = 440./500*0.187
def correct_scaling(mid):
    

    # version 3 and higher have correct scaling already applied
    if DATA[mid]['gls_ver'] < 3 and DATA[mid]['gls_ver'] >= 0:
        f = ( (scale_fact*100)**2 )
    else:
        f = 1

    print INT*2,'- correcting scaling f=%5.2f' % f
    
    DATA[mid]['scale_fact'] = f
        
    DATA[mid]['Mtot_ave_scaled'] = DATA[mid]['Mtot_ave_uncorrected'] * f
    DATA[mid]['Mtot_min_scaled'] = DATA[mid]['Mtot_min_uncorrected'] * f
    DATA[mid]['Mtot_max_scaled'] = DATA[mid]['Mtot_max_uncorrected'] * f
        
  

model = {}
def correct_mass(mid):
    global model
    print INT*2,'- correcting mass for redshifts',
    
    model = DATA[mid]  # this is a "pointer", updates should change the orginal as well
    

    zl_actual = model['z_lens_meassured']
    zs_actual = 2.0                 #!!!!!!!!! source redshifts not yet available, using estimate
    zl_used = model['z_lens_used']
    zs_used = model['z_src_used']

   
       
    f_act = sig_factor(zl_actual,zs_actual)
    f_use = sig_factor(zl_used,zs_used)
    fact = f_act / f_use
    
    # TODO refracture: only save the factors, don't actually calcualte any 
    m_cf = sig_factor(zl_actual,zs_actual) / sig_factor(zl_used,zs_used)
    r_cf = dis_factor(zl_actual,zs_actual) / dis_factor(zl_used,zs_used)
    

    if zl_actual * zs_actual * zl_used * zs_used > 0:
        model['sig_fact'] = m_cf
        model['dis_fact'] = r_cf
    else:
        model['sig_fact'] = None
        model['dis_fact'] = None

    Dl_a, Ds_a, Dls_a = z_to_D(zl_actual, zs_actual)
    Dl_u, Ds_u, Dls_u = z_to_D(zl_used, zs_used)
    
    D = {
        'l'  : {'actual': Dl_a,  'used':Dl_u},    
        's'  : {'actual': Ds_a,  'used':Ds_u},    
        'ls' : {'actual': Dls_a, 'used':Dls_u},    
    }
    model['D'] = D
    
    
    
#    print INT*2,"> zl_act: %4.2f  zl_use: %4.2f  zs_act: %4.2f  zs_use: %4.2f  f1: %e  f2: %e" % (
#        zl_actual,zl_used,zs_actual,zs_used,
#        f_act, f_use
#    )

    keys = ['Mtot_ave', 'Mtot_min', 'Mtot_max']
    
    if zl_actual * zs_actual * zl_used * zs_used > 0:
        for k in keys:
            org_mass = model[k+'_scaled']
            corr_mass = org_mass * fact
            model[k+'_z_corrected'] = corr_mass
            #print INT*2,'> %s: %e -> %e' % (k,model[k+'_scaled'], model[k+'_z_corrected'])
    else:
        for k in keys:
            model[k+'_z_corrected'] = None
        #print INT*2,'> no data available!!'
    print 'DONE (f=%.3f)' % fact

    




### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)

pickle_fn  = join(S['cache_dir'], 'sane_data.pickle')
csv_fn     = join(S['temp_dir'],  'sane_data.csv')

if len(sys.argv)>1:
    if '-d' in sys.argv: del_cache(I,pickle_fn)
    print I,"DONE"
    sys.exit()
        

if os.path.isfile(pickle_fn):
    DATA = load_pickle(I, pickle_fn)
else:
    sanitise()
    save_pickle(I, pickle_fn, DATA)

save_csv(I, csv_fn, DATA, 'mid')
    
print_last_line(I,DATA)

