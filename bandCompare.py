'''
Created on 2017/11/27

script for plot graph to compare wannier90 and espresso original band structure
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

    args=parser.parse_args() 
    
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
    
    maxkwan=float(wbdata[wanbp-1].split()[0])
    maxkpw=float(pwdata[pwbp-1].split()[0])
    print(maxkwan)
    print(maxkpw)
    
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
    
    
    
    
    
    
