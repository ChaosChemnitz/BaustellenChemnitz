#!/usr/bin/env python

import bs4, urllib.request, re, datetime, pprint, json

dateRegex = '(\d{1,2})\.(\d{1,2})\.(\d{2,4})'

def extractDate(dateString):
	data = {}
	specificDate = re.match('^' + dateRegex  + '$', dateString)
	if specificDate:
		tmp = specificDate.groups()
		date = datetime.date(
			int(tmp[2]),
			int(tmp[1]),
			int(tmp[0])
		)
		data['since'] = date
		data['until'] = date
		return data

	fromToDate = re.match('^(von|ab|seit)?\s*' + dateRegex + '\s*bis\s*' + dateRegex + ',?\s*(.*)$', dateString)
	if fromToDate:
		tmp = fromToDate.groups()
		sinceDate = datetime.date(
			int(tmp[3]),
			int(tmp[2]),
			int(tmp[1])
		)
		untilDate = datetime.date(
			int(tmp[6]),
			int(tmp[5]),
			int(tmp[4])
		)
		data['since'] = sinceDate
		data['until'] = untilDate
		if tmp[7]:
			data['notice'] = tmp[7]
		return data

	fromDate = re.match('^(ab|seit)?\s*' + dateRegex + '$', dateString)
	if fromDate:
		tmp = fromDate.groups()
		date = datetime.date(
			int(tmp[3]),
			int(tmp[2]),
			int(tmp[1])
		)
		data['since'] = date
		data['until'] = None
		return data

	untilDate = re.match('^(bis)?\s*' + dateRegex + '$', dateString)
	if untilDate:
		tmp = untilDate.groups()
		date = datetime.date(
			int(tmp[3]),
			int(tmp[2]),
			int(tmp[1])
		)
		data['since'] = date
		data['until'] = None
		return data

	untilEstimatedDate = re.match('^(seit)?\s*' + dateRegex + '\s*bis voraussichtlich\s*(.*)$', dateString)
	if untilEstimatedDate:
		tmp = untilEstimatedDate.groups()
		date = datetime.date(
			int(tmp[3]),
			int(tmp[2]),
			int(tmp[1])
		)
		data['since'] = date
		data['until'] = None
		data['notice'] = 'bis voraussichtlich ' + tmp[4]
		return data

	print(dateString)

def extractLocation(locationString):
	data = {}
	between = re.match('^zwischen\s*(.*) und (.*)$', locationString)
	if between:
		data['streets'] = between.groups()
		data['relation'] = 'between'
		return data

	intersection = re.match('^(Einmündung|in Höhe)\s*(.*)$', locationString)
	if intersection:
		data['streets'] = intersection.group(1).split('/')
		data['relation'] = 'intersection'
		return data

	townwards = re.match('^(stadtwärts nach|landwärts vor)\s*(.*)$', locationString)
	if townwards:
		data['streets'] = townwards.group(1)
		data['relation'] = 'townwards-after'
		return data

	countrywards = re.match('^(stadtwärts vor|landwärts nach)\s*(.*)$', locationString)
	if countrywards:
		data['streets'] = countrywards.group(1)
		data['relation'] = 'townwards-before'
		return data

	print(locationString)

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
			tmp = extractDate(value)
			if tmp:
				tmpData['parsed']['date'] = tmp
			else:
				unparsed = True
		elif key == 'Maßnahme':
			tmpData['parsed']['action'] = value
		elif key == 'Lage':
			tmp = extractLocation(value)
			if tmp:
				tmpData['parsed']['location'] = tmp
			else:
				unparsed = True
		else:
			unparsed = True

		if unparsed:
			tmpData['content'].append({
				'key': key,
				'value': value
			})

	data.append(tmpData)

print(json.dumps(data, cls=DateTimeEncoder))




