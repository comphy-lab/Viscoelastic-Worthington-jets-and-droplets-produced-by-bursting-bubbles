# To get jet height with time and max jet height

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

def gettingXheight(filename):
    exe = ["./getXheight_theta_v4", filename]
    p = sp.Popen(exe, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = p.communicate()
    temp1 = stderr.decode("utf-8")
    temp2 = temp1.split("\n")
    temp3 = temp2[0].split(" ")
    return float(temp3[0]), float(temp3[1]), float(temp3[2]), float(temp3[3]), float(temp3[4]), float(temp3[5])
# ----------------------------------------------------------------------------------------------------------------------


nGFS = 5000
Ldomain = 4
GridsPerR = 64
nr = int(GridsPerR*Ldomain)


rmin, rmax, zmin, zmax = [-Ldomain, Ldomain, -Ldomain, Ldomain]
lw = 2

Jetheight_max_temp = -30.0
t_temp = 0.0
tsnap = 0.01
# remove file if it already exists
if os.path.exists("Theta_time.txt"):
    os.remove("Theta_time.txt")
    
for ti in range(int(0.5/tsnap)+1):
    t = tsnap*ti
    place = "intermediate/snapshot-%5.4f" % t

    if not os.path.exists(place):
        print("%s File not found!" % place)
    else:
                tp, xTP, yTP, vTP, xcmax, ycmax = gettingXheight(place)
                
                # Write output to file for plotting
                print (tp)
                thetap = 1 - np.arccos((xcmax + 1)/np.sqrt((xcmax+ 1)**2+ycmax**2))/np.pi
                
                print("Theta is %f" % thetap)
                with open('Theta_time.txt', 'a') as f:
                    print("%f %f" % (tp, thetap), file=f)
                    
