from scipy.integrate import odeint

Omr = 4.8e-5
Oml = 0.72
Omk = 0
Omm = 1 - Omr - Oml - Omk

def dcomov(r,a):
    H = (Omm/a**3 + Omr/a**4 + Oml + Omk/a**2)**.5
    return 1/(a*a*H)

def sig_factor(zlens,zsrc):
    alens = 1./(1+zlens)
    asrc = 1./(1+zsrc)
    a = [asrc,alens,1]
    r = odeint(dcomov,[0],a)[:,0]
    Dl = alens*(r[2]-r[1])
    Ds = asrc*r[2]
    Dls = asrc*r[1]
    return Dl*Ds/Dls

