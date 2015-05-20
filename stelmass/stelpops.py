from numpy import ndarray
from scipy.interpolate import interp1d

fil = open('Rafael_chab.dat')
lyst = fil.readlines()[10:]
z = ndarray(shape=len(lyst))
jr = 0*z
sr = 0*z
for i in range(len(lyst)):
    v = lyst[i].split()
    z[i] = v[0]
    jr[i] = v[3]
    sr[i] = v[4]

magjr = interp1d(z,jr)
magsr = interp1d(z,sr)

zl = []
msjr = []
mssr = []
fil = open('table.txt')
lyst = fil.readlines()
for lyne in lyst:
    v = lyne.split('&')
    id = v[0]
    zp = float(v[4])
    mag = float(v[5])
    asw = v[8]
    print asw,id,
    if zp !=0 and mag != 0:
        zl.append(zp)
        logm = (magjr(zp)-mag)*0.4
        msjr.append(10**(logm-10))
        logm = (magsr(zp)-mag)*0.4
        mssr.append(10**(logm-10))
        print msjr[-1],mssr[-1]
    else:
        print


from pylab import plot, scatter, show
# plot(z,magjr(z))
# plot(z,magsr(z))
# scatter(z,msjr)
# show()


