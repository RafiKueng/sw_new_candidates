import numpy as np
import matplotlib.pyplot as pl

M1 = 10**(11.884)
mr = 0.02820
beta = 1.057
gamma = 0.556

M = np.logspace(11,14,20)

m = M*2*mr / ((M/M1)**(-beta) + (M/M1)**gamma)

pl.loglog(m,M)
pl.show()
