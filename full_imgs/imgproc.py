# -*- coding: utf-8 -*-
"""
Created on Thu Feb  5 00:03:30 2015

@author: rafik
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Feb  4 23:53:08 2015

@author: rafik
"""

from PIL import Image
from os import path

pf = '_'

for i in range(12800):
    
    si = "%06i_input.png" % i
    s1 = "%06i_img1.png" % i
    s2 = "%06i_img2.png" % i
    s31 = "%06i_img3.png" % i
    s32 = "%06i_img3_ipol.png" % i

    if not path.isfile(s1):
        continue
    
    print "working on %06i"%i

    skip = False
    if path.isfile(s32):
        isnew = True
        s3 = s32
    elif path.isfile(s31):
        isnew = False
        s3 = s31
    else:
        skip = True


    ii = Image.open(si)
    ii = ii.crop([172, 62, 477+172, 477+62])
    ii.save(pf+si)

    i1 = Image.open(s1)
    i1 = i1.crop([172, 62, 477+172, 477+62])
    i1.save(pf+s1)


    i2 = Image.open(s2)
    if isnew:
        i2 = i2.crop([172, 62, 477+172, 477+62])
    else:
        i2 = i2.crop([38, 20, 190, 172])
    i2.save(pf+s2)


    if not skip:
        i3 = Image.open(s3)
        i3 = i3.crop([172, 62, 477+172, 477+62])
        i3.save(pf+s3)
        
    
    
    