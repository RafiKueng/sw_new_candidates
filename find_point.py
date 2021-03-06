
import numpy as np
from scipy import ndimage
from scipy import misc
from scipy.ndimage import label
import matplotlib.pyplot as plt

import re


fname = "004741.cfg"

class FoundNoMaxError(Exception):
    pass
class FoundManyMaxError(Exception):
    pass

def getMaxDistCFG(fname):
    with open(fname) as f:
        lines = f.readlines()
        
    text = "".join(lines)
    res = re.findall('[A-I]\s=\s(.*)', text)
    res2 = [_.split(",") for _ in res]
    res3 = [np.array([float(_[0]), float(_[1])]) for _ in res2]
    dists = [np.sqrt(np.sum(_**2)) for _ in res3]
            
    return max(dists), dists


def getMaxDistImg(fname = fname, im=None):
    """
    Open an input image file,
    determine all extremalpoints,
    identify max (red)
    calulate all dists to max,
    return max dist, and list of dists, maxpoint
    """

    leg = ['max', 'sad', 'min'] # legend.. id of type of extremal point

    if im is None:
        im = misc.imread(fname)
    
    r = im[:,:,0]
    g = im[:,:,1]
    b = im[:,:,2]
    
    maxpnt = ((r==255) & (g == 0) & (b == 0))
    sadpnt = ((r==0) & (g == 128) & (b == 0))
    minpnt = ((r==0) & (g == 255) & (b == 255))
    
    points = []
    
    for i, pnts in enumerate([maxpnt, sadpnt, minpnt]):
        lbl, nlbls = label(pnts)
        for j in range(1, nlbls+1):
            pntpos = np.ma.median(np.array(np.where(lbl==j)), axis=1)
            pntvar = np.ma.var(np.array(np.where(lbl==j)), axis=1)
            print leg[i], pntpos.data, pntvar,
            # for a real point a variance of ca 15 in each dimension is expected
            # so we only save those
            if (pntvar[0] > 7 and pntvar[0] < 20) and (pntvar[1] > 7 and pntvar[1] < 20):
                points.append((leg[i], pntpos.data))
                print "save"
            else:
                print "skip"
    
    dists = []
    maxposes = [_ for _ in points if _[0]=='max']

    if len(maxposes) < 1:
          raise FoundNoMaxError("Found no max")
    if len(maxposes) > 1:
          raise FoundManyMaxError("Found many max")
    
    try:
        x = maxposes[0][1]
        for pos in points:
            y = pos[1]
            dists.append(np.sqrt(np.sum((x-y)**2)))
    except:
        print "!"*80
        pass
    
    return max(dists), dists, maxposes[0][1]

    
    
    
    
    
if __name__ == "__main__":
    #fname1 = "ASW0001c3j_5R6UYQZUTI_input.png"
    fname_cfg = "004741.cfg"
    fname_img = "ASW0004dv8_004741_input.png"
    fname_img = "output/spl-input/_tmp_SW37_ASW00086xq_BYQATMOXCM_spl-input.png"
    
    
    
    print getMaxDistImg(fname_img)[0]
#    print getMaxDistCFG(fname_cfg)[0]
    
    
#plt.imshow(minpnt, cmap="gray")
#plt.show()
#plt.imshow(sadpnt, cmap="gray")
#plt.show()
#plt.imshow(maxpnt, cmap="gray")
#plt.show()
