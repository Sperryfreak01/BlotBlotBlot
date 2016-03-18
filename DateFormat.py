import requests # https://github.com/kennethreitz/requests
import records # https://github.com/kennethreitz/records
from BeautifulSoup import BeautifulSoup
from folium import plugins, folium
import geocoder
import datetime


db = records.Database('sqlite:///blot.db')
BlotterURL = "http://ws.ocsd.org/Blotter/BlotterSearch.aspx"

dbentry = db.query('SELECT CaseNumber, "Date" from Incidents')
for entry in dbentry:
    try:
        date_object = datetime.datetime.strptime(entry['Date'], '%m/%d/%Y %I:%M:%S %p')
        trimmeddate = date_object.strftime('%Y-%m-%d %H:%M')
        db.query('UPDATE Incidents SET "Date"=:trimmeddate WHERE CaseNumber=:CaseNum', CaseNum=entry['CaseNumber'], trimmeddate=trimmeddate)
    except ValueError as e:
        print e


