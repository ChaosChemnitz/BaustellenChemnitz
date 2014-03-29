#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request, json, urllib.parse

from scrape import DateTimeEncoder

def findIntersection(street1, street2):

	a = '%3Cosm-script%20output%3D%22json%22%20timeout%3D%2225%22%3E%0A%20%20%20%20%3Cid-query%20type%3D%22area%22%20ref%3D%223600062594%22%20into%3D%22area%22%2F%3E%0A%20%20%20%20%3Cunion%3E%0A%20%20%20%20%20%20%20%20%3Cquery%20type%3D%22way%22%3E%0A%20%20%20%20%20%20%3Chas-kv%20k%3D%22name%22%20v%3D%22'
	b = '%22%2F%3E%0A%20%20%20%20%20%20%3Carea-query%20from%3D%22area%22%2F%3E%0A%20%20%20%20%3C%2Fquery%3E%0A%20%20%3C%2Funion%3E%0A%20%20%3C%21--%20print%20results%20--%3E%0A%20%20%3Cprint%20mode%3D%22body%22%2F%3E%0A%20%20%3Crecurse%20type%3D%22down%22%2F%3E%0A%20%20%3Cprint%20mode%3D%22skeleton%22%20order%3D%22quadtile%22%2F%3E%0A%3C%2Fosm-script%3E'

	data = '<osm-script>' + \
		'<osm-script output="json" timeout="25">' + \
			'<id-query into="area" {{nominatimArea:Chemnitz}} type="area"/>' + \
			'<union>' + \
				'<query type="way">' + \
					'<has-kv k="name" v="PLACEHOLDER"/>' + \
					'<area-query from="area"/>' + \
				'</query>' + \
			'</union>' + \
			'<print mode="body"/>' + \
			'<recurse type="down"/>' + \
			'<print mode="skeleton" order="quadtile"/>' + \
		'</osm-script>' + \
	'</osm-script>'

	response = urllib.request.urlopen("http://overpass-api.de/api/interpreter?data=" + a + urllib.parse.quote(street1) + b )
	content = response.read()
	data1 = json.loads(content.decode('utf8'))

	response = urllib.request.urlopen("http://overpass-api.de/api/interpreter?data=" + a + urllib.parse.quote(street2) + b )
	content = response.read()
	data2 = json.loads(content.decode('utf8'))

	if(len(data1['elements']) == 0 or len(data2['elements']) == 0):
		return

	d = set(data1['elements'][0]['nodes'])
	e = set(data2['elements'][0]['nodes'])

	f = e.intersection(d)

	g = []
	for node in data2['elements']:
		if node['type'] == 'node' and node['id'] in list(f):
			g.append({'lat': node['lat'], 'lon': node['lon']})

	return g


f = open('data.json')
data = json.load(f)

found = []
i = 0
for entry in data:
	i += 1
	if 'location' in entry['parsed'] and entry['parsed']['location']['relation'] == 'intersection':
		street1 = entry['street']
		street2 = entry['parsed']['location']['streets'][0]
		# remove "
		street1 = street1.replace('"', '')
		street2 = street2.replace('"', '')
		print('%2i/%2i process %s %s'%(i, len(data), street1, street2))
		entry['geodata'] = findIntersection(street1, street2)
		found.append(entry)
	else:
		print('%2i/%2i'%(i, len(data)))

f = open('data-parsed.json', 'w')
json.dump(found, f, cls=DateTimeEncoder)
f.close()
