# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 11:56:24 2015

@author: rafik
"""

import os
import cPickle as pickle

pickle_filename = 'ratings.pickle'
csv_filename = 'ratings.csv'
datafile = 'categorisation_of_quality.txt'




ratings = {}



def fetch_file():
    with open(datafile, 'r') as f:
        lines = f.readlines()
        
    for line in lines:
        line = ' '.join(line.split()) # replace multiple whitespace by just one
        elems = line.split()
        
        try:
            rr = elems[3]
        except:
            rr = ''
        if rr.startswith('l') and len(rr)>=2:
            if rr[1:]=='++':
                rat = 2
            elif rr[1:]=='+':
                rat = 1
            elif rr[1]=='?':
                rat = 0
            elif rr[1]=='-':
                rat = -1
            else:
                rat = None
        else:
            rat = None

        asw = elems[1]
        
        print asw, "has rating:", rat
        ratings[asw] = rat
    



def save_pickle():
    print "get_ratings: save_pickle"
    
    for model in _models:
        mid = model[0]
        
        data[mid] = {
            'asw'  : model[1],
            'user' : model[3],
            'swid' : model[2],
            'mid'  : mid
        }
            
    with open(pickle_filename, 'wb') as f:
        pickle.dump(ratings, f, -1)
        



data = {}

def main():
    fetch_file()
    #save_csv()
    #save_pickle()
    


if __name__ == "__main__":
    main()
else:
    if os.path.isfile(pickle_filename):
        print "loaded ratings from pickle"
        with open(pickle_filename, 'rb') as f:
            ratings = pickle.load(f)
    else:
        print "loaded ratings from file:", datafile
        main()
        

