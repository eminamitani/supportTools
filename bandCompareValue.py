'''
Created on 2018/08/09

script for plot graph to compare wannier90 and espresso original band structure
this script has a function to evaluate the eigenvalue difference
@author: Emi Minamitani
'''
import argparse
import os
import numpy as np
import re
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='comparison of band ', fromfile_prefix_chars='@')
    parser.add_argument('--wanBand', metavar='filename of band data obtained from wannier90', action='store')
    parser.add_argument('--wangnu', metavar='filename of gnuscript obtained from wannier90', action='store')
    parser.add_argument('--pwBand', metavar='filename of band data obtained by pw.x', action='store')
    parser.add_argument('--pwrange', metavar='the range of band index to compare in espresso output:initial and final band index', type=int, nargs=2,action='store')
    parser.add_argument('--wanrange',metavar='the range of band index to compare in wannier output :initial and final band index', type=int, nargs=2,action='store')
    
    args=parser.parse_args() 
    
    nbandpw=args.pwrange[1]-args.pwrange[0]
    nbandwan=args.wanrange[1]-args.wanrange[0]
    
    if(nbandpw-nbandwan >0):
        print("number of band is different")
    
    wanband=open(args.wanBand, "r")
    wbdata=wanband.readlines()
    wanband.close()
    
    wangnu=open(args.wangnu,"r")
    gnu=wangnu.readlines()
    wangnu.close()
    
    pwband=open(args.pwBand,"r")
    pwdata=pwband.readlines()
    pwband.close()
    
    #find break point in band data
    counter=0
    wanbp=0
    for i in wbdata:
        if len(i.split())==0:
            wanbp=counter
            break
           
        
        counter=counter+1
         
    print(wanbp)
    
    counter=0
    pwbp=0
    for i in pwdata:
        if len(i.split())==0:
            pwbp=counter
            break
           
        
        counter=counter+1
         
    print(pwbp)
    
    if(wanbp-pwbp>0):
        print ("number of k-point is different!")
    
    maxkwan=float(wbdata[wanbp-1].split()[0])
    maxkpw=float(pwdata[pwbp-1].split()[0])
    #print(maxkwan)
    #print(maxkpw)
    
    #gather eigenvalues for selected band
    wbpos=[]
    wbpos.append(0)
    for i in range(len(wbdata)):
        if len(wbdata[i].split())==0:
            wbpos.append(i+1)
            
    
    pbpos=[]
    pbpos.append(0)
    for i in range(len(pwdata)):
        if len(pwdata[i].split())==0:
            pbpos.append(i+1)
    
    #print(wbpos)
    #print(pbpos)
    
    #print(args.wanrange[0])
    #print(args.wanrange[1])
    wbeig=[]
    wbkpt=[]
    for i in range(len(wbpos)):
        if(i>=args.wanrange[0]-1 and i<=args.wanrange[1]-1 ):
            #print(i)
            for j in range(wanbp):
                #print(wbdata[wbpos[i]+j].split())
                wbeig.append(float(wbdata[wbpos[i]+j].split()[1]))
                wbkpt.append(float(wbdata[wbpos[i]+j].split()[0]))
    
    pbeig=[]
    #print(args.pwrange[0])
    #print(args.pwrange[1])
    for i in range(len(pbpos)):
        if(i>=args.pwrange[0]-1 and i<=args.pwrange[1]-1 ):
            #print(i)
            for j in range(pwbp):
                pbeig.append(float(pwdata[pbpos[i]+j].split()[1]))
            
    #check the output
    fwan=open("waneig.dat","w")
    for i in wbeig:
        fwan.write(str(i)+"\n")
    fwan.close
    
    fpw=open("pweig.dat","w")
    for i in pbeig:
        fpw.write(str(i)+"\n")
    fpw.close()
    
    eigdiff=[]
    
    if(len(pbeig)-len(wbeig) >0):
        print("number of eigenvalue in pw and wannier is different")
        
    for i in range(len(pbeig)):
        eigdiff.append(float(pbeig[i])-float(wbeig[i]))
        
    print("max positive difference:"+str(max(eigdiff)))
    print("max negative difference:"+str(min(eigdiff)))
    
    diffmax=max(abs(min(eigdiff)),max(eigdiff))
    print("maxdiff:"+str(diffmax))
    
    #plotting script for gnuplot with difference weight
    
    fdiff=open("difference.dat","w")
    counter=0
    for i in range(nbandwan):
        for j in range(wanbp):
            fdiff.write(str(wbkpt[counter]) + "  "+ str(wbeig[counter]) +"   "+ str(eigdiff[counter]) +"\n")
            counter=counter+1
        
        fdiff.write("\n")
    
    fdiff.close()
            
    
        
    
    scale=maxkwan/maxkpw
    
    #parse the data in gnuplot script
    ymin=0.0
    ymax=0.0
    sympoints=[]
    pointsline=" "
    for i in gnu:
        if i.find("yrange")>=0:
            enerange=re.findall(r"-?[0-9]+.[0-9]+",i)
            print(enerange)
            ymin=float(enerange[0])
            ymax=float(enerange[1])
        
        if i.find("xtics") >=0:
            pointsline=i
            points=re.findall(r"[0-9]+.[0-9]+",i)
            print(points)
            for j in points:
                sympoints.append(float(j))
                
    
    
    print(sympoints) 
    print(pointsline)      
    
    gp=open("gnuplot.plt", "w")
    gp.write("set term postscript eps enhanced color \"Arial\" 25 \n")
    gp.write("set output \"compare.eps\" \n")
    gp.write("set style data dots \n")
    gp.write("set key below \n")
    gp.write("ymin= "+ str(ymin) +"\n")
    gp.write("ymax= "+ str(ymax) +"\n")
    gp.write("set xrange [0.0: "+str(maxkwan) +" ] \n")
    gp.write("set yrange [ymin : ymax ] \n")
    for i in sympoints:
        gp.write("set arrow from "+ str(i) + " , " + "ymin" + " to " + str(i) +" , ymax  nohead \n")
    gp.write(pointsline)
    
    gp.write("plot \"" +args.wanBand +"\" ti \" wannier \" w l lw 3, \\\n")
    gp.write("\"" +args.pwBand +"\" using ($1)*"+str(scale) +":2 ti \" original \" w l lc rgb \"blue\" lt 2 \n")
    
    
    gp.close()
    
    Ediffmax=max(wbeig)
    Ediffmin=min(wbeig)
    gpdiff=open("gnuplot_diff.plt", "w")
    gpdiff.write("set term postscript eps enhanced color \"Arial\" 25 \n")
    gpdiff.write("set output \"compare_diff.eps\" \n")
    gpdiff.write("set style data dots \n")
    gpdiff.write("set key below \n")
    gpdiff.write("ymin= "+ str(Ediffmin) +"\n")
    gpdiff.write("ymax= "+ str(Ediffmax) +"\n")
    gpdiff.write("set xrange [0.0: "+str(maxkwan) +" ] \n")
    gpdiff.write("set yrange [ymin : ymax ] \n")
    for i in sympoints:
        gpdiff.write("set arrow from "+ str(i) + " , " + "ymin" + " to " + str(i) +" , ymax  nohead \n")
    gpdiff.write(pointsline)
    
    gpdiff.write("set cbrange["+str(-diffmax)+":"+str(diffmax)+"] \n")
    gpdiff.write("set title \"wannier interpolation difference\" \n")
    gpdiff.write("set palette defined ( 0 '#0fffee',1 '#0090ff', 2 '#000fff',3 '#000090',4 '#000000',5 '#7f0000', 6 '#ee0000', 7 '#ff7000', 8 '#ffee00') \n")
    gpdiff.write("plot \"difference.dat\" using 1:2:3 noti  w l lc palette \n")
    
 
    
    
    gpdiff.close()
    
    
    
    
    
    
