
import cPickle as pickle


print 'candidates, load_pickle'
with open('candidates.pickle', 'rb') as f:
    candidates = pickle.load(f)


data = {}
 
with open("cat_qual.txt") as f:
    for i, l in enumerate(f.readlines()):
        print "line",i,
        l = l.strip()
        try:
            swid  = l[0:4]
            asw = l[5:15]
            mid   = l[16:26]
            qua   = l[29:30]
            txt   = l[31:]
        except IndexError:
            print "skipping"
            continue
        print swid, asw, mid, qua, txt
                
        
        if not swid == "----" and qua in ['+','-','?']:
            
            d = {'c1': (qua, txt), 'asw':asw,'swid':swid}
            #data[asw] = d
            data[swid] = d
            
            
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
            

# check which are missing
print "\n\nchecking completeness"

missing = []
for cswid in candidates['swid'].keys():
    if cswid not in data.keys():
        print " > missing:", cswid, candidates['swid'][cswid]['asw']
        missing.append((cswid, candidates['swid'][cswid]['asw']))
    
    
    
    
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


for k,v in data.items():
    swid = v['swid']
    asw = v['asw']
    flags = []
    print " >",k,asw,
    
    c1 = v.get('c1',('XX',''))
    c2 = v['c2']
    
    r1 = c1[0]
    r2 = c2[0]
    
    tags = c2[1]
    tag = c1[1]
    
    if not tag == '':
        tags.append(tag)
    
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
    
    print ""
    
    #scan for flags:
    for flag, kws in flags_lut.items():
        for kw in kws:
            for tag in tags:
                if kw in tags:
                    # set the flag
                    if flag not in flags:
                        flags.append(flag)
    
    nicedata[swid] = {'rating':rat, 'tags':tags, 'asw': asw, 'flags': flags}

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
    
    
    
    
    

            