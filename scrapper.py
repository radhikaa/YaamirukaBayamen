from bottle import route, run
import requests
import code
from pyquery import PyQuery
from newspaper import Article
import csv 
import urllib
import json
import sys
import pycps
import ast

result = []
crime_map = {}
start = "/url?q="
end = "&"
final1 = []
rest_json1 = []

@route('/all_sambavams')
def crimes():
	pruneDataSet()
	for i in range(0,50):
		scrap(i*10)
	print("=================================================")
	groupByArea([x for x in final1 if x is not None])
	rest_json = constructJson(crime_map)
	print(type(rest_json))
	exportData(rest_json1)
	return rest_json


def constructJson(crime_map):
	index = 1
	for map in crime_map:
		temp = {}
		temp["id"] = index
		temp["name"] = map
		temp["source"] = "verified"
		print(map)
		print(getLatLong(map))
		latLong = getLatLong(map).split(',')
		if len(latLong) > 0:
			temp["lat"] = latLong[0]
			temp["long"] = latLong[1]
		temp["occurences"] = str(crime_map[map])
		rest_json1.append(temp)
		index = index + 1
	return json.dumps(rest_json1) 

def groupByArea(final_crimes):
	for crime in final_crimes:
		if crime in crime_map:
			crime_map[crime] += 1
		else:
			crime_map[crime] = 0

def scrap(index):
	base_url = "https://www.google.co.in/search?q=chennai%20accidents&tbm=nws&start="+str(index)
	web_page = requests.get(base_url)
	parsed_content = PyQuery(web_page.text)
	all_crimes = parsed_content('a')
	for crime in all_crimes:
		crime_url = crime.attrib["href"]
		print(crime_url)
		if '/url?q=' in crime_url:
			try:
				url = (crime_url.split(start))[1].split(end)[0]
				article = Article((crime_url.split(start))[1].split(end)[0])
				print(url)
				article.download()
				article.parse()

				text = article.text
				print("TEXTTT")
				print(text)
				print("TEXTTTEND")
				area_name = findLocation(text)
				final1.append(area_name)
			except Exception:
				pass

def pruneDataSet():
	with open('chennai.csv', 'rt') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',')
		for row in spamreader:
			result.append(row[0].lower())

def findLocation(text):
	for res in result:
		if text.lower().find(res) > 0:
			return res

def getLatLong(area):
	api_key = 'AIzaSyDOjBGZEBvLCpHXkNvl-bBBxKHhzAeSaqU'
	area = area.replace(" ", "%20")
	url = 'https://maps.googleapis.com/maps/api/geocode/json?address='+area+'%20chennai&key='+api_key
	response = json.loads(urllib.urlopen(url).read().decode('utf-8'))
	if len(response["results"]) > 0:
		co_ord=response["results"][0]["geometry"]["location"]
		latLong = str(co_ord["lat"]) + "," + str(co_ord["lng"])
		return latLong

def exportData(rest_json):
	print("*******")
	print(rest_json)
	con = pycps.Connection('tcp://cloud-eu-0.clusterpoint.com:9007', 'YaamirukaBayamen', 'radhikab@thoughtworks.com', 'radhikab', '1201')
	listing = rest_json
	for j in listing:
		print(j)
		con.insert(j)

run(host='localhost', port= 8080, debug=True, reloader=True)