# -*- coding: utf-8 -*-
"""
download the input image

Created on Sun Nov  1 18:23:58 2015

@author: rafik
"""

from os import makedirs
from os.path import join, isfile, isdir

import settings as SET
reload(SET)
SET.set_mpl_rc()
STY = SET.styles
S = SET.settings


import requests as rq
#from PIL import Image
import numpy as np
#from scipy import ndimage
from scipy import misc
import matplotlib.pyplot as plt


#from settings import settings as S, INT
#from settings import print_first_line, print_last_line, getI

import find_point
import create_data as CRDA

MODELS, MAPS = CRDA.get_dataset_data()

DBG = SET.DEBUG
#DBG = True
#DBG_swid = "SW42"
DBG_swid = "SW31"
#DBG_mid = ["004758", '007350', "EUTVAVV6XJ"]

#imgdir = join(S['output_dir'],'spl_images')


PRINT_CAPTION = True


itemname = "spl-input"
fpath = join(S['output_dir'], itemname)
#filename = "{_[swid]}_{_[asw]}_{_[mid]}_%s." + SET.imgext
filename = SET.filename_base % itemname


OVERRIDE = {
    'SW57': (83.0, np.sqrt(-0.56267**2+1.4179**2))  # meassured from saddle to saddle point
    }



### MAIN #####################################################################

def main():
    return get_images(MODELS)


##############################################################################



def get_images(data):
    '''
    Download one set of images for a particular mid
    '''
    
    n_models = len(data.items())
    
#    for img in [   # all the others than input don't work!
#                'input.png',
#                #'img3_ipol.png', 
#                #'img3.png',
#                #'img1.png',
#                #'img2.png'
#                ]:
#        #print INT*2, img,
#        img_name = img[:-4]

    # this used to be a for loop downloading all the files, but isn't anymore
    # because all the other files are generated in some other way
    img = 'input.png' 
    img_name = img[:-4]
        
    for i, blob in enumerate(sorted(data.items())):

        mid, M = blob
        asw = M['asw']
        swid = M.get('swid', "SWXX")
        typ = M['type']
        isZCorr = M['z_corrected']
        
        if DBG and not swid==DBG_swid:
            #print "skip no swid", swid, DBG_swid
            continue
#        if DBG and not mid in DBG_mid:
#            #print "skip no mid", mid, DBG_mid
#            continue
        
        print "(%3.0f%%) getting %-10s image for mid:%-10s asw:%s swid:%s)" % (100.0*i/n_models, img, mid, asw, swid)
        
        
#        imgdir  = fpath % img_name
#        imgname = join(fpath % img_name, filename.format(_={'asw':asw, 'mid':mid,'swid':swid})) % img_name
        imgdir  = fpath
        imgname = join(fpath, filename.format(_={'asw':asw, 'mid':mid,'swid':swid}))

        if not isdir(imgdir):
            makedirs(imgdir)
        if not isdir(SET.splinp_path):
            makedirs(SET.splinp_path)
    
        #print imgdir
        #print imgname
        #continue
        
        if typ == "new":
            url = "http://labs.spacewarps.org/media/spaghetti/%s/%s/%s" % (mid[0:2],mid[2:], img)
        elif typ == "old":
            url = 'http://mite.physik.uzh.ch/result/' + '%06i/' % int(mid) + img
        else:
            print "ERROR!!!!"
            continue

        tmp_path = join(SET.splinp_path, "_org_" + filename.format(_={'asw':asw, 'mid':mid,'swid':swid}))

        if isfile(tmp_path) and not DBG:
            print 'SKIPPING DL (already present)'

        else:
        
            r = rq.get(url, stream=True)
            
            if r.status_code >= 300: # reuqests takes care of redirects!
                print 'ERROR:', r.status_code
                continue
    
            if 'content-type' in r.headers and 'json' in r.headers['content-type']:
                print 'ERROR: no valid png file (json)' 
                continue
    
            with open(tmp_path, 'w') as f:
                for chunk in r.iter_content(1024*4):
                    f.write(chunk)
            print 'downloaded,',
        
#            # cut the image to square, overwriting the orginal
#            i1 = Image.open(path)
#            if not img == 'input.png':
#                i1 = i1.crop([172, 62, 477+172, 477+62])
#            else:
#                i1 = i1.crop([100, 0, 600+100, 600+0])
#            i1.save(path)
#            #i1.save(path[:-3] + 'eps')
#            print "cut,",
            

        im = misc.imread(tmp_path)

        # calculate the scaling
        cfg_maxdist = np.max([ np.abs(x['pos']) for x in M['images']])
        try:
            MDIobj = find_point.getMaxDistImg(im=im)
            img_maxdist, dists, maxpoint = MDIobj
        except find_point.FoundNoMaxError:
            print "found no max",
            
            if swid in OVERRIDE.keys():
                print " OVERRIDING"
                img_maxdist = [OVERRIDE[swid][0],]
                cfg_maxdist = OVERRIDE[swid][1]
            else:
                print " skipping"
                continue
        
        # add the data here for debug purposes
        M['img_maxdist'] = img_maxdist
        M['cfg_maxdist'] = cfg_maxdist
        
        if DBG:
            print "\nmax dists"
            print "  cfg:", cfg_maxdist
            print "  img:", img_maxdist
            print "  max:", maxpoint
            print "  rat:", img_maxdist / cfg_maxdist
#            print "  (scalefact:", M['pixel_scale_fact'],")"
            #print "  (dis_fact :", M['dis_fact'],")"
        
        #cfg_maxdist *= M['pixel_scale_fact'] #* _['dis_fact']
        
        # get pixel length of one arcsec
        arcsec_in_px = img_maxdist / cfg_maxdist
        
        # plot using mpl for same style
        fig = plt.figure(**STY['figure_sq_small'])
        ax = fig.add_subplot(111)
        
        #ax.imshow(im[:,100:700,:])
        
        R = M['mapextend']
        Rinpx = int(R * arcsec_in_px)
        mx, my = maxpoint.astype(int)

        # create bigger image with black border, such that we can cut
        oshape = np.array(im.shape)
        nshape = oshape + 2*np.array([Rinpx, Rinpx, 0])
        nim = np.zeros(nshape, dtype=np.uint8)
        nim[:,:] = [0,0,0,255] # [255,128,0,255]
        nim[Rinpx:Rinpx+oshape[0],Rinpx:Rinpx+oshape[1],:] = im # put original image ontop
        
#        print nim
#        ax.imshow(nim[:,:,:])

        x = (mx - Rinpx) + Rinpx  # the offset at the end is due the added border above
        y = (my - Rinpx) + Rinpx
        u = (mx + Rinpx) + Rinpx
        v = (my + Rinpx) + Rinpx
        
        print x,y,u,v, arcsec_in_px
        ax.imshow(nim[x:u,y:v,:])
        
#        
#        a = cfg_maxdist
#        #xy = (maxpoint[0]*a-30, maxpoint[1]*a-30)
#        xy = (u, 3)
#        #Rpx = 60
#
#        import matplotlib.patches as patches
#        ax.add_patch(
#            patches.Rectangle(
#                xy, #x,y
#                Rpx,  #width
#                Rpx,  # height
#                fill=False,edgecolor="red",
#            )
#        )
        
        ax.tick_params(**STY['no_ticks'])
        ax.tick_params(**STY['no_labels'])
        
        if PRINT_CAPTION:
    #        SET.add_inline_label(ax, swid, color="dark")
            SET.add_caption_swid(ax, text=swid, color='dark')
            SET.add_caption_mid(ax, text=mid+("" if isZCorr else "*"), color='dark')
            
            # sanity check
            if arcsec_in_px < 500:
                asb = SET.add_size_bar(
                    ax,
                    r"1$^{\prime\prime}$",
                    length=arcsec_in_px,
                    height=0.01,
                    heightIsInPx = True,
                    theme="dark",
                    **STY['scalebar']
                )


        plt.tight_layout()
        fig.savefig(imgname, **STY['figure_save'])
        
        if DBG:
            plt.show()
            #return asb
            #return cfg_maxdist, img_maxdist, M
            #break
            
        plt.close(fig)
        print 'done'
            
        #if DBG: break
#    if DBG:
#        return cfg_maxdist, img_maxdist, M
            


I = SET.getI(__file__)
SET.print_first_line(I)
asb = main()
SET.print_last_line(I)


