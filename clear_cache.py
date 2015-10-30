# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 14:51:33 2015

@author: rafik
"""

import os, shutil
from settings import settings as S


for path in [ S['cache_dir'], S['temp_dir'], S['asset_dir'] ]:
    if os.path.exists(path):
        shutil.rmtree(path)
