import requests # https://github.com/kennethreitz/requests
import records # https://github.com/kennethreitz/records
from BeautifulSoup import BeautifulSoup
from folium import plugins, folium
import geocoder
import datetime


db = records.Database('sqlite:///blot.db')
BlotterURL = "http://ws.ocsd.org/Blotter/BlotterSearch.aspx"

#dbentry = db.query('SELECT * from Incidents')
#    for entry in dbentry
date_object = datetime.datetime.strptime('3/6/2016 5:15:53 PM', '%m/%d/%Y %I:%M:%S %p')
week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
if date_object >= week_ago:
    print 'true'
    print date_object
    print week_ago
