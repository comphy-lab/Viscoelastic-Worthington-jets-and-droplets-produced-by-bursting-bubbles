# Author: Vatsal Sanjay
# vatsalsanjay@gmail.com
# Physics of Fluids
# Last updated: 19-Nov-2020

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

def gettingFacets(filename):
    exe = ["./getFacet", filename]
    p = sp.Popen(exe, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = p.communicate()
    temp1 = stderr.decode("utf-8")
    temp2 = temp1.split("\n")
    segs = []
    skip = False
    if (len(temp2) > 1e2):
        for n1 in range(len(temp2)):
            temp3 = temp2[n1].split(" ")
            if temp3 == ['']:
                skip = False
                pass
            else:
                if not skip:
                    temp4 = temp2[n1+1].split(" ")
                    r1, z1 = np.array([float(temp3[1]), float(temp3[0])])
                    r2, z2 = np.array([float(temp4[1]), float(temp4[0])])
                    ##segs.append((r1,z1))
                    segs.append(((r1, z1),(r2, z2)))
                    segs.append(((-r1, z1),(-r2, z2)))
                    skip = True
    return segs

def gettingfield(filename, zmin, zmax, rmax, nr, Ohs, Ohp, Oha):
    exe = ["./getData", filename, str(zmin), str(0), str(zmax), str(rmax), str(nr), str(Ohs), str(Ohp), str(Oha)]
    p = sp.Popen(exe, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = p.communicate()
    temp1 = stderr.decode("utf-8")
    temp2 = temp1.split("\n")
    # print(temp2) #debugging
    Rtemp, Ztemp, D2temp, veltemp, Utemp, Vtemp, taupTemp = [],[],[],[],[],[],[]

    for n1 in range(len(temp2)):
        temp3 = temp2[n1].split(" ")
        if temp3 == ['']:
            pass
        else:
            Ztemp.append(float(temp3[0]))
            Rtemp.append(float(temp3[1]))
            D2temp.append(float(temp3[2]))
            veltemp.append(float(temp3[3]))
            Utemp.append(float(temp3[4]))
            Vtemp.append(float(temp3[5]))
            taupTemp.append(float(temp3[6]))

    R = np.asarray(Rtemp)
    Z = np.asarray(Ztemp)
    D2 = np.asarray(D2temp)
    vel = np.asarray(veltemp)
    U = np.asarray(Utemp)
    V = np.asarray(Vtemp)
    taup = np.asarray(taupTemp)
    nz = int(len(Z)/nr)

    # print("nr is %d %d" % (nr, len(R))) # debugging
    print("nz is %d" % nz)

    R.resize((nz, nr))
    Z.resize((nz, nr))
    D2.resize((nz, nr))
    vel.resize((nz, nr))
    U.resize((nz, nr))
    V.resize((nz, nr))
    taup.resize((nz, nr))

    return R, Z, D2, vel, U, V, taup, nz

def gettingXheight(filename):
    exe = ["./getXheight_maxcurv_v2", filename]
    p = sp.Popen(exe, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = p.communicate()
    temp1 = stderr.decode("utf-8")
    temp2 = temp1.split("\n")
    temp3 = temp2[0].split(" ")
    return float(temp3[0]), float(temp3[1]), float(temp3[2]), float(temp3[3]), float(temp3[4]), float(temp3[5])
# ----------------------------------------------------------------------------------------------------------------------


nGFS = 50000
Ldomain = 4
GridsPerR = 64
nr = int(GridsPerR*Ldomain)
Ohs, Ohp, Oha = 1e-2, 1e-2, 1e-4

rmin, rmax, zmin, zmax = [-Ldomain, Ldomain, -Ldomain, Ldomain]
lw = 2

folder = 'Video_jheight'  # output folder

if not os.path.isdir(folder):
    os.makedirs(folder)

for ti in range(nGFS):
    t = 0.1*ti
    place = "intermediate/snapshot-%5.4f" % t
    name = "%s/%8.8d.png" %(folder, int(t*1000))

    if not os.path.exists(place):
        print("%s File not found!" % place)
    else:
        if os.path.exists(name):
            print("%s Image present!" % name)
        else:
            segs = gettingFacets(place)
            if (len(segs) == 0):
                print("Problem in the available file %s" % place)
            else:

                R, Z, taus, vel, U, V, taup, nz = gettingfield(place, zmin, zmax, rmax, nr, Ohs, Ohp, Oha)
                
                tp, zTP, rTP, vTP, zcmax, rcmax = gettingXheight(place)
                
                zminp, zmaxp, rminp, rmaxp = Z.min(), Z.max(), R.min(), R.max()

                # print(zminp, zmaxp, rminp, rmaxp)

                # Part to plot
                AxesLabel, TickLabel = [50, 20]
                fig, ax = plt.subplots()
                fig.set_size_inches(19.20, 10.80)

                ax.plot([0, 0], [zmin, zmax],'-.',color='grey',linewidth=lw)

                ax.plot([rmin, rmin], [zmin, zmax],'-',color='black',linewidth=lw)
                ax.plot([rmin, rmax], [zmin, zmin],'-',color='black',linewidth=lw)
                ax.plot([rmin, rmax], [zmax, zmax],'-',color='black',linewidth=lw)
                ax.plot([rmax, rmax], [zmin, zmax],'-',color='black',linewidth=lw)

                ## Drawing Facets
                line_segments = LineCollection(segs, linewidths=4, colors='green', linestyle='solid')
                ax.add_collection(line_segments)
                ax.set_title('$t/\\tau_\gamma$ = %4.3f' % t, fontsize=TickLabel)
                #plt.scatter(segs[0], segs[1])
                #print("The line collection array: ",segs)

                ax.plot(rTP, zTP, 'o', color='red', markersize=10)
                ax.plot(rcmax, zcmax, 'o', color='blue', markersize=10)
                
                ## Copied Lines
                ax.set_aspect('equal')
                ax.set_xlim(rmin, rmax)
                ax.set_ylim(zmin, zmax)

                ax.axis('off')
                # plt.show()
                plt.savefig(name, bbox_inches="tight",dpi=250)
                plt.close()
