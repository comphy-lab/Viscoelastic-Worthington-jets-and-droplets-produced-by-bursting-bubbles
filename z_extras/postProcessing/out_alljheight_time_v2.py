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
    exe = ["./getXheight_maxcurv_v2", filename]
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
tsnap = 0.02
# remove file if it already exists
if os.path.exists("Jlength_time.txt"):
    os.remove("Jlength_time.txt")
    
for ti in range(int(0.3/tsnap), int(1.75/tsnap)):
    t = tsnap*ti
    place = "intermediate/snapshot-%5.4f" % t

    if not os.path.exists(place):
        print("%s File not found!" % place)
    else:
                tp, zTP, rTP, vTP, zcmax, rcmax = gettingXheight(place)
                jlen =  zTP - zcmax
                # Write output to file for plotting
                print (tp)
                print("The jet height is %f" % zTP)
                print("The jet length is %f" % jlen)
                with open('Jlength_time.txt', 'a') as f:
                    print("%f %f %f" % (tp, zTP, zcmax), file=f)
                if (jlen > Jetheight_max_temp):
                    Jetheight_max_temp = jlen
                    t_temp = tp
                print("The jet length max is %f" % Jetheight_max_temp)
                
                # append in output file
                

f = open("../out_maxjlength_time.txt", "a")
f.write("%4.6f"  % (t_temp))
f.write(",")
f.write("%4.6f"  % (Jetheight_max_temp))
f.write("\n")
f.close()

