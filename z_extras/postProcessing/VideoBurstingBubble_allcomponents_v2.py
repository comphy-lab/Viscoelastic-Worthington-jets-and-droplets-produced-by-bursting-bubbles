# Author: Vatsal Sanjay
# vatsalsanjay@gmail.com
# Physics of Fluids
# Last updated: 19-Nov-2020

import numpy as np
import os
import subprocess as sp
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.collections import LineCollection
from matplotlib.ticker import StrMethodFormatter, MultipleLocator
import sys

matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['text.usetex'] = True
# matplotlib.rcParams['text.latex.preamble'] = [r'']

def gettingFacets(filename):
    exe = ["./getFacet", filename]
    
    # Execute the command and get the stdout and stderr
    p = sp.Popen(exe, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = p.communicate()

    # Decode bytes to string, assuming utf-8 encoding
    temp1 = stderr.decode("utf-8") # stderr runs fine. shouldn't it be stdout?

    # Splits the temp1 string into a list
    temp2 = temp1.split("\n")

    # Line segments
    segs = []
    skip = False
    if (len(temp2) > 1e2):
      
        # for n1 in range(len(temp2)):
        for n1 in range(len(temp2)): 
            
            # Again split on the basis of blank-space
            temp3 = temp2[n1].split(" ")
            

            # If temp3 is empty then skip is false
            if temp3 == ['']:
                skip = False
                pass
            else:
                if not skip:

                    temp4 = temp2[n1+1].split(" ")
                    
                    r1, z1 = np.array([float(temp3[1]), float(temp3[0])])
                    r2, z2 = np.array([float(temp4[1]), float(temp4[0])])
                    segs.append(((r1, z1),(r2, z2)))
                    segs.append(((-r1, z1),(-r2, z2)))
                    skip = True 
    return segs

def gettingfield(filename, zmin, zmax, rmax, nr, Ohs, Ohp, Oha):
    # Convert values to string using str()
    exe = ["./getData", filename, str(zmin), str(0), str(zmax), str(rmax), str(nr), str(Ohs), str(Ohp), str(Oha)]
    
    # Execute the command and get the stdout and stderr
    p = sp.Popen(exe, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = p.communicate()
    
    # Decode bytes to string, assuming utf-8 encoding
    temp1 = stderr.decode("utf-8")
    temp2 = temp1.split("\n")

    Rtemp, Ztemp, D2temp, veltemp, Utemp, Vtemp, AxxTemp, AyxTemp, AyyTemp, AqqTemp = [],[],[],[],[],[],[],[],[],[]

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

    return R, Z, D2, vel, U, V, nz, Axx, Ayx, Ayy, Aqq
# ----------------------------------------------------------------------------------------------------------------------


nGFS = 100000
Ldomain = 4
GridsPerR = 128
nr = int(GridsPerR*Ldomain)
Ohs, Ohp, Oha = 1e-2, 1e-2, 1e-4

rmin, rmax, zmin, zmax = [-Ldomain, Ldomain, -Ldomain, Ldomain]
lw = 2

folder = 'Video'  # output folder

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

                R, Z, logD, vel, U, V, nz, Axx, Ayx, Ayy, Aqq = gettingfield(place, zmin, zmax, rmax, nr, Ohs, Ohp, Oha)
                
                zminp, zmaxp, rminp, rmaxp = Z.min(), Z.max(), R.min(), R.max()
                WindowR, WindowZ = 3, 3
                #print(zminp, zmaxp, rminp, rmaxp)
                
                #Define the grids where axes will be plotted
                fig = plt.figure()
                fig.suptitle(r"$t/t_\gamma = %3.2f$" % t, fontsize=25)
                gs = gridspec.GridSpec(1, 3)
                
                ax1 = plt.subplot(gs[0, 0])
                ax2 = plt.subplot(gs[0, 1])
                ax3 = plt.subplot(gs[0, 2])

                # Part to plot
                AxesLabel, TickLabel, HeadLabel = [50, 20, 30]
                #fig, ax = plt.subplots()
                
                fig.set_size_inches(16.00, 5.0)

                # Adds a rectangular boundary
                #rect = matplotlib.patches.Rectangle((rmin, zmin), rmax-rmin, zmax-zmin, linewidth=2, edgecolor='k', facecolor='none')
                #ax.add_patch(rect)
                ## Drawing Facets
                #line_segments = LineCollection(segs, linewidths=4, colors='green', linestyle='solid')
                #ax.add_collection(line_segments)
                #ax1.add_collection(line_segments)
                #ax1.set_xlim(rmin/2, rmax/2)
                #ax1.set_ylim(zmin/2, zmax/2)
                #ax2.add_collection(line_segments)

                COLORMAP = "RdBu_r"
                VMIN, VMAX = -3.5, 3.5
                for ax in [ax1, ax2, ax3]:  
                    rect2 = matplotlib.patches.Rectangle((-WindowR, -WindowZ), 2*WindowR, 2*WindowZ, linewidth=2, edgecolor='black', facecolor='none')
                    line_segments = LineCollection(segs, linewidths=4, colors='green', linestyle='solid')
                    ax.add_collection(line_segments)
                    ax.set_aspect('equal')
                    ax.set_xlim(-WindowR, WindowR)
                    ax.set_ylim(-WindowZ, WindowZ)
                    ax.plot([0, 0], [zmin, zmax],'-.',color='grey',linewidth=lw-1)
                    ax.add_patch(rect2)
                    ax.axis('off')

                ax_data_dict = {
                     ax1: [r"$V$", r"$\log\left(\|\mathbf{\mathcal{D}}\|\right)$", vel, logD, "Blues", "hot_r", 2, 0, 2, 0],
                     ax2: [r"$\left( \log A \right)_{rr}$", r"$\left( \log A \right)_{rz}$", Axx, Ayx, COLORMAP, COLORMAP, VMAX, VMIN, VMAX, VMIN],
                     ax3: [r"$\left( \log A \right)_{zz}$",r"$\left( \log A \right)_{\theta \theta}$", Ayy, Aqq, COLORMAP, COLORMAP, VMAX, VMIN, VMAX, VMIN],
                    }

                for ax, data in ax_data_dict.items():
                    #ax.set_title(data[0], fontsize=12)
                    cntrl1=ax.imshow(data[2], cmap=data[4], interpolation='Bilinear', origin='lower', extent= [0, -4, -4, 4], vmax = data[6], vmin = data[7])
                    cntrl2=ax.imshow(data[3], cmap=data[5], interpolation='Bilinear', origin='lower', extent= [0, 4, -4, 4], vmax = data[8], vmin = data[9])
                    #ax.imshow(data[1], cmap=data[2], interpolation='Bilinear', origin='lower', extent= [-rminp, rmaxp, zminp, zmaxp], vmax = data[3], vmin = data[4])
                    #ax.set_aspect('equal')
                    #ax.set_xlim(-2.5, 2.5)
                    #ax.set_ylim(0, 5)
                    
                    l, b, w, h = ax.get_position().bounds
                    
                    cb1 = fig.add_axes([l+0.05*w, b-0.05, 0.375*w, 0.03])
                    c1 = plt.colorbar(cntrl1,cax=cb1,orientation='horizontal')
                    c1.set_label(data[0],fontsize=TickLabel, labelpad=5)
                    c1.ax.tick_params(labelsize=TickLabel)
                    c1.ax.xaxis.set_major_locator(MultipleLocator((data[6]-data[7])/2))
                    c1.ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.1f}'))
                    
                    cb2 = fig.add_axes([l+0.575*w, b-0.05, 0.375*w, 0.03])
                    c2 = plt.colorbar(cntrl2,cax=cb2,orientation='horizontal')
                    c2.set_label(data[1],fontsize=TickLabel, labelpad=5)
                    c2.ax.tick_params(labelsize=TickLabel)
                    c2.ax.xaxis.set_major_locator(MultipleLocator((data[8]-data[9])/2))
                    c2.ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.1f}'))

                ## D
                #cntrl1 = ax.imshow(taus, cmap="hot_r", interpolation='Bilinear', origin='lower', extent=[-rminp, -rmaxp, zminp, zmaxp], vmax = 0.0, vmin = -3.0)
                ## V
                #cntrl2 = ax.imshow(taup, cmap="bone_r", interpolation='Bilinear', origin='lower', extent=[rminp, rmaxp, zminp, zmaxp], vmax = 0.0, vmin = -3.0)

                '''
                ax.set_aspect('equal')
                ax.set_xlim(rmin, rmax)
                ax.set_ylim(zmin, zmax)
                # t2 = t/tc
                ax.set_title('$t/\\tau_\gamma$ = %4.3f' % t, fontsize=TickLabel)
                '''


                '''
                l, b, w, h = ax.get_position().bounds
                cb1 = fig.add_axes([l+0.05*w, b-0.05, 0.40*w, 0.03])
                c1 = plt.colorbar(cntrl1,cax=cb1,orientation='horizontal')
                c1.set_label('$\log_{10}\left(\\tau_s\\right)$',fontsize=TickLabel, labelpad=5)
                c1.ax.tick_params(labelsize=TickLabel)
                c1.ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.1f}'))
                cb2 = fig.add_axes([l+0.55*w, b-0.05, 0.40*w, 0.03])
                c2 = plt.colorbar(cntrl2,cax=cb2,orientation='horizontal')
                c2.ax.tick_params(labelsize=TickLabel)
                c2.set_label('$\log_{10}\left(\\tau_p\\right)$',fontsize=TickLabel, labelpad=5)
                c2.ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.2f}'))

                '''
                #ax1.axis('off')
                #plt.show()
                plt.savefig(name, bbox_inches="tight",dpi=250)
                plt.close()
