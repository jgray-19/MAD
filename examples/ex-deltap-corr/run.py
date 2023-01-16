import numpy as np
import matplotlib.pyplot as plt
from pymadng import MAD
import os
os.system("../madx64 ex-deltap-corr.madx > /dev/null")
os.system("../mad -q ex-deltap-corr.mad")

mad = MAD(mad_path="../mad")

def compare_dict(dict1):
    max_err = {}
    for k, v in dict1.items():
        for k2, v2 in dict1.items():
            max_err[k+k2] = 0
            for i in range(len(v)):
                if k != k2:
                    if np.abs(v[i]) < 1:
                        err = np.abs((v[i] - v2[i]))
                    else:
                        err = np.abs((v[i] - v2[i])/v[i])
                
                    if err > max_err[k+k2]:
                        max_err[k+k2] = err
    return max_err

types = ["dp_noco", "dp", "noco"]
for t in types:
    mad["ng"] = mad.mtable().read(f"'ex_run/twiss_{t}.tfs'")
    mad["x"] = mad.mtable().read(f"'ex_ref/twiss_{t}_x.ref'")
    mad["p"] = mad.mtable().read(f"'ex_ref/twiss_{t}_p.ref'")
    print(t)

    beta = {}
    alfa = {}
    try:
        beta["n"] = mad.ng.beta11 * (1 + mad.ng.deltap) # beta adjustment for delta p
    except AttributeError:
        beta["n"] = mad.ng.beta11
    beta["x"] = mad.x.BETX
    beta["p"] = mad.p.BETA11
    
    alfa["n"] = mad.ng.alfa11
    alfa["x"] = mad.x.ALFX
    alfa["p"] = mad.p.ALFA11
    
    max_beta_err = compare_dict(beta)
    max_alfa_err = compare_dict(alfa)
    
    print("xp\talfa =", max_alfa_err["xp"], "beta =", max_beta_err["xp"])
    print("np\talfa =", max_alfa_err["np"], "beta =", max_beta_err["np"])
    print("nx\talfa =", max_alfa_err["nx"], "beta =", max_beta_err["nx"], "\n")
    
## Why is t = 0 for all s in the no closed orbit case? (MAD-NG)
## Why is pt = 0 for the closed orbit case? (MAD-NG and PTC but not MAD-X)
## PTC fails to correctly calculate the beta and alpha functions for the non closed orbit case