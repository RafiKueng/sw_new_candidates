# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 20:37:05 2016

@author: rafik
"""

import os
from os.path import join, isfile, isdir

import sys
import requests
from PIL import Image
from StringIO import StringIO
import numpy as np

import parse_candidates as PACA
import create_data as CRDA
import get_state_and_config as GSAC # import will trigger download!
import download_orginals as DORG # import triggers download

_ = GSAC.I + DORG.I
del _

from settings import settings as S, INT, save_pickle, load_pickle, save_csv
from settings import print_first_line, print_last_line, getI, del_cache


CRDA.ONLY_RECENT_MODELS
CRDA.ALL_MODELS

GSAC.I # do this to remove unused warnings in IDE

data = ['ASW0007k4r']


for asw in data:
    
    orgimg_fn = "%s_orginal.png" % asw
    
    if not isfile(orgimg_fn):
        print INT, 'downloading file'

        
        # download orginal image
        
        max_file_size = 10*2**20 # 10 MiB
        min_file_size = 10*2**10 # 10 KiB
    
        s = requests.Session()
    
        try:
            resp = s.get("https://api.zooniverse.org/projects/spacewarp/talk/subjects/"+asw)
        except:
            print 'remote database not available'
            continue
        if resp.status_code >= 400 or len(resp.text) ==0:
            print 'remote database returned 404 or nothing'
            continue
            
        json = resp.json()
    
        # check if the provided link is valid and/or maybe redirect
        try:
            resp2 = s.get(json['location']['standard'])
        except:
            print 'resource / img not available'
            continue
    
        if int(resp2.headers['content-length']) <= min_file_size: #images should be at least 10kiB to be valid
            print 'resource / img too small to be an image'
            continue
        elif int(resp2.headers['content-length']) > max_file_size:
            print 'resource / img too big'
            continue
            
        
        urls = []
        for r in [resp2] + resp2.history:
            urls.append(r.url)
        
        try:
            orginal_image = Image.open(StringIO(resp2.content))
        except:
            print 'not an valid image'
            continue
        
        orginal_image.save(orgimg_fn)
    else:
        print INT, 'orginal image file already present'
        orginal_image = Image.open(orgimg_fn)

    org_image = np.array(orginal_image)
    

