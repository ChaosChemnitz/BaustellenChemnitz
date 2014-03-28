#!/usr/bin/env python

import bs4, urllib.request, re, datetime, pprint, json

import extractors.date, extractors.street

dateRegex = '(\d{1,2})\.(\d{1,2})\.(\d{2,4})'

class DateTimeEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime.datetime):
			return obj.isoformat()
		elif isinstance(obj, datetime.date):
			return obj.isoformat()
		elif isinstance(obj, datetime.timedelta):
			return (datetime.datetime.min + obj).time().isoformat()
		else:
			return super(DateTimeEncoder, self).default(obj)


soup = bs4.BeautifulSoup(urllib.request.urlopen('http://www.chemnitz.de/chemnitz/de/aktuelles/baustellenservice/index.itl'))

links = soup.select('#col2_content a')

relLinks = [link['href'] for link in links]

data = []
i = 0
for link in relLinks:
	i += 1
	print('%2i/%2i'%(i, len(relLinks)))
	tmpData = {
		'parsed': {},
		'content': []
	}
	soup = bs4.BeautifulSoup(urllib.request.urlopen('http://www.chemnitz.de/chemnitz/de/aktuelles/baustellenservice/' + link))
	box = soup.select('#col2_content')
	if(len(box) > 1):
		print('box has not exactly one element - ' + link)
	box = box[0]
	street = box.select('h2.standalone')
	if(len(street) != 1):
		print('street has not exactly one element - ' + link)
	tmpData['street'] = street[0].string
	table = box.select('tr')
	for row in table:
		key = row.find(name='th').string
		value = row.find(name='td').string
		unparsed = False
		if key in ['Einschränkung', 'Einschränkungen']:
			tmpData['parsed']['restriction'] = value
		elif key == 'Zeitraum':
			try:
				tmpData['parsed']['date'] = extractors.date.extract(value)
			except extractors.date.DateExtractionException as e:
				unparsed = True
				print('DateExtractionException:', e)
		elif key == 'Maßnahme':
			tmpData['parsed']['action'] = value
		elif key == 'Lage':
			try:
				tmpData['parsed']['location'] = extractors.street.extract(value)
			except extractors.street.StreetExtractionException as e:
				unparsed = True
				print('StreetExtractionException:', e)
		else:
			unparsed = True

		if unparsed or True:
			tmpData['content'].append({
				'key': key,
				'value': value
			})

	data.append(tmpData)

#print(json.dumps(data, cls=DateTimeEncoder))




