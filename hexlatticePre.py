'''
Created on 2018/11/12

@author: Emi Minamitani
'''

import argparse
import glob 
import shutil
import os
import numpy as np



if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='generate input files to determine the hexagonal lattice constant', fromfile_prefix_chars='@')
    parser.add_argument('--start_a', metavar='minimum value of in-plane lattice constant', type=float, action='store')
    parser.add_argument('--last_a',metavar='maximum value of in-plane lattice constant', type=float, action='store')
    parser.add_argument('--sample_a',metavar='sampling number of in-plane lattice constant', type=int, action='store')
    parser.add_argument('--start_ca',metavar='minimum value of c/a ratio', type=float, action='store')
    parser.add_argument('--last_ca', metavar='maximum value of c/a ratio', type=float, action='store')
    parser.add_argument('--sample_ca', metavar='sampling number of c/a ratio',type=int, action='store')
    parser.add_argument('--template', metavar='template file',type=str, action='store')
    
    args=parser.parse_args()
    temp=open(args.template,"r")
    
    info=temp.readlines()
    
    temp.close()
    
    latta=np.linspace(args.start_a, args.last_a, args.sample_a)
    ca=np.linspace(args.start_ca, args.last_ca, args.sample_ca)
    
    dirs=[]
    
    alat=0.0
    caratio=0.0
    counter=0
    alatline=0
    relaxLine=0
    caLine=0
    cellInfoLine=0
    for i in info:
        
        if i.find("calculation")>=0:
            relaxLine=counter
                
        if i.find("celldm(1)")>=0:
            alat=float(i.strip("\n").split("=")[1].strip())
            print("original lattice constant="+str(alat))
            alatline=counter
        
        if i.find("celldm(3)") >=0:
            caratio=float(i.strip("\n").split("=")[1].strip())
            print("original c/a ratio="+str(caratio))
            caLine=counter
        
            
        counter=counter+1
    
    
    for la in latta:
        for caratio in ca:
    
            newaLine="celldm(1)= "+str(la)+" \n"
            caratopLine="celldm(3)= "+str(caratio)+" \n"
            info[alatline]=newaLine
            info[caLine]=caratopLine
    
            scfLine="calculation=\'scf\' \n"
            info[relaxLine]=scfLine
            
            dirname="a-"+str(la)+"-ca-"+str(caratio)
            
            try:
                os.mkdir(dirname)
            except OSError:
                print('directry already exist, file is overwritted')
           
            f=open(dirname+"/"+args.template,"w")
            dirs.append(dirname)
    
            for i in info:
                f.write(i)
            
            f.close()
            
            upffiles=glob.glob("./*.upf")
            for file in upffiles:
                shutil.copy(file,dirname)
    
    #making runscript
    fs=open("run.sh","w")
    fs.write("#!/bin/csh\n")
    fs.write("#$ -cwd  \n")
    fs.write("#$ -V -S /bin/bash \n")
    fs.write("#$ -N hex-lattice \n")
    fs.write("#$ -o stdout \n")
    fs.write("#$ -e stdout \n")
    fs.write("#$ -q all.q \n")
    fs.write("#$ -pe x32 32 \n")
    
    fs.write("for dir in ./a-*ca-*; do \n")
    fs.write("cd $dir \n")
    fs.write("mpirun -np 32 /home/emi/espresso/install-test/qe-6.2/bin/pw.x -npool 32 < " + args.template +" > scf.out \n")
    fs.write("cd ../ \n")
    fs.write("done \n")
    
    fs.close()
    
    