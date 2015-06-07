# -*- coding: utf-8 -*-
"""
Created on Wed May 27 17:20:02 2015

@author: rafik
"""

import requests as rq



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
		continue

	if 'content-type' in r.headers and 'json' in r.headers['content-type']:
		print 'ERROR: no valid png file (json)' 

	with open(path, 'w') as f:
		for chunk in r.iter_content(1024*4):
			f.write(chunk)
	print 'done'

	
    
def fetch_talk():
    
	models = []
	
	page = 1
	
	while True:

		print "scanning pg", page
		url = "https://api.zooniverse.org/projects/spacewarp/talk/boards/BSW0000006/discussions/DSW0000eo1?page=%i" % page
		
		resp = rq.get(url)
		
		try:
			comms = resp.json()['comments']
		except KeyError:
			break
		
		print ".. found n comments:", len(comms)
		
		for i, comm in enumerate(comms)
			txt = comm['body']
			lines = txt.split('\r\n')
			
			for line in lines:
				parts = line.split('-')
				if len(parts) == 3 and parts[1].startswith('*** Rev'):
					mdl = parts[2].strip()
					models.append(mdl)
					print "    comm", i, "; found model: ", mdl
		page = page + 1
	return models
	
def writemodels(models):
	with open('new_models.txt', 'w') as f:
		f.writelines(models)
		
def parse_config(model_id):
	with open(cfgtmpl % model_id) as f:
		lns = f.readlines()
	
	for l in lns:
		if "" in l:
			return "ok"
	return "chk"


def getmodels():
	
	path = '.'
	
	models = []
	
	with open('oldmodels.txt') as f:
		lns = f.readlines()
	for ln in lns:
		models.append(('old', ln))

	with open('newmodels.txt') as f:
		lns = f.readlines()
	for ln in lns:
		models.append(('new', ln))


	nmodels = []
	for tp, model_id in models:
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
			
	
			
	
	
	