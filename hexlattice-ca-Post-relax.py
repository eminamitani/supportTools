'''
Created on 2018/11/14

ca-ratio optimization: Post process
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
        caratio=float(tmp[1])
        
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
        
        datas.append([caratio,fene])

        savedir=args.prefix+".save"
        if os.path.isdir(savedir):
            print("removing save dir")
            shutil.rmtree(savedir)
        
        os.chdir("../")
    
    #sort
    sortedData=sorted(datas,key=lambda x:(x[0]))
    
    fdata=open("results.txt","w")
    fdata.write("# c/a   energy(Ry) \n")
    for data in sortedData:
        fdata.write(str(data[0])+"   "+str(data[1])+ " \n")
        
    
    fdata.close()     
    
    print("finish write file")
    #dataplot
    dataarray=np.array(sortedData)
    
    x=dataarray[:,0]
    y=dataarray[:,1]
    
    plt.plot(x,y,marker='o',ls="-")
    plt.xlabel("c/a ratio")
    plt.ylabel("total energy")
    plt.savefig("ca-ratio-E.png")
    plt.show()
    
            
    

