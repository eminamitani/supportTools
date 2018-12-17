'''
Created on 2017/10/17
making input for epw based on QE SCF calculation input
this program just create templete, and need to combine with sed or something more purpose specific script
(for example set-up projection related parameters, disentangle related parameters...etc)
@author: Emi Minamitani
'''

import argparse
import os
import numpy as np
import re
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='phonon input ', fromfile_prefix_chars='@')
    parser.add_argument('--scfFile', metavar='filename of scf calculation of pw.x', action='store')
    parser.add_argument('--wanmesh', metavar='mesh for wannier interpolation in 3 direction, total 3 number required', type=int, action='store',nargs=3)
    parser.add_argument('--prefix', metavar='prefix for QE calculation', type=str,action='store')
    parser.add_argument('--phononDir', metavar='path or QE phonon calculation',type=str, action='store')
    parser.add_argument('--polar', metavar='include long range electrostatic force effect or not', type=bool, default="true", action='store')
    parser.add_argument('--fermiread', metavar='set up Ef by manual', type=bool, default="true", action='store')

    
    args=parser.parse_args()   
    print(args.scfFile)
    f=open(args.scfFile,"r")
    lines=f.readlines()  
    f.close()
    
    #copy to epw.scf.in
    
    fscf=open(args.prefix+".epw.scf.in","w")
    
    for i in lines:
        fscf.write(i)
    
    fscf.close()
    
    #extract mass and some informations from scf file for epw input
    outdir=" "
    ntype=0
    for i in lines:
        if(i.find("ntyp")>=0):
            ntype=int(i.strip(" ").strip("\n").split("=")[1])
        if(i.find("outdir")>=0):
            outdir=i
    
    print("number of type="+str(ntype))
    
    type=[]
    mass=[]
    count=0
    for i in lines:
        if (i.find("ATOMIC_SPECIES")>=0):
            for j in range(ntype):
                info=lines[count+1+j].strip(" ").strip("\n").split(" ")
                type.append(info[0])
                mass.append(info[1])
        count=count+1
    
    print(type)
    print(mass)
    
    
    #making nscf input
    #replace calculation tag and kpoint block
    
    #first generate kpoint mesh
    meshpoint=[]
    x=np.linspace(0,1,args.wanmesh[0], endpoint=False)
    y=np.linspace(0,1,args.wanmesh[1], endpoint=False)
    z=np.linspace(0,1,args.wanmesh[2], endpoint=False)
    
    

    weight=1.0/args.wanmesh[0]/args.wanmesh[1]/args.wanmesh[2]
    
    for xx in x:
        for yy in y:
            for zz in z:
                
                kx=xx
                ky=yy
                kz=zz
                
                meshpoint.append([kx,ky,kz, weight])
    
    count=0
    
    for i in lines:
       
        if (str(i).find('calculation')>=0):
            lines[count]="calculation=\'nscf\'\n"
        
        if (str(i).find('K_POINTS')>=0):
            lines[count]="K_POINTS crystal \n"
            lines[count+1]=str(args.wanmesh[0]*args.wanmesh[1]*args.wanmesh[2])+" \n"
            for i in meshpoint:
                lines.append(str(i[0])+" "+str(i[1])+" "+str(i[2])+ " "+str(i[3])+"\n")
        count=count+1
    
    fnscf=open(args.prefix+".epw.nscf.in","w")
    
    for i in lines:
        fnscf.write(str(i))
    
    fnscf.close()
    
    
    #extract the irreduciable qpoint in phonon calculation
    
    path=str(args.phononDir)+"/"+str(args.prefix)+".dyn0"

    
    try:
        fdyn=open(path)
    except FileNotFoundError:
        #split case
        path=str(args.phononDir)+"/phjob_0/"+str(args.prefix)+".dyn0"
        fdyn=open(path)
        
    phononLines=fdyn.readlines()
    
    #number of irreduciable q-point
    nirr=len(phononLines)-2
    qmeshinfo=phononLines[0]
    match=re.findall(r'[0-9]+',qmeshinfo)
    
    qmesh=[]
    for i in match:
        qmesh.append(int(i))
            
    print(qmesh)
    
    irrq=[]
    for i in range(nirr):
        irrq.append(phononLines[i+2].strip(" ").strip("\n"))
        
    #print(irrq)
    
    
    
    fepw=open(args.prefix+".epw.in", "w")
    fepw.write('-- \n') #arbitaly string
    fepw.write('&inputepw \n')
    fepw.write("prefix= \'"+args.prefix+"\' \n")
    for i in range(len(type)):
        fepw.write("amass("+str(i+1)+")= "+str(mass[i])+"\n")
    fepw.write(outdir)
    
    fepw.write("iverbosity  =0 \n")
    fepw.write("elph        = .true.\n")
    fepw.write("epbwrite    = .true.\n")
    fepw.write( "epbread     = .false. \n")
    if (args.polar):
        fepw.write( "lpolar      = .true. \n")
    
    fepw.write( "epwwrite    = .true. \n")  
    fepw.write( "epwread     = .false. \n") 
    
    fepw.write( "nbndsub     =  !replace by appropriate number \n") 
    fepw.write( "nbndskip     =  !replace by appropriate number \n") 
    
    fepw.write( "wannierize  = .true. \n") 
    fepw.write("iprint  =2 \n")
    
    fepw.write("\n")
    fepw.write("!wannier control tags \n")
    fepw.write( "dis_win_min     =  !replace by appropriate number \n") 
    fepw.write( "dis_win_max     =  !replace by appropriate number \n")
    fepw.write( "dis_froz_min     =  !replace by appropriate number \n") 
    fepw.write( "dis_froz_max     =  !replace by appropriate number \n")
    
    for i in range(len(type)):
        fepw.write("proj("+str(i+1)+")= \'"+str(type[i])+":  \' !write specific orbital such as s:p:sp3 \n")
 
    
    fepw.write('wdata(1) =\'dis_num_iter = 1000 \' !set maximum iteration number\n')
    fepw.write("\n")
    fepw.write("!epc calculation control tags \n")
    fepw.write( "elecselfen  = .true. \n") 
    fepw.write( "phonselfen  = .true. \n") 
    fepw.write( "a2f         = .false. \n")
    fepw.write( "parallel_k  = .true. \n")
    fepw.write( "parallel_q  = .false. \n")
    fepw.write( "fsthick     = 1.0 ! eV  \n")
    fepw.write( "eptemp      = 100 ! K  \n")
    fepw.write( "degaussw    = 0.05 ! eV \n")
    
    if(args.fermiread):
        fepw.write( "efermi_read = .true. \n")
        fepw.write( "fermi_energy =   !replace by appropriate number \n")
        
    fepw.write( "dvscf_dir   = \'" +args.phononDir+"/save\' \n")
    fepw.write("\n")
    fepw.write("!Wannier fine mesh \n")
    fepw.write( "nkf1        = !replace by appropriate number  \n")
    fepw.write( "nkf2        = !replace by appropriate number  \n")
    fepw.write( "nkf3        = !replace by appropriate number  \n")
    
    
    fepw.write( "!if you want to calculate on specific path, please use   \n")
    fepw.write( "!filqf  = 'path'  \n")
    fepw.write( "nqf1        = !replace by appropriate number  \n")
    fepw.write( "nqf2        = !replace by appropriate number  \n")
    fepw.write( "nqf3        = !replace by appropriate number  \n")
    fepw.write("\n")
    fepw.write("!original mesh \n")
    
    fepw.write( "nk1        ="+ str(args.wanmesh[0]) +"\n")
    fepw.write( "nk2        ="+ str(args.wanmesh[1]) +"\n")
    fepw.write( "nk3        ="+ str(args.wanmesh[2]) +"\n")
    
    
    fepw.write( "nq1        ="+ str(qmesh[0]) +"\n")
    fepw.write( "nq2        ="+ str(qmesh[1]) +"\n")
    fepw.write( "nq3        ="+ str(qmesh[2]) +"\n")
    fepw.write("/ \n")
    
    fepw.write(str(nirr)+ "  cartesian \n")
    for i in irrq:
        fepw.write(i+"    "+ "1.0000 \n")

    
    fepw.close()
    
        
    
    