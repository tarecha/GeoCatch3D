import numpy as np
import pandas as pd
from scipy.stats import gumbel_r

# data R24 annual maxima (contoh: 10 tahun)
R = np.array([97.1,	87,	107.4,	96.7,	84.6,	145,	95.7,	70.9,	105.4,	71.2])

def gumbel_RT(series, T):
    loc, scale = gumbel_r.fit(series)   # fit Gumbel (loc, scale)
    p = 1 - 1.0/float(T)
    return gumbel_r.ppf(p, loc=loc, scale=scale)

# contoh: estimasi R10
print("R10:", gumbel_RT(R, 10))

# bootstrap untuk interval kepercayaan
def bootstrap_RT(series, T, nboot=2000, alpha=0.05):
    n = len(series)
    boots = []
    for _ in range(nboot):
        samp = np.random.choice(series, size=n, replace=True)
        try:
            boots.append(gumbel_RT(samp, T))
        except:
            boots.append(np.nan)
    boots = np.array(boots)
    lo = np.nanpercentile(boots, 100*alpha/2)
    hi = np.nanpercentile(boots, 100*(1-alpha/2))
    return lo, hi, np.nanmedian(boots)

for T in [2,5,10,25,50]:
    lo, hi, med = bootstrap_RT(R, T, nboot=2000)
    print(f"T={T}: median={med:.2f}, 95%CI=({lo:.2f}, {hi:.2f})")
