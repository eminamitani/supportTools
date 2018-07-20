'''
Created on 2017/10/13

Supporting script to phonon job split into several independent job divided by q-points
@author: Emi Minamitani

'''
import argparse
import re
import os
import shutil
import glob
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='phonon input ', fromfile_prefix_chars='@')
    parser.add_argument('--scfFile', metavar='filename of scf calculation of pw.x', action='store')
    parser.add_argument('--qmesh', metavar='mesh for 3 direction, total 3 number required', type=int, action='store',nargs=3)
    parser.add_argument('--polar', metavar='need to calculate Born effective charge and dielectric constant', type=bool,action='store',default='true')
    parser.add_argument('--njobs', metavar='number of split jobs', type=int, action='store')
    parser.add_argument('--nqs', metavar='number of irreduciable qpoints', type=int, action='store')
    
    args=parser.parse_args() 
    
    #loadbarance with napsack method
    loadmin=[]
    loadmax=[]
    
    work=int(args.nqs/args.njobs)
    work2=args.nqs%args.njobs
    for i in range(args.njobs):
        minval=1+i*work+min(i,work2)
        loadmin.append(minval)
        loadmax.append(minval+work-1)
        if(work2 >i):
            loadmax[i]=loadmax[i]+1
    
    print(loadmin)
    print(loadmax)
    
    
    #get common information
    f=open(args.scfFile,"r")
    lines=f.readlines()  
    f.close()
    print(lines)
    
    prefix=''
    outdir=''
    psuedo_dir=''
    for i in lines:
        
        if (i.find("prefix") >=0):
            prefix=i.strip("\n")
        
        if (i.find("outdir") >=0):
            outdir=i.strip("\n")
            
        if (i.find("pseudo_dir") >=0):
            psuedo_dir=i.strip("\n")
            
    
    print(prefix)
    print(outdir)
    
    prefixName=re.sub('[\" \' \s]', '', prefix.split("=")[1])
    print(prefixName)
    
    psuedoPosition=re.sub('[\" \' \s]', '', psuedo_dir.split("=")[1])
    print(psuedoPosition)
    
    #making directory for each split job
    
    dirlist=[]
    
    for i in range(args.njobs):
        dirname="phjob_"+str(i)
        dirlist.append(dirname)
        try:
            os.mkdir(dirname)
        except OSError:
            print('directry already exist')
        shutil.copy2(args.scfFile, dirname)
        
        #copy upf file (consider extention=upf case)
        files=glob.glob("*[upf UPF]")
        print(files)
        
        for j in files:
            shutil.copy2(j, dirname)
            
        
        os.chdir(dirname)
        phononInput=prefixName+".phonon.in"
        
        fp=open(phononInput,"w")
        fp.write(prefixName+" phonon \n")
        fp.write('&inputph \n')
        fp.write(prefix+'\n')
        fp.write(outdir+'\n')
        fp.write('tr2_ph=1.0d-16 \n')
        fp.write('fildyn=\''+prefixName+".dyn\' \n")
        fp.write('fildvscf=\'dvscf\'\n')
        fp.write('alpha_mix(1)=0.2 \n')
        fp.write('trans=.true. \n')
        fp.write('ldisp=.true. \n')
        if (args.polar):
            fp.write('epsil=.true. \n')
        
        fp.write('nq1='+str(args.qmesh[0])+',nq2='+str(args.qmesh[1])+',nq3='+str(args.qmesh[2])+'\n')
        
        fp.write('start_q='+ str(loadmin[i])+' \n')
        fp.write('last_q='+ str(loadmax[i])+' \n')
            
        fp.write('/\n')
        fp.close()
        
        
        #write runscript
        #for muse system
        #please modify pwscfRoot and nodes and so on appropriate
        pwscfRoot="/home/emi/espresso/install-test/qe-6.2/bin/"
        nodes=24
        frun=open("phrun.sh","w")
        frun.write("#!/bin/csh \n")
        frun.write("#$ -cwd  \n")
        frun.write("#$ -V -S /bin/bash  \n")
        frun.write("#$ -N "+prefixName+"-ph-"+str(i)+"\n")
        frun.write("#$ -o stdout \n")
        frun.write("#$ -e stdout \n")
        frun.write("#$ -pe smp "+str(nodes) +" \n")
        frun.write("mpirun "+ pwscfRoot+"pw.x"+ " -npool " +str(nodes) +" < "+args.scfFile+ " > scf.out \n")
        frun.write("mpirun "+ pwscfRoot+"ph.x"+ " -npool " +str(nodes) +" < "+phononInput+ " > phonon.out \n")
        frun.close()
        
        os.chdir('../')   
    
    
    #bash script for running job at once
    
    fallrun=open("runall.sh","w")
    fallrun.write("#!/bin/sh \n")
    
    for i in dirlist:
        fallrun.write("cd "+i +"\n")
        fallrun.write("qsub phrun.sh \n")
        fallrun.write("cd ../ \n")
    
    fallrun.close()
    
    #output directry list for post process purpose
    fdirlist=open("directoryList.txt","w")
    
    for i in dirlist:
        fdirlist.write(i +"\n")
    
    fdirlist.close()
        
                
        
    
    
    
    