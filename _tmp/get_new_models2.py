# coding: utf-8
import requests as rq


r1 = rq.get('http://swlabs:8080/db/spaghetti/_design/isfinal/_view/isfinal')

rows = r1.json()['rows']

data = {}
for row in rows:
    mid = row['id']
    lensid = row['value']['lens_id']
    r2 = rq.get('http://swlabs:8080/db/lenses/'+lensid)
    asw = r2.json()['metadata']['zooniverse_id']
    cdate = row['value']['created_at']
    
    data[mid] = {
    
        'type' : 'brandnew',
        'asw': asw,
        'cdate': cdate


        'gls_ver'     : int(     glsv    ),
        'lmt_ver'     : str(     lmtv    ),
        'pixscale'    : float(   pxscale ),
        'user'        : unicode( user    ).strip(),
        'pixrad'      : int(     pixrad  ),
        'n_models'    : int(     nmodel  ),
        'z_src_used'  : float(   zsrc    ),
        'z_lens_used' : float(   zlens   ),
        'created_on'  : str(     created_on)

        
        }
