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

def gettingbaseprop(filename):
    exe = ["./getbaseprop_v2", filename]
    p = sp.Popen(exe, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = p.communicate()
    dropstats = []
    temp1 = stderr.decode("utf-8")
    temp2 = temp1.split("\n")
    temp3 = temp2[0].split(" ")
    return float(temp3[0]), float(temp3[1]), float(temp3[2]), float(temp3[3]), float(temp3[4])
# ----------------------------------------------------------------------------------------------------------------------


nGFS = 5000
Ldomain = 4


lw = 2
tsnap=0.01
    
for ti in {60}:
    t = tsnap*ti
    place = "intermediate/snapshot-%5.4f" % t

    if not os.path.exists(place):
        print("%s File not found!" % place)
    else:
            tp, x, y, D33, sigma33 = gettingbaseprop(place) # time, number od drops, volume, x, y
            print(tp)
            print("Time: %4.3f, xcmax: %4.3f, ycmax: %4.3f, D33avg: %4.3f, sigma33avg: %4.3f" % (tp, x, y, D33, sigma33))
                # append in output file
            
            f = open("out_baseprop_time_v3.txt", "a")
            f.write("%4.6f"  % (tp))
            f.write(" ")
            f.write("%4.6f"  % (y))
            f.write(" ")
            f.write("%4.6f"  % (D33))
            f.write(" ")
            f.write("%4.6f"  % (sigma33))
            f.write("\n")

f.close()
