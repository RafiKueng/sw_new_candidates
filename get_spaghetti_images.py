# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 18:23:58 2015

@author: rafik
"""

from os import makedirs
from os.path import join, isfile, isdir

import requests as rq
from PIL import Image

from settings import settings as S, INT
from settings import print_first_line, print_last_line, getI


from create_data import ALL_MODELS

imgdir = join(S['output_dir'],'images','spaghetti')



### MAIN #####################################################################

def main():
    get_images(ALL_MODELS)


##############################################################################



def get_images(data):
    '''
    Download one set of images for a particular mid
    '''
    
    n_models = len(data.items())
    
    for i, __ in enumerate(data.items()):

        mid,_ = __
        asw = _['asw']
        swid = _.get('swid', "SWXX")
        typ = _['type']
        
        print INT, "(%3.0f%%) gettings images for %-10s (asw: %s swid:%s)" % (100.0*i/n_models, mid, asw, swid)
        
        if not isdir(imgdir):
            makedirs(imgdir)
        
        for img in ['input.png', 'img3_ipol.png', 'img3.png', 'img1.png', 'img2.png']:
            print INT*2, img,
    
            if typ == "new":
                url = "http://labs.spacewarps.org/media/spaghetti/%s/%s/%s" % (mid[0:2],mid[2:], img)
            elif typ == "old":
                url = 'http://mite.physik.uzh.ch/result/' + '%06i/' % int(mid) + img
            else:
                print "ERROR!!!!"
                continue
    
            path = join(imgdir, "%s_%s_%s" % (asw, mid, img))
    
            if isfile(path):
                print 'SKIPPING (already present)'
                continue
    
            r = rq.get(url, stream=True)
            
            if r.status_code >= 300: # reuqests takes care of redirects!
                print 'ERROR:', r.status_code
                continue
    
            if 'content-type' in r.headers and 'json' in r.headers['content-type']:
                print 'ERROR: no valid png file (json)' 
                continue
    
            with open(path, 'w') as f:
                for chunk in r.iter_content(1024*4):
                    f.write(chunk)
            print 'written,',
            
            # cut the image to square, overwriting the orginal
            i1 = Image.open(path)
            if not img == 'input.png':
                i1 = i1.crop([172, 62, 477+172, 477+62])
            else:
                i1 = i1.crop([100, 0, 600+100, 600+0])
            i1.save(path)
            print "cut,",
            print 'done'
            
            


I = getI(__file__)
print_first_line(I)
main()
print_last_line(I)


