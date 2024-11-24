# To get length, velocity and overall vertical momentum

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

def gettingInertia(filename):
    exe = ["./getInertia", filename]
    p = sp.Popen(exe, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = p.communicate()
    dropstats = []
    temp1 = stderr.decode("utf-8")
    temp2 = temp1.split("\n")
    temp3 = temp2[0].split(" ")
    return float(temp3[0]), float(temp3[1]), float(temp3[2]), float(temp3[3]), float(temp3[4])
# ----------------------------------------------------------------------------------------------------------------------


nGFS = 71
Ldomain = 4


lw = 2
tsnap=0.01
    
for ti in range(nGFS):
    t = tsnap*ti
    place = "intermediate/snapshot-%5.4f" % t

    if not os.path.exists(place):
        print("%s File not found!" % place)
    else:
            tp, xmax, utip, momavg, keavg = gettingInertia(place) # time, number od drops, volume, x, y
            print(tp)
            print("Time: %4.3f, xmax: %4.3f, utip: %4.3f, momavg: %4.3f, keavg: %4.3f" % (tp, xmax, utip, momavg, keavg))
                # append in output file
            
            f = open("out_Inertia_time.txt", "a")
            f.write("%4.6f"  % (tp))
            f.write("\t")
            f.write("%4.6f"  % (xmax))
            f.write("\t")
            f.write("%4.6f"  % (utip))
            f.write("\t")
            f.write("%4.6f"  % (momavg))
            f.write("\t")
            f.write("%4.6f"  % (keavg))
            f.write("\n")

f.close()
