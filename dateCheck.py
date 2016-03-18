import requests # https://github.com/kennethreitz/requests
import records # https://github.com/kennethreitz/records
from BeautifulSoup import BeautifulSoup
from folium import plugins, folium
import geocoder
import datetime


db = records.Database('sqlite:///blot.db')
BlotterURL = "http://ws.ocsd.org/Blotter/BlotterSearch.aspx"

week_ago =  datetime.datetime.now() - datetime.timedelta(days=7)
week_ago = week_ago.strftime('%Y-%m-%d %H:%M')
print week_ago

dbentry = db.query('SELECT CaseNumber, "Date" from Incidents WHERE "Date" > :daterange', daterange=week_ago)

for entry in dbentry:
    print ('case:%s date:%s' % (entry['CaseNumber'],entry['Date']))
