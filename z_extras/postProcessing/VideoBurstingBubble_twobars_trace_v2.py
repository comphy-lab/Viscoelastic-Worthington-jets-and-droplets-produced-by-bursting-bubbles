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
matplotlib.rc('text.latex', preamble=r'\usepackage{amsmath}')

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
    # Convert values to string using str()
    exe = ["./getData_v3", filename, str(zmin), str(0), str(zmax), str(rmax), str(nr), str(Ohs), str(Ohp), str(Oha)]
    
    # Execute the command and get the stdout and stderr
    p = sp.Popen(exe, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = p.communicate()
    
    # Decode bytes to string, assuming utf-8 encoding
    temp1 = stderr.decode("utf-8")
    temp2 = temp1.split("\n")

    Rtemp, Ztemp, D2temp, veltemp, Utemp, Vtemp, AxxTemp, AyxTemp, AyyTemp, AqqTemp, traceTemp = [],[],[],[],[],[],[],[],[],[],[]

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
            AxxTemp.append(float(temp3[6]))
            AyxTemp.append(float(temp3[7]))
            AyyTemp.append(float(temp3[8]))
            AqqTemp.append(float(temp3[9]))
            traceTemp.append(float(temp3[10]))
            

    R = np.asarray(Rtemp)
    Z = np.asarray(Ztemp)
    D2 = np.asarray(D2temp)
    vel = np.asarray(veltemp)
    U = np.asarray(Utemp)
    V = np.asarray(Vtemp)
    nz = int(len(Z)/nr)
    Axx = np.asarray(AxxTemp)
    Ayx = np.asarray(AyxTemp)
    Ayy = np.asarray(AyyTemp)
    Aqq = np.asarray(AqqTemp)
    trace = np.asarray(traceTemp)

    # print("nr is %d %d" % (nr, len(R))) # debugging
    print("nz is %d" % nz)

    R.resize((nz, nr))
    Z.resize((nz, nr))
    D2.resize((nz, nr))
    vel.resize((nz, nr))
    U.resize((nz, nr))
    V.resize((nz, nr))
    Axx.resize((nz,nr))
    Ayx.resize((nz,nr))
    Ayy.resize((nz,nr))
    Aqq.resize((nz,nr))
    trace.resize((nz,nr))

    return R, Z, D2, vel, U, V, nz, Axx, Ayx, Ayy, Aqq, trace
# ----------------------------------------------------------------------------------------------------------------------


nGFS = 50000
Ldomain = 4
GridsPerR = 64
nr = int(GridsPerR*Ldomain)
Ohs, Ohp, Oha = 1e-2, 1e-2, 1e-4

#rmin, rmax, zmin, zmax = [-Ldomain, Ldomain, -Ldomain, Ldomain]
rmin, rmax, zmin, zmax = [-4, 4, -4, 4]
lw = 2

folder = 'Video_twobars_video'  # output folder

if not os.path.isdir(folder):
    os.makedirs(folder)

for ti in range(nGFS):
    t = 0.01*ti
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

                R, Z, logD, vel, U, V, nz, Axx, Ayx, Ayy, Aqq, trace = gettingfield(place, zmin, zmax, rmax, nr, Ohs, Ohp, Oha)
                
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
                # ax.set_title(r'$t/\sqrt{\rho R_0^3/\gamma}$ = %4.3f' % t, fontsize=TickLabel)
                #plt.scatter(segs[0], segs[1])
                #print("The line collection array: ",segs)

                ## Copied Lines
                ax.set_aspect('equal')
                ax.set_xlim(rmin, rmax)
                ax.set_ylim(zmin, zmax)
                #ax.set_xlim(-3,3)
                #ax.set_ylim(-3,3)
                
                ## D
                cntrl1 = ax.imshow(vel, cmap="Blues", interpolation='Bilinear', origin='lower', extent=[0, -4, -4, 4], vmax = 2.0, vmin = 0.0)
                ## V
                cntrl2 = ax.imshow(trace, cmap="hot_r", interpolation='Bilinear', origin='lower', extent=[0, 4, -4, 4], vmax = 1.0, vmin = -2.0)


                #ax.set_aspect('equal')
                #ax.set_xlim(rmin, rmax)
                #ax.set_ylim(zmin, zmax)
                # t2 = t/tc
                ax.set_title(r'$t/\sqrt{\rho R_0^3/\gamma}$ = %4.2f' % t, fontsize=1.5*TickLabel)

                l, b, w, h = ax.get_position().bounds
                cb1 = fig.add_axes([l+0.05*w, b-0.05, 0.40*w, 0.03])
                c1 = plt.colorbar(cntrl1,cax=cb1,orientation='horizontal')
                c1.set_label(r'$\|\mathbf{v}\|\sqrt{\rho R_0/\gamma}$',fontsize=TickLabel, labelpad=5)
                c1.ax.tick_params(labelsize=TickLabel)
                c1.ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.1f}'))
                cb2 = fig.add_axes([l+0.55*w, b-0.05, 0.40*w, 0.03])
                c2 = plt.colorbar(cntrl2,cax=cb2,orientation='horizontal')
                c2.ax.tick_params(labelsize=TickLabel)
                c2.set_label(r'$\log_{10} \left( tr \left( \boldsymbol{\sigma}_p \right) \right)$',fontsize=TickLabel, labelpad=5)
                c2.ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.1f}')) 

                ax.axis('off')
                # plt.show()
                plt.savefig(name, bbox_inches="tight", dpi=250)
                plt.close()
