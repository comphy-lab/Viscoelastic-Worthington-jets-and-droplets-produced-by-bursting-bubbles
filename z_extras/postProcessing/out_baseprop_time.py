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
    exe = ["./getbaseprop", filename]
    p = sp.Popen(exe, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = p.communicate()
    dropstats = []
    temp1 = stderr.decode("utf-8")
    temp2 = temp1.split("\n")
    temp3 = temp2[0].split(" ")
    return float(temp3[0]), float(temp3[1]), float(temp3[2]), float(temp3[3])
# ----------------------------------------------------------------------------------------------------------------------


nGFS = 5000
Ldomain = 4


lw = 2
tsnap=0.01
    
for ti in range(60, nGFS):
    t = tsnap*ti
    place = "intermediate/snapshot-%5.4f" % t

    if not os.path.exists(place):
        print("%s File not found!" % place)
    else:
            tp, xcmax, ycmax, D33avg = gettingbaseprop(place) # time, number od drops, volume, x, y
            print(tp)
            print("Time: %4.3f, xcmax: %4.3f, ycmax: %4.3f, D33avg: %4.3f" % (tp, xcmax, ycmax, D33avg) )
                # append in output file
            
            f = open("out_baseprop_time.txt", "a")
            f.write("%4.6f"  % (tp))
            f.write(",")
            f.write("%4.6f"  % (ycmax))
            f.write(",")
            f.write("%4.6f"  % (D33avg))
            f.write("\n")

f.close()
