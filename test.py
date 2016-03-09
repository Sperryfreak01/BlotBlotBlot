import requests # https://github.com/kennethreitz/requests
import records # https://github.com/kennethreitz/records
from BeautifulSoup import BeautifulSoup
from folium import plugins, folium
import geocoder

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

def getLocation(textLocation, city):
    #textLocation = textLocation.replace("//", "and")
    textLocation = ('%s %s') % (textLocation.replace("//", " and "), cityList[city])
    g = geocoder.google(textLocation,key='AIzaSyAjPgRQbIeHjaOX7FT8lap0r6M2TRHsZyw')
    try:
        print g.json
        print g.json['lat'], g.json['lng']
        return g.json['lat'], g.json['lng'], g.json['confidence']
    except:
        print g.json
        print 'Unable to geocode incident location'
        return 37.8267, -122.4233, 0


exist = db.query('SELECT * FROM Incidents WHERE Lat=:lat', lat='90')
for places in exist:
    print places['Location'], places['City']
    lat, lon, conf = getLocation(places['Location'], places['City'])
    db.query('UPDATE Incidents SET Lat=:Lat,Lon=:Lon,CONFIDENCE=:conf WHERE CaseNumber=:CaseNum', CaseNum=places['CaseNumber'], Lat=lat, Lon=lon, conf=conf)

exist = db.query('SELECT * FROM Incidents WHERE CONFIDENCE is null')
for places in exist:
    print places['Location'], places['City']
    lat, lon, conf = getLocation(places['Location'], places['City'])
    db.query('UPDATE Incidents SET Lat=:Lat,Lon=:Lon,CONFIDENCE=:conf WHERE CaseNumber=:CaseNum', CaseNum=places['CaseNumber'], Lat=lat, Lon=lon, conf=conf)
