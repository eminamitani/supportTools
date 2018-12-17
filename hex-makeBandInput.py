'''
Created on 2017/11/10
making band calculation inputs for hexagonal system
@author: Emi Minamitani
'''
import argparse
import os
import re
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='band structure calclation for hex ', fromfile_prefix_chars='@')
    parser.add_argument('--scfIn', metavar='filename of scf calculation of pw.x', action='store')
    parser.add_argument('--prefix', metavar='prefix for QE calculation', type=str,action='store')
    parser.add_argument('--dim', metavar='dimension of the system', type=int, default=3, action="store")

    args=parser.parse_args()
    f=open(args.scfIn,"r")
    lines=f.readlines()
    f.close()

    #output logs
    flog=open("log.txt","w")
    flog.write("--scfIn="+ str(args.scfIn) +"\n")
    flog.write("--prefix="+ str(args.prefix) +"\n")
    flog.close()

    #making input for nscf calculation for bandstructure
    nscflines=lines[:]

    calculationLines="calculation=\'bands\' \n "
    counter=0
    kpointPosition=0
    for i in nscflines:
        if i.find("calculation")>=0:
            nscflines[counter]=calculationLines

        if i.find("K_POINTS") >=0:
            kpointPosition=counter

        counter=counter+1

    #remove kpoint section
    del nscflines[kpointPosition:kpointPosition+2]

    #add kpoint path information

    if(args.dim==3):
        nscflines.append("K_POINTS {tpiba_b} \n 8 \n gG 30 \n M  30 \n K  30\n" \
                    + " gG 30 \n A  30 \n L  30 \n H  30 \n A  1 \n")
    elif(args.dim==2):
        nscflines.append("K_POINTS {tpiba_b} \n 8 \n gG 30 \n M  30 \n K  30\n" \
                    + " gG 1 \n")

    fnscf=open(args.prefix+".nscf.in","w")
    for i in nscflines:
        fnscf.write(i)

    fnscf.close()

    fband=open(args.prefix+".band.in", "w")
    fband.write("& bands \n")
    fband.write("outdir =\'./\' \n")
    fband.write("prefix=\'"+args.prefix+"\' \n")
    fband.write("filband=\'"+args.prefix+".band\' \n")
    fband.write("lsym= .true. \n")
    fband.write("/ \n")
    fband.close()


    #write runscript
    #for muse system
    #please modify pwscfRoot and nodes and so on appropriate
    pwscfRoot="/home/emi/espresso/install-test/gitHub/q-e/bin/"
    nodes=24
    frun=open("runband.sh", "w")
    frun.write("#!/bin/csh \n")
    frun.write("#$ -cwd  \n")
    frun.write("#$ -V -S /bin/bash  \n")
    frun.write("#$ -N "+args.prefix+"-band \n")
    frun.write("#$ -o stdout \n")
    frun.write("#$ -e stdout \n")
    frun.write("#$ -pe smp "+str(nodes) +" \n")
    frun.write("mpirun "+ pwscfRoot+"pw.x"+ " -npool  " +str(nodes)  + " < "+args.scfIn+ " > scf.out \n")
    frun.write("mpirun "+ pwscfRoot+"pw.x"+ " -npool  "+str(nodes)  +" < "+args.prefix+".nscf.in" + " > nscf.out \n")
    frun.write("mpirun "+ pwscfRoot+"bands.x"+ " -npool  "+str(nodes) +" < "+args.prefix+".band.in" + " > band.out \n")

    frun.close()
