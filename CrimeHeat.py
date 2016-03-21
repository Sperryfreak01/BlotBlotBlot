import gevent
import geocoder
import requests  # https://github.com/kennethreitz/requests
import grequests
from BeautifulSoup import BeautifulSoup
import datetime
import folium
import folium.plugins
import folium.element
import cgi
import logging
import multiprocessing
from multiprocessing import pool
import Scheduler
import geopy
import records

logger = logging.getLogger(__name__)
#mappool = multiprocessing.Pool(processes=multiprocessing.cpu_count())              # start 4 worker processes


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

def renderMap(datapoints, popups, markers, city, days):  #TODO center map on city and fix zoom
    #folium_figure = m.get_root()
    #folium_figure.header._children['bootstrap'] = folium.element.JavascriptLink('{{another url of your choice}}')
    map_osm = folium.Map(location=[33.6700, -117.7800], width='75%', height='75%')

    map_osm.add_children(folium.plugins.HeatMap(datapoints))
    map_osm.save('./maps/%sMap%s.html' % (city, days))
    logger.debug('%s map complete' % city)


def scheduleMap(datapoints, popups, markers, city, days):
    #mappool.apply_async(target=renderMap, args=(datapoints, popups, markers, city, days))
    p = multiprocessing.Process(target=renderMap, args=(datapoints, popups, markers, city, days))
    p.start()
    p.join(0)


def createheatmap(db, days=0, month=None):
    if days > 0:
        mapstartdate =  datetime.datetime.now() - datetime.timedelta(days=days)
        mapstartdate = mapstartdate.strftime('%Y-%m-%d %H:%M')

    for city in cityList:
        datapoints = []
        popups = []
        markers = []

        calldatapoints = []
        callpopups = []
        callmarkers = []

        arrestdatapoints = []
        arrestpopups = []
        arrestmarkers = []

        logger.debug('creating %s day map for %s' % (days, city))

        #  Get all of the incidents and arrests since teh specified date
        dbIncidents = db.query('SELECT * from Incidents WHERE "Date" > :daterange', daterange=mapstartdate)


        for entry in dbIncidents:
            datapoints.append((entry['Lat'], entry['Lon']))


        logger.debug('appending multiprocessing job %s' % city)
        jobname = ('heat %sday' % (days))
        #Scheduler.schedule(scheduleMap, name=jobname, args=[datapoints, popups, markers, city, days])

        renderMap(datapoints, None, None, 'HEAT', days)
db = records.Database('sqlite:///blot.db')
createheatmap(db,days=3)