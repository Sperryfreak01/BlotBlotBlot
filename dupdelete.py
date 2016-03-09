import requests # https://github.com/kennethreitz/requests
import records # https://github.com/kennethreitz/records
from BeautifulSoup import BeautifulSoup
from folium import plugins, folium
import geocoder

db = records.Database('sqlite:///blot.db')
BlotterURL = "http://ws.ocsd.org/Blotter/BlotterSearch.aspx"

db.query('delete from Incidents where rowid not in (select max(rowid) from Incidents group by CaseNumber)')


