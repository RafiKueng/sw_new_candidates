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

from stelmass.angdiam import sig_factor, dis_factor, kappa_factor


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
    # possibly corrected by newer measurements (corrected_redshifts.txt)
    data['z_lens_measured'] = PACA.DATA[asw]['z_lens']
    data['z_src_measured'] = PACA.DATA[asw].get('z_src', None)

    
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
    
    
    
    

#
# in old version of SpL I painted the orgiginal images (440px^2) to
# a canvas of size 500px^2 and meassured distances there in (pixels / 100)
# and in the original image 1 px = 0.187 arcsec
#   
def correct_scaling(mid):
    
    scf = 440./500*0.187*100
    # version 3 and higher have correct scaling already applied
    if DATA[mid]['gls_ver'] < 3 and DATA[mid]['gls_ver'] >= 0:
        f1 = ( (scf)**2 )
        f2 = scf
    else:
        f1 = 1
        f2 = 1

    print INT*2,'- correcting scaling f=%5.2f' % f1
    
    DATA[mid]['area_scale_fact'] = f1
    DATA[mid]['pixel_scale_fact'] = f2
        
    DATA[mid]['Mtot_ave_scaled'] = DATA[mid]['Mtot_ave_uncorrected'] * f1
    DATA[mid]['Mtot_min_scaled'] = DATA[mid]['Mtot_min_uncorrected'] * f1
    DATA[mid]['Mtot_max_scaled'] = DATA[mid]['Mtot_max_uncorrected'] * f1
        
  

model = {}
def correct_mass(mid):
    global model
    print INT*2,'- correcting mass for redshifts',
    
    model = DATA[mid]  # this is a "pointer", updates should change the orginal as well
    

    zl_actual = model['z_lens_measured']    # from the tex file of SW2 paper
    zs_actual = model['z_src_measured'] or 2.0   # if value 0, "" None, use default of 2.0 for src redshifts
    zl_used = model['z_lens_used']          # from PSAC: the parsed config file
    zs_used = model['z_src_used']           # same here

   
       
    # f_act = sig_factor(zl_actual,zs_actual)
    # f_use = sig_factor(zl_used,zs_used)
    
    # fact = f_act / f_use
    
    # TODO refracture: only save the factors, don't actually calcualte any 
    m_cf = sig_factor(zl_actual,zs_actual) / sig_factor(zl_used,zs_used)
    r_cf = dis_factor(zl_actual,zs_actual) / dis_factor(zl_used,zs_used)
    k_cf  = kappa_factor(zl_used, zs_used)
    

    if zl_actual * zs_actual * zl_used * zs_used > 0:
        model['sig_fact'] = m_cf
        model['dis_fact'] = r_cf
        model['kappa_fact'] = k_cf
    else:
        model['sig_fact'] = None
        model['dis_fact'] = None
        model['kappa_fact'] = None

    
    
    print INT*2,"> zl_act: %4.2f  zl_use: %4.2f  zs_act: %4.2f  zs_use: %4.2f  kappa_fact: %e" % (
        zl_actual,zl_used,zs_actual,zs_used,
        k_cf
    )

    keys = ['Mtot_ave', 'Mtot_min', 'Mtot_max']
    
    if zl_actual * zs_actual * zl_used * zs_used > 0:
        for k in keys:
            org_mass = model[k+'_scaled']
            corr_mass = org_mass * m_cf
            model[k+'_z_corrected'] = corr_mass
            #print INT*2,'> %s: %e -> %e' % (k,model[k+'_scaled'], model[k+'_z_corrected'])
    else:
        for k in keys:
            model[k+'_z_corrected'] = None
        #print INT*2,'> no data available!!'
    print 'DONE (f=%.3f)' % m_cf

    




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

#save_csv(I, csv_fn, DATA, 'mid')
    
print_last_line(I,DATA)

