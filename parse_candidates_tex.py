# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 02:38:54 2015

@author: rafik
"""

def write_csv():
    with open('candidates.csv', 'w') as f:
        for c in candidates:
            f.write('\t'.join(c)+'\n')

candidates = []

with open('candidates.tex') as f:
    lns = f.readlines()
    
for line in lns:
    line = line.strip().strip('\\')
    line = line.replace('\,', ' ')
    line = line.replace('$-$', '-')
    line = line.replace('$+$', '+')
    tkns = line.split('&') 
    tkns = [_.strip() for _ in tkns]
    tkns[0] = "SW%02i" % int(tkns[0][2:])
    candidates.append(tkns)
    
            
write_csv()
