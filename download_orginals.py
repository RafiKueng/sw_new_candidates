# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 11:47:57 2016

@author: rafik
"""

import sys
import os
import requests
from PIL import Image
from StringIO import StringIO

import parse_candidates as PACA

import settings as _S
from settings import settings as S, INT
from settings import print_first_line, print_last_line, getI


_path = _S.sworg_path
_fn = "%s.png" # placeholder is asw name

DATA = {}

resp = None

def download_from_spacewarps(asws = []):
    
    global resp
    n = len(asws)
    
    for i, asw in enumerate(asws):
        
        orgimg_fn = os.path.join( _path, _fn % asw )

        print I, "%03i/%03i downloading" %(i+1,n), asw
        
        if not os.path.isfile(orgimg_fn):
            print INT, 'downloading'
    
            DATA[asw] = "failed"
            
            # download orginal image
            
            max_file_size = 10*2**20 # 10 MiB
            min_file_size = 10*2**10 # 10 KiB
        
            s = requests.Session()
        
            try:
                resp = s.get("https://api.zooniverse.org/projects/spacewarp/talk/subjects/"+asw)
            except:
                print INT, 'remote database not available'
                continue
            print INT, resp
            if resp.status_code >= 400 or len(resp.text) ==0:
                print INT, 'remote database returned 404 or nothing'
                continue
                
            json = resp.json()
        
            # check if the provided link is valid and/or maybe redirect
            try:
                resp2 = s.get(json['location']['standard'])
            except:
                print INT, 'resource / img not available'
                continue
        
            if int(resp2.headers['content-length']) <= min_file_size: #images should be at least 10kiB to be valid
                print INT, 'resource / img too small to be an image'
                continue
            elif int(resp2.headers['content-length']) > max_file_size:
                print INT, 'resource / img too big'
                continue
                
            
            urls = []
            for r in [resp2] + resp2.history:
                urls.append(r.url)
            
            try:
                orginal_image = Image.open(StringIO(resp2.content))
            except:
                print INT, 'not an valid image'
                continue
            
            orginal_image.save(orgimg_fn)
            DATA[asw] = "done"
        else:
            print INT, 'already present'
            DATA[asw] = "present"
    
    print I, "demanded:", n
    print I, "got     :", len([1 for _ in DATA.values() if _=='done'])
    print I, "failed  :", len([1 for _ in DATA.values() if _=='failed'])
    print I, "present :", len([1 for _ in DATA.values() if _=='present'])


### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)


if len(sys.argv)>1:
    sys.argv.pop(0)
    items = sys.argv
    download_from_spacewarps(items)

else:
    download_from_spacewarps(PACA.DATA.keys())
    
print_last_line(I, DATA)

