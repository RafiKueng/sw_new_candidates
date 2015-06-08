# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 02:16:15 2015

@author: rafik
"""





all_models = []
def load_all_models():
    
    with open('all_candidate_models.csv') as f:
        for line in f.readlines():
            all_models.append(line[:-1].split(','))

candidate_id_lookup = {}
def add_candidate_id_lookup():

    with open('candidates.csv') as f:
        lns = f.readlines()
    for line in lns:
        tkn = line.strip().split('\t')
        pid = tkn[0]
        asw = tkn[8]
        
        candidate_id_lookup[asw] = pid
        
    for i, m in enumerate(all_models):
        asw = m[2].split(' ')[0]
        try:
            npid = candidate_id_lookup[asw]
        except KeyError:
            npid = '----'
        opid = m[3]
        
        if not opid=='' and not npid=='----' and not npid == opid:
            print "horrible error!! check pids", m[0], asw, npid, opid
        all_models[i][3] = npid
        




def do_something():
    path = '.'
    nmodels = []
    for _ in models:
        model_id = _[0]
        tp = _[1]
        print "get model", model_id, "(%s)" % tp

        get_single_model(tp, model_id, path)
        get_config(tp, model_id, path)
        if tp=="old":
            dat = parse_config(model_id)
        else:
            dat = "ok"
            
        nmodels.append(tp, model_id, dat)
        
    models = nmodels
    
    with open('all_models.txt', 'w') as f:
        for d in models:
            f.write(','.join(d))
            
    
            
def get_config(model_id):
    pass
        
def parse_config(model_id):
    with open(cfgtmpl % model_id) as f:
        lns = f.readlines()
    
    for l in lns:
        if "" in l:
            return "ok"
    return "chk"
    
    
cfgtmpl = '%s.config'

def get_single_model(tp, id, path):
    if tp=='old':
        url = 'http://mite.physik.uzh.ch/result/%s/state.txt' % id    
    else:
        p1 = id[:2]
        p2 = id[2:]
        url = 'http://labs.spacewarps.org/media/spaghetti/%s/%s/state.glass' % (p1, p2)
    
    path = os.path.join(path, "state_%s.gls" % id)
    
    r = rq.get(url, stream=True)
    
    if r.status_code >= 300: # requests takes care of redirects!
        print 'ERROR:', r.status_code
        return

    if 'content-type' in r.headers and 'json' in r.headers['content-type']:
        print 'ERROR: no valid png file (json)' 

    with open(path, 'w') as f:
        for chunk in r.iter_content(1024*4):
            f.write(chunk)
    print 'done'


def main():
    load_all_models()


main()
