'''
Created on 2018/11/12

@author: Emi Minamitani
'''
import argparse 
import shutil
import os
import numpy as np
import re
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import BoundaryNorm


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='post process to determine the hexagonal lattice constant', fromfile_prefix_chars='@')
    parser.add_argument('--prefix', metavar='prefix of some temporary file firectory', type=str, action='store')
    parser.add_argument('--outfile',metavar='name of scf output file', type=str, action='store')
    
    args=parser.parse_args()
    dirs=[]
    tmp=os.listdir("./")
    
    for i in tmp:
        if os.path.isdir(i):
            dirs.append(i)
    
    datas=[]
    for idir in dirs:
        
        os.chdir(idir)
        
        tmp=idir.split("-")
        latta=float(tmp[1])
        caratio=float(tmp[3])
        
        f=open(args.outfile,"r")
        lines=f.readlines()
        f.close()
        
        final=[s for s in lines if re.match('\!.+total.*',s)]
        #print(final)
        #relaxation--> several final total energy
        #using the last data
        tf=final[-1].strip("\n").rstrip("Ry").split("=")
        #print(tf[1])
        fene=float(tf[1])
        
        datas.append([latta,caratio,fene])

        savedir=args.prefix+".save"
        if os.path.isdir(savedir):
            print("removing save dir")
            shutil.rmtree(savedir)
        
        os.chdir("../")
    
    #sort
    sortedData=sorted(datas,key=lambda x:(x[0],x[1]))
    
    fdata=open("results.txt","w")
    fdata.write("# a  c/a   energy(Ry) \n")
    for data in sortedData:
        fdata.write(str(data[0])+"  "+str(data[1])+"   "+str(data[2])+ " \n")
        
    
    fdata.close()     
    
    print("finish write file")
    #dataplot
    dataarray=np.array(sortedData)
    
    x=dataarray[:,0]
    y=dataarray[:,1]
    z1d=dataarray[:,2]
    
    #making grid point
    z=np.reshape(z1d,(len(list(set(x))),len(list(set(y)))))
    print(z)
    xgrid=np.reshape(x,(len(list(set(x))),len(list(set(y)))))
    ygrid=np.reshape(y,(len(list(set(x))),len(list(set(y)))))
    
    levels=MaxNLocator(nbins=60).tick_values(z1d.min(), z1d.max())
    cmap = plt.get_cmap('PiYG')
    norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
    
    fig, ax0=plt.subplots()
    cf=ax0.contourf(xgrid,ygrid,z,levels=levels,cmap=cmap)
    fig.colorbar(cf,ax=ax0)
    plt.xlabel("lattice constant (a.u.)")
    plt.ylabel("c/a ratio")
    plt.savefig("contour-relax.png")
    plt.show()
    
            
    

