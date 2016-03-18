from gevent import monkey
monkey.patch_all()
import gevent
import requests # https://github.com/kennethreitz/requests
import records # https://github.com/kennethreitz/records
from BeautifulSoup import BeautifulSoup
from folium import plugins, folium
import geocoder
import datetime
import Helper

db = records.Database('sqlite:///blot.db')
BlotterURL = "http://ws.ocsd.org/Blotter/BlotterSearch.aspx"



cityList = {'AV':'ALISO VIEJO', 'AN':'ANAHEIM', 'BR':'BREA', 'BP':'BUENA PARK', 'CN':'ORANGE COUNTY',
            'CS':'ORANGE COUNTY', 'CM':'COSTA MESA', 'CZ':'COTO DE CAZA', 'ON':'ORANGE COUNTY',
            'OS':'ORANGE COUNTY', 'CY':'CYPRESS', 'DP':'DANA POINT', 'DH':'DANA POINT', 'FA':'ORANGE COUNTY',
            'FV':'FOUNTAIN VALLEY', 'FU':'FULLERTON', 'GG':'GARDEN GROVE', 'HB':'HUNTINGTON BEACH', 'IR':'IRVINE',
            'JW':'JOHN WAYNE AIRPORT', 'LR':'LA HABRA', 'LM':'LA MIRADA', 'LP':'LA PALMA', 'LD':'LADERA RANCH',
            'LB':'LAGUNA BEACH', 'LH':'LAGUNA HILLS', 'LN':'LAGUNA NIGUEL', 'LW':'LAGUNA WOODS', 'LF':'LAKE FOREST',
            'FL':'LAS FLORES', 'LA':'LOS ALAMITOS', 'MC':'MIDWAY CITY', 'MV':'MISSION VIEJO', 'NB':'NEWPORT BEACH',
            'NH':'NEWPORT BEACH', 'OR':'ORANGE', 'OC':'ORANGE COUNTY', 'PL':'PLACENTIA',
            'RV':'RANCHO MISSION VIEJO', 'RS':'RANCHO SANTA MARGARITA','RO':'ROSSMOOR', 'SC':'SAN CLEMENTE',
            'SJ':'SAN JUAN CAPISTRANO', 'SA':'SANTA ANA', 'SB':'SEAL BEACH', 'SI':'SILVERADO CANYON', 'ST':'STANTON',
            'SN':'SUNSET BEACH', 'TC':'TRABUCO CANYON', 'TU':'TUSTIN', 'VP':'VILLA PARK', 'WE':'WESTMINSTER',
            'YL':'YORBA LINDA'}

for city in cityList:
    #print Helper.getLocation('', cityList[city])
    cityLocation = {}
    #cityLocation[city] = Helper.getLocation('', city)
#print cityLocation




week_ago =  datetime.datetime.now() - datetime.timedelta(days=7)
week_ago = week_ago.strftime('%Y-%m-%d %H:%M')
print week_ago

dbentry = db.query('SELECT CaseNumber, Location, City from Incidents WHERE CONFIDENCE<:long', long=2)

for entry in dbentry:
    print entry['CaseNumber']
    lat, lon, conf = Helper.getLocation(entry['Location'], Helper.cityList[entry['City']])
    db.query('UPDATE Incidents SET Lat=:prunedlat, Lon=:prunedlon, CONFIDENCE=:conf WHERE CaseNumber=:CaseNum', CaseNum=entry['CaseNumber'], prunedlat=lat,  prunedlon=lon, conf=conf)



