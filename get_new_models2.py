# coding: utf-8
import requests as rq


r1 = rq.get('http://swlabs:8080/db/spaghetti/_design/isfinal/_view/isfinal')

rows = r1.json()['rows']

data = {}
for row in rows:
    mid = row['id']
    lensid = row['value']['lens_id']
    r2 = rq.get('http://swlabs:8080/db/lenses/'+lensid)
    asw = r2.json()['metadata']['zooniverse_id']
    cdate = row['value']['created_at']
