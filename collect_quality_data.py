# -*- coding: utf-8 -*-
"""
Created on some time ago, rewritten 2016.04.19

This
- parses all the comments
- complies them to one object
- does general sanity checks of the data (or allows to do them by hand..
  see output file)

simply run it

@author: rafik
"""

import cPickle as pickle
import os
import sys
import codecs

import parse_candidates as PACA
#import plot_masses as PLMA
import create_data as CRDA

from settings import settings as S, INT, save_pickle, load_pickle, save_csv
from settings import print_first_line, print_last_line, getI, del_cache


file1 = "categorisation_of_quality.txt" # used to be cat_qual.txt
file2 = "candidate_evaluation.txt" # used to be notes.txt
file_manual = "manual_corrections.txt" # manual corrections, used to be manually.txt




DATA = {}

no_swid = []



# http://stackoverflow.com/questions/14906764/how-to-redirect-stdout-to-both-file-and-console-with-scripting
class Logger(object):
    def __init__(self, fn):
        self.terminal = sys.stdout
        self.log = codecs.open(fn, "w", encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass    
    
    def close(self):
        self.log.close()
        return self.terminal

### MAIN #####################################################################

I = getI(__file__)
print_first_line(I)


# print 'candidates, load_pickle'
# with open('candidates.pickle', 'rb') as f:
#     candidates = pickle.load(f)
MAP = PACA.MAP


print I, "reading", file1
 
with open(os.path.join(S['input_dir'], file1)) as f:
    
    print INT, "line sw   asw        mid        q comment"
    for i, l in enumerate(f.readlines()):
        print INT, "%03i " % i,
        l = l.strip()
        try:
            swid  = l[0:4]
            asw = l[5:15]
            mid   = l[16:26]
            qua   = l[29:30]
            txt   = l[31:].split(';')
        except IndexError:
            print "[invalid line, SKIPPING]", "!"*10
            continue

        if not qua in ['+','-','?']:
            qua = "X"

        print swid, asw, '%10s'%mid, qua, txt
        
        # try to look up the swid
        if swid == "----":
            swid = MAP.get(asw, "----")
        
        if not swid == "----":
            d = {'c1': (qua, txt), 'asw':asw, 'swid':swid}
            DATA[swid] = d
            # print "[saved]"

            # just a last sanity check that the labels didn't change
            if not swid == MAP[asw]:
                print INT, "missmatch:",swid, '-VS-', asw, '->', MAP[asw], "!" * 10
        
        else:
            no_swid.append((i,asw))
            print INT*2, "SKIPPED (no swid or no qualifier)"
            
print I, "check if skipped really don't have swid"
for i, asw in no_swid:
    if asw in MAP:
        print I, "ABORT ERROR, THINK AGAIN", "!"*80
            
print I, "DONE with", file1


print "\n",'-'*80,"\n"

print I, "reading", file2            
            
with open(os.path.join(S['input_dir'], file2)) as f:
    
    print INT, "line swid asw        cat         comments"
    
    for i, l in enumerate(f.readlines()):
        print INT, "%03i " % i,
        l = l.strip()
        try:
            asw = l[0:10]
            elems = [_.strip() for _ in l[11:].split(';')]
            qua = elems.pop(0)
            tags = elems
            
        except IndexError:
            print INT, "skipping", "!"*80
            continue

        swid = MAP[asw]
        print swid, asw, "%-11s"%qua, tags
        dd = {'c2': (qua, tags),'asw':asw,'swid':swid}
        
        if DATA.has_key(swid) and not DATA[swid]['asw'] == asw:
            print "  !! paranoia alarm"
        
        if not DATA.has_key(swid):
            print "  !! new one"
            #DATA[asw] = d
            DATA[swid] = dd
        else:
            DATA[swid].update(dd)





print '\n','-'*80,'\n'

print I, "reading", file_manual

with open(os.path.join(S['input_dir'], file_manual)) as f:

    print INT, "line swid asw       q  comments"
    
    for i, l in enumerate(f.readlines()):
        print INT, "%03i "%i,
        l = l.strip()
        prts = l.split()
        swid = prts[0]
        qua = int(prts[1])
        try:
            tags = [prts[2]]
        except IndexError:
            tags = []

        asw = MAP[swid]
        print swid, asw, qua, tags
        dd = {'c3': (qua, tags),'asw':asw,'swid':swid}
        
        if not DATA.has_key(swid):
            print INT, "   !! new one"
            #DATA[asw] = d
            DATA[swid] = dd
        else:
            DATA[swid].update(dd)


            
print '\n','-'*80,'\n'



# check which are missing
print I, "checking completeness"

missing = []
for paca_asw in PACA.DATA.keys():
    paca_swid = MAP[paca_asw]
    if paca_swid not in DATA.keys():
        print " > missing:", paca_swid, paca_asw
        missing.append((paca_swid, paca_asw))
        
print I, "DONE, found %s missing items" % len(missing)
    
    
print '\n','-'*80,'\n'



# check if we agree, just for fun, use second rating anyways
print I, "checking ratings"


# look up table to convert different ratings to universal int ratings -1, ..., 2
lut = {
#  2  convincong
    '+' : 2, 
    'convincing' : 2,
#  1  plausible
    'plausible' : 1,
#  0  unclear
    'unclear' : 0,
    '?': 0,
# -1  doubtful
    'doubtful': -1,
    '-':-1,
# NAN no rating:
    'X': None,
}

lut.update({-1:-1,0:0,1:1,2:2,None:None})

# official description for uniform print
rlut = {
    -1: "doubtful",
     0: "unclear ",
     1: "plausibl",
     2: "convncng",
  None: " -none- ",
}

# add inofficial ones to rlut
for k,v in lut.items():
    rlut[k] = rlut[v]

flags_lut = {
# more modelling
    "m_model" : ('nw', 'more modelling needed'),
}

print INT, u"         override ┐  ┌ ratings_fit?"
print INT, u"swid asw          │  │   rating1    rating2    rating3       flags     tags "
print INT, u" │    │           │  │    │          │          │             │         │"
     #       SW01 ASW0004dv8   X convncng plausibl  -none-    [1]
for k,v in sorted(DATA.items()):
    swid = v['swid']
    asw = v['asw']
    
    print INT, swid, asw,
    
    c1 = v.get('c1',('X',[]))
    c2 = v.get('c2',('X',[]))
    c3 = v.get('c3',('X',[]))
    
    # ratings
    r1 = c1[0]
    r2 = c2[0]
    r3 = c3[0]
    
    # tags
    t1 = c1[1]
    t2 = c2[1]
    t3 = c3[1]
    
    rat = None
    tags = []
    flags = []
    chosenr=0

    for t in t1 + t2 + t3:
        if t:
            tags.append(t)
    
    if lut.has_key(r2):
        rat = lut[r2]
        chosenr = 2
    else:
        print "!!!!! why?? strange rating in main file2", r2, '!'*10
        continue
    
    if rat=="X": # no rating from r2
        if lut.has_key(r1):
            rat = lut[r1]
            chosenr = 1
        else:
            print "!!!!! why1??", r1, '!'*10
            continue
        
    print " ",

    if r3!="X": # if there is NO override from r3
        rat = r3
        chosenr = 3
        print "!",
        DATA[swid]['override'] = True
    else:
        print " ",
        DATA[swid]['override'] = False
        
    if rat=="X":
        print "--", # at this point there should be no entry with no rating (it would miss completly)
    elif not lut[r1] == lut[r2]:
        print  "XX",
        DATA[swid]['conflict'] = True
    else:
        print u"  ",
        DATA[swid]['conflict'] = False

    print " ",
        
    for i,s in enumerate([rlut[r] for r in [r1,r2,r3]]):
        if i==chosenr-1:
            print "[%s]"%s,
        else:
            print " %s "%s,

    DATA[swid]['chosen'] = chosenr # which file was chosen, r1, r2, or r3
    DATA[swid]['rating'] = rat
    DATA[swid]['rating_str'] = rlut[rat]
    DATA[swid]['ratings'] = [lut[r] for r in [r1,r2,r3]]
    DATA[swid]['ratings_str'] = [rlut[r] for r in [r1,r2,r3]]
    
    
    print "   ",

    
#    if rat == None:
#        if not r3=="XX":
#            print " !man override! ",
#            rat = r3
#        else:
#            print "no rating available",
#    
#    
#    print "  [%s]" % rat
#    
    #scan for flags:
    for flag, kws in flags_lut.items():
        for kw in kws:
            for tag in tags:
                if kw in tags:
                    # set the flag
                    if flag not in flags:
                        flags.append(flag)
    print '%-8s'%(";".join(flags)), "; ".join(tags)
    
    DATA[swid].update({'asw': asw, 'tags':tags, 'flags': flags})



print '\n','-'*80,'\n'


# general check for completeness
print I, "general check for completness"

# can also contain non candidates
all_with_models_asw = set([v['asw'] for m, v in CRDA.ALL_MODELS.items()]) # from 
all_with_models = set([MAP[_] for _ in all_with_models_asw])

all_candidates_asw = set(PACA.DATA.keys()) # from spacewarps tex file
all_candidates = set([v['swid'] for k,v in PACA.DATA.items()])

missing_redshift = set([v['swid'] for k,v in PACA.DATA.items() if v['z_lens']<=0.00001])

missing_models_asw = all_candidates_asw - all_with_models_asw # set difference (in A but not in B)
missing_models = set([MAP[_] for _ in missing_models_asw])

missing_rating = all_candidates - set(DATA.keys())

conflicting_ratings = set([k for k,v in DATA.items() if v['conflict']])
overrided_rating = set([k for k,v in DATA.items() if v['override']])

oint = INT
INT=""


sanitychk_fn = os.path.join(S['output_dir'], 'sanity_checks.txt')
LOG = Logger(sanitychk_fn)
sys.stdout = LOG

print INT,u"                  ┌ R: missing rating"
print INT,u"                  │ ┌ M: missing models"
print INT,u"                  │ │ ┌ Z: missing redshift"
print INT,u" ┌ swid           │ │ │   ┌ O: overridden"
print INT,u" │    ┌ asw       │ │ │   │ ┌ C: conflicting           ┌ ratings    ┌ tags "
print INT,u" │    │           │ │ │   │ │       ┌──────────┬───────┴──┐         │ "

l = 1
for swid in ['SW%02i'%i for i in range(1,60)]:
    
    print INT, swid, MAP[swid],

    print "_"*l,
    
    # missing rating
    print ("R" if swid in missing_rating else u"_"),
        
    # missing any model
    print ("M" if swid in missing_models else u"_"),

    # missing redshift data
    print ("Z" if swid in missing_redshift else u"_"),
    
    print "_"*l,
    
    if not swid in missing_rating:
        print ("O" if swid in overrided_rating else "_"),
        print ("C" if swid in conflicting_ratings else "_"),

        print "_"*l,

        for i,s in enumerate([rlut[r] for r in DATA[swid]['ratings']]):
            if i==DATA[swid]['chosen']-1:
                print "[%s]"%s,
            else:
                print " %s "%s,
                
        print "_"*l,
        
        print "; ".join(DATA[swid]['flags'] + DATA[swid]['tags'])
        
sys.stdout = LOG.close()

INT=oint

print '\n','-'*80,'\n'


#creating nice latex output
make_latex_output = False
if make_latex_output:
    ttl = r"\subsection{%s}"
    pre = r"\begin{itemize}"
    fmt = r"  \item %s (%s)"
    pst = r"\end{itemize}"
    
    
    for wrd, rat in {'convincing' : 2,'plausible' : 1,'unclear' : 0,'doubtful': -1}.items():
        print "\n"+ ttl % wrd
        print pre
        for n in sorted([(k, d_['asw']) for k, d_ in DATA.items() if d_['rating']==rat]):
            print fmt % n
        print pst
    
    print "\n" + ttl % "missing"
    print pre
    for n in sorted(missing):
        print fmt % n
    print pst
        
    print '\n','-'*80,'\n'

pickle_fn = os.path.join(S['cache_dir'], 'ratings.pickle')
print I, 'save_pickle'
with open(pickle_fn, 'wb') as f:
    pickle.dump(DATA, f, -1)
    
    

            