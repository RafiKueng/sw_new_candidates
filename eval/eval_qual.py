
import cPickle as pickle


print 'candidates, load_pickle'
with open('candidates.pickle', 'rb') as f:
    candidates = pickle.load(f)


data = {}
no_swid = []

print "\nreading cat_qual.txt"            
 
with open("cat_qual.txt") as f:
    for i, l in enumerate(f.readlines()):
        print "line %02i" % i,
        l = l.strip()
        try:
            swid  = l[0:4]
            asw = l[5:15]
            mid   = l[16:26]
            qua   = l[29:30]
            txt   = l[31:]
        except IndexError:
            print "[invalid line, SKIPPING]", "!"*10
            continue
        print swid, asw, '%10s'%mid, qua, txt,
                
        
        if not swid == "----" and qua in ['+','-','?']:
            
            d = {'c1': (qua, txt), 'asw':asw,'swid':swid}
            #data[asw] = d
            data[swid] = d
            print "[saved]"
        
        else:
            no_swid.append(asw)
            print "[no swid or no qualifier, SKIPPED]"


print "\ncheck if skipped really don't have swid"
for asw in no_swid:
    try:
        # this should usually fail..
        swid = candidates['asw'][asw]['swid']
        print "-> %s - %s" % (asw, swid)
    except KeyError:
        # all is fine, go on
        continue



print '-'*80
print "\nreading notes.txt"            
            
with open("notes.txt") as f:
    for i, l in enumerate(f.readlines()):
        print "line",i,
        l = l.strip()
        try:
            asw = l[0:10]
            elems = [_.strip() for _ in l[11:].split(';')]
            qua = elems.pop(0)
            tags = elems
            
        except IndexError:
            print "skipping"
            continue

        swid = candidates['asw'][asw]['swid']
        print asw, swid, qua, tags
        dd = {'c2': (qua, tags),'asw':asw,'swid':swid}
        
        if data.has_key(swid) and not data[swid]['asw'] == asw:
            print "  !! paranoia alarm"
        
        if not data.has_key(swid):
            print "  !! new one"
            #data[asw] = d
            data[swid] = dd
        else:
            data[swid].update(dd)



print '-'*80
print "\nreading manually.txt"            
            
with open("manually.txt") as f:
    for i, l in enumerate(f.readlines()):
        print "line",i,
        l = l.strip()
        prts = l.split()
        swid = prts[0]
        qua = int(prts[1])
        try:
            tags = [prts[2]]
        except IndexError:
            tags = []

        asw = candidates['swid'][swid]['asw']
        print asw, swid, qua, tags
        dd = {'c3': (qua, tags),'asw':asw,'swid':swid}
        
        
        if not data.has_key(swid):
            print "  !! new one"
            #data[asw] = d
            data[swid] = dd
        else:
            data[swid].update(dd)



            
print '-'*80

# check which are missing
print "\n\nchecking completeness"

missing = []
for cswid in candidates['swid'].keys():
    if cswid not in data.keys():
        print " > missing:", cswid, candidates['swid'][cswid]['asw']
        missing.append((cswid, candidates['swid'][cswid]['asw']))
    
    
print '-'*80
    
    
# check if we agree, just for fun, use second rating anyways
print "\n\nchecking ratings"

nicedata = {}

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
    'XX': None,
}


flags_lut = {
# more modelling
    "m_model" : ('nw', 'more modelling needed'),
}


for k,v in sorted(data.items()):
    swid = v['swid']
    asw = v['asw']
    flags = []
    print " >",k,asw,
    
    c1 = v.get('c1',('XX',''))
    c2 = v.get('c2',('XX',[]))
    c3 = v.get('c3',('XX',[]))
    
    r1 = c1[0]
    r2 = c2[0]
    r3 = c3[0]
    
    tag = c1[1]
    tags = c2[1]
    tags3 = c3[1]
    
    if not tag == '':
        tags.append(tag)
    tags.extend(tags3)
    
    if lut.has_key(r2):
        rat = lut[r2]
    else:
        print "!!!!! why2??", r2, '!'*10
        continue
    
    if not lut.has_key(r1):
        print "!!!!! why1??", r1, '!'*10
        continue

    if not lut[r1] == lut[r2]:
        print "(missmatch here:", r2, 'vs', r1, ')',
    
    if rat == None:
        if not r3=="XX":
            print " !man override! ",
            rat = r3
        else:
            print "no rating available",
    
    
    print "  [%s]" % rat
    
    #scan for flags:
    for flag, kws in flags_lut.items():
        for kw in kws:
            for tag in tags:
                if kw in tags:
                    # set the flag
                    if flag not in flags:
                        flags.append(flag)
    
    nicedata[swid] = {'rating':rat, 'tags':tags, 'asw': asw, 'flags': flags}



print '-'*80


# general check for completeness
print "\ngeneral check for completness\n"
for swid in ['SW%02i'%i for i in range(1,60)]:
    if not swid in nicedata.keys():
        print " - missing:",swid

print '-'*80


#creating nice latex output

ttl = r"\subsection{%s}"
pre = r"\begin{itemize}"
fmt = r"  \item %s (%s)"
pst = r"\end{itemize}"


for wrd, rat in {'convincing' : 2,'plausible' : 1,'unclear' : 0,'doubtful': -1}.items():
    print "\n"+ ttl % wrd
    print pre
    for n in sorted([(k, d['asw']) for k, d in nicedata.items() if d['rating']==rat]):
        print fmt % n
    print pst

print "\n" + ttl % "missing"
print pre
for n in sorted(missing):
    print fmt % n
print pst
    

import cPickle as pickle
pickle_filename = 'nicedata.pickle'
print 'eval.py: save_pickle'
with open(pickle_filename, 'wb') as f:
    pickle.dump(candidates, f, -1)
    
    

            