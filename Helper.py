import geocoder
import requests  # https://github.com/kennethreitz/requests
import grequests
from BeautifulSoup import BeautifulSoup

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

def getWebpages():
    BlotterURL = "http://ws.ocsd.org/Blotter/BlotterSearch.aspx"

    #session = requests.Session()
    #r = requests.get(BlotterURL)
    r = requests.get(BlotterURL)

    if r.status_code != requests.codes.ok:
        sys.exit()

    soup = BeautifulSoup(r.content)

    # ASP validation and session fields
    input_fields = soup.findAll("input", {'type':'hidden'})

    for inputs in input_fields:
        if inputs['id'] == '__VIEWSTATE':
            ViewState = inputs['value']
            #print ViewState
        if inputs['id'] == '__VIEWSTATEGENERATOR':
            ViewStateGen = inputs['value']
            #print ViewStateGen
        if inputs['id'] == '__EVENTVALIDATION':
            EventValidation = inputs['value']
            #print EventValidation
    headers = {
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        'origin': "http//ws.ocsd.org",
        'x-devtools-emulate-network-conditions-client-id': "3D54FA71-2ADC-4CB2-8140-B266EC5E9596",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded",
        'dnt': "1",
        'referer': "http//ws.ocsd.org/Blotter/BlotterSearch.aspx",
        'accept-encoding': "gzip, deflate",
        'accept-language': "en-US,en;q=0.8",
        'cookie': "ASP.NET_SessionId=a0ooc555m13vlofbtiljc055",
        'cache-control': "no-cache",
        }
    cityIndex = []
    payloads = []
    for city in cityList:
        payloads.append({'SortBy': '',
                           '__EVENTARGUMENT': '',
                           '__EVENTTARGET': '',
                           '__EVENTVALIDATION': EventValidation,
                           '__SCROLLPOSITIONX': '0',
                           '__SCROLLPOSITIONY': '0',
                           '__VIEWSTATE': ViewState,
                           '__VIEWSTATEGENERATOR': ViewStateGen,
                           'btn7Days.x': '15',
                           'btn7Days.y': '8',
                           'ddlCity': city
                        })
        cityIndex.append(city)

        request = (grequests.request("POST", BlotterURL, data=payload, headers=headers) for payload  in payloads)
    responses =grequests.map(request)
    print 'got a bunch of webpages'
    return responses, cityIndex




def getLocation(textLocation, city):
    #textLocation = textLocation.replace("//", "and")
    textLocation = ('%s %s CA') % (textLocation.replace("//", " and "), city)
    #print textLocation
    g = geocoder.google(textLocation, key='AIzaSyAjPgRQbIeHjaOX7FT8lap0r6M2TRHsZyw')
    try:
        #print g.json
        #print g.json['lat'], g.json['lng']
        return g.json['lat'], g.json['lng'], g.json['confidence']
    except:
        #print g.json
        print 'Unable to geocode incident location'
        return 37.8267, -122.4233, 0