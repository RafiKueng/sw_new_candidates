
import numpy as np
import csv


states = ['012683']


for statenr in states:

    fpath = 'states/%s.state' % statenr
    
    fact = 0.428
    div_scale_factors = 440./500*100
    
     
    state = loadstate(fpath)
    state.make_ensemble_average()
    obj, data = state.ensemble_average['obj,data'][0]
    
    n_rings = len(obj.basis.rings)
    
    kappaRenc = np.zeros(n_rings)
    pixPerRing = np.zeros(n_rings)
    pixEnc = np.zeros(n_rings)
      
    
    for i in range(n_rings):
        pixEnc[i] = len(obj.basis.rings[i])
        pixPerRing[i] = len(obj.basis.rings[i])
        for j in range(i):
            pixEnc[i] += len(obj.basis.rings[j])
    
    
    for k in range(n_rings):
        enc = 0
        #enc = data['kappa(R)'][k] * pixPerRing[k]    
        for kk in range(k+1):
            enc += data['kappa(R)'][kk] * pixPerRing[kk]
        
        enc /= pixEnc[k]
        enc *= fact

        kappaRenc[k] = enc
        
    mLtR = data['M(<R)']
    
    x_vals = (np.arange(n_rings)+0.5) * div_scale_factors * obj.basis.cell_size[0]
    
    if True:
        with open(statenr+'.csv', 'w') as f:
            csvwriter = csv.writer(f)
            
            csvwriter.writerow(x_vals)
            csvwriter.writerow(kappaRenc)
        
    if True:
        print '%8s ' % 'ringnr',
        for n in range(n_rings):
            print "%9i " % n,
        print ''
        print '%8s ' % 'x val',
        for x in x_vals:
            print "%8.3e " % x,
        print ""
        print '%8s ' % 'k_encl',
        for ke in kappaRenc:
            print "%8.3e " % ke,
        print ""
        print '%8s ' % 'M(<R)',
        for m in mLtR:
            print "%8.3e " % m,
        print ''            
        




