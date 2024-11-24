# To get droplet volume with case

import numpy as np
import os
import subprocess as sp
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.ticker import StrMethodFormatter
import sys

matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['text.usetex'] = True
# matplotlib.rcParams['text.latex.preamble'] = [r'']

def gettingdropstats(filename):
    exe = ["./getdropstats_v2", filename]
    p = sp.Popen(exe, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = p.communicate()
    dropstats = []
    temp1 = stderr.decode("utf-8")
    temp2 = temp1.split("\n")
    temp3 = temp2[0].split(" ")
    #print(temp3)
    #return len(temp2)
    #for n1 in range(len(temp2)):
    #    temp3 = temp2[n1].split(" ")
    #    print (temp3)
    
    #np.asarray
    #return float(temp3[0]), temp3[1], temp3[2], temp3[3], temp3[4]
    #return temp3[0], temp3[1], temp3[2], temp3[3], temp3[4]
    return float(temp3[0]), float(temp3[1]), float(temp3[2]), float(temp3[3]), float(temp3[4])
# ----------------------------------------------------------------------------------------------------------------------


nGFS = 50000
Ldomain = 4
GridsPerR = 64
nr = int(GridsPerR*Ldomain)


rmin, rmax, zmin, zmax = [-Ldomain, Ldomain, -Ldomain, Ldomain]
lw = 2
tsnap=0.05

# remove file if it already exists
#if os.path.exists("out_vol_time.txt"):
#    os.remove("out_vol_time.txt")
    
for ti in range(6, 30):
    t = tsnap*ti
    place = "intermediate/snapshot-%5.4f" % t

    if not os.path.exists(place):
        print("%s File not found!" % place)
    else:
                tp, jd, vd, xd, yd = gettingdropstats(place) # time, number od drops, volume, x, y
                print(tp)
                if not vd == 0:
                    print("Time: %4.3f, Drops: %d, Volume: %4.3f, x: %4.3f, y: %4.3f" % (tp, jd, vd, xd, yd))
                # append in output file
                    f = open("../out_vol_time.txt", "a")
                    f.write("%4.6f"  % (tp))
                    f.write(",")
                    f.write("%4.6f"  % (vd))
                    f.write("\t")
                    break
                    #if (xd > 3.75):
                    #  break

f.write("\n")
f.close()

