#!/usr/bin/env python 

import json
import sys


for x in range(1, len(sys.argv)):

    fn = sys.argv[x]
    mid = ".".join(fn.split(".")[0:-1])
    
    print fn, mid
    
    data = json.load(open(fn))
    txt = data['obj']['gls']    
    txt=txt.replace("tmp_media/000000/", "tmp_media/%s/" % mid)
    
    with open('../'+fn, 'w') as f:
        f.write(txt)
    
