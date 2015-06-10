# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 20:18:39 2015

@author: rafik
"""
import os
import cPickle as pickle


picklename = 'tmp_all_models.pickle'
csvname = 'tmp_all_models.csv'


data = {}

keys = [] # all the data keys we have


def collect_all_models():
    
    import get_old_models as old_models
    import get_new_models as new_models
    
    for mid, d in old_models.data.items():
        data[mid] = d
        
    for k in d.keys():
        if not k in keys:
            keys.append(k)
        
    for mid, d in new_models.data.items():
        data[mid] = d

    for k in d.keys():
        if not k in keys:
            keys.append(k)
    
def check_swid():

    import candidates
    
    for mid, d in data.items():
        n_swid = candidates.get_swid.get(d['asw'], '----')
        o_swid = d.get('swid', '-NONE-')
        
        if not n_swid == o_swid:
            print "   problem: not matching swid with %s: %s vs %s" % (str(mid), n_swid, o_swid)
            data[mid]['swid'] = n_swid

def set_type():

    for mid, d in data.items():
        if type(mid)==int:
            d['type'] = 'old'
        elif (type(mid)==unicode or type(mid)==str) and len(mid)==10:
            d['type'] = 'new'
        else:
            print mid
            print len(mid)
            print type(mid)
            raise ValueError('what a strange mid')

    

            
def save_csv():
    print "get_all_models: save_csv"
    with open(csvname, 'w') as f:
        f.write(','.join(keys)+'\n')
        
        for mid, dic in data.items():
            for k in keys:
                if k in dic.keys():
                    f.write('%s,' % str(dic[k]))
                else:
                    f.write(',')
            f.write('\n')
  

def save_pickle():
    print "get_all_models: save_pickle"
    
    with open(picklename, 'w') as f:
        pickle.dump(data, f, -1)






def main():
    collect_all_models()
    check_swid()
    set_type()
    save_csv()
    save_pickle()
    


if __name__ == "__main__":
    main()
else:
    if os.path.isfile(picklename):
        print "loaded new models from temp pickle"
        with open(picklename) as f:
            data = pickle.load(f)
    else:
        main()
        
