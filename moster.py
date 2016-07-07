# Moster et al (2010)
# http://adsabs.harvard.edu/abs/2010ApJ...710..903M

from scipy.optimize import brentq

M1 = 10**(11.884)
mr = 0.02820
beta = 1.057
gamma = 0.556

def moster(M):
    m = M*2*mr / ((M/M1)**(-beta) + (M/M1)**gamma)
    return m

# brentq(moster(M), -pi, pi)

def mosterinv(m):
    return brentq(lambda M: moster(M) - m, 1e11, 1e14)


if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as pl

    M = np.logspace(11,14,20)
    m = M*2*mr / ((M/M1)**(-beta) + (M/M1)**gamma)
    Mx = np.array([mosterinv(x) for x in m])
    pl.loglog(m,M)
    pl.loglog(m,2*Mx)

    pl.show()



