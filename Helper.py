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
import Scheduler
import geopy

logger = logging.getLogger(__name__)


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
    logger.info('getting webpages')
    BlotterURL = "http://ws.ocsd.org/Blotter/BlotterSearch.aspx"

    r = requests.get(BlotterURL)

    if r.status_code != requests.codes.ok:
        sys.exit()

    soup = BeautifulSoup(r.content)

    # ASP validation and session fields
    input_fields = soup.findAll("input", {'type':'hidden'})

    for inputs in input_fields:  # gets the form validation variables the server presents, needed for submitting the form
        if inputs['id'] == '__VIEWSTATE':
            ViewState = inputs['value']

        if inputs['id'] == '__VIEWSTATEGENERATOR':
            ViewStateGen = inputs['value']

        if inputs['id'] == '__EVENTVALIDATION':
            EventValidation = inputs['value']

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
    responses = grequests.map(request)
    logger.info('got a bunch of webpages')
    return responses, cityIndex

def getLocation(textLocation, city):
    textLocation = ('%s %s CA') % (textLocation.replace("//", " and "), city)
    #logger.debug(textLocation)
    g = geocoder.google(textLocation, key='AIzaSyAjPgRQbIeHjaOX7FT8lap0r6M2TRHsZyw')
    if g.json['ok'] == True:
        splitedLat = str.split(str(g.json['lat']), '.')
        joinedLat = '%s.%s' %(splitedLat[0],splitedLat[1][:5])  # truncate the lat to 5 decimal points

        splitedLon = str.split(str(g.json['lng']), '.')
        joinedLon = '%s.%s' %(splitedLon[0],splitedLon[1][:5])  # truncate the long to 5 decimal points
        return joinedLat, joinedLon, g.json['confidence']
    else:
        logger.warning('Unable to geocode incident location: %s' % g.json)
        return 37.8267, -122.4233, 0

def crimeParser(db, response,city):

    logger.info('going through %s' % city)
    getNotes = False
    noteCaseNum = ''
    try:
        soup = BeautifulSoup(response.content)
    except AttributeError as e:
        logger.error(e)
        return
    table = soup.find("table", cellpadding=4)
    rows = table.findAll("tr")

    for row in rows:
        if row.attrs[0] == (u'class', u'trEven') or row.attrs[0] == (u'class', u'trOdd'):
            cells = row.findAll("td")
            IncidentDate = cells[0].getText()
            date_object = datetime.datetime.strptime(IncidentDate, '%m/%d/%Y %I:%M:%S %p')
            trimmeddate = date_object.strftime('%Y-%m-%d %H:%M')
            CaseNum = cells[2].getText()
            Description = cells[3].getText().replace("&nbsp;", "")
            IncidentLocation = cells[4].getText()
            exist = db.query('SELECT CaseNumber FROM Incidents WHERE CaseNumber=:CaseNum', CaseNum=CaseNum, fetchall=True)
            try:
                if exist[0]['CaseNumber'] == CaseNum:
                    logger.debug('the Case number already exists in the database, case: %s, city:%s' %(CaseNum, cityList[city]))
                    if cells[5].getText().replace("&nbsp;", "") == 'read':
                        logger.debug('has notes')
                        getNotes = True
                        noteCaseNum = CaseNum
                    else:
                        logger.debug('does not have notes')
                        getNotes = False
            except:
                getNotes = False
                logger.debug('Found a new incident %s' % CaseNum)
                if 'Arrest Info' in Description:
                    logging.info('subject arrested')
                    arrestparse(db, CaseNum)
                    arrested = 1
                else:
                    arrested = 0
                    logging.info('no arrests')
                lat, lon, confidence = getLocation(IncidentLocation, cityList[city])
                db.query('INSERT INTO Incidents (CaseNumber, Incident, Location, "Date", Lat, Lon, City, CONFIDENCE, Aresst) VALUES (:CaseNum, :Description, :IncidentLocation, :IncidentDate, :lat, :lon, :city, :confidence, :arrested)',
                          CaseNum=CaseNum, Description=Description, IncidentLocation=IncidentLocation, IncidentDate=trimmeddate, lat=lat, lon=lon, city=city, confidence=confidence, arrested=arrested)
                if 'Arrest Info' in Description:
                    arrestparse(db, CaseNum)
        if row.attrs[0] == (u'id', u'trNotes') and getNotes:
            cells = row.findAll("td")
            notes = row.getText()
            logger.debug('scrapped notes say: %s' % notes)
            exist = db.query('SELECT Notes FROM Incidents WHERE CaseNumber=:CaseNum', CaseNum=noteCaseNum, fetchall=True)
            try:
                if exist[0]['Notes'] == notes:
                    logger.debug('notes are up to date')
                    pass
                else:
                    logger.debug('notes out of date')
                    db.query('UPDATE Incidents SET Notes=:note WHERE CaseNumber=:CaseNum', CaseNum=noteCaseNum, note=notes)
            except:
                logger.debug('db has no notes')
                db.query('UPDATE Incidents SET Notes=:note WHERE CaseNumber=:CaseNum', CaseNum=noteCaseNum, note=notes)

def renderMap(datapoints, popups, city, days ):
    map_osm = folium.Map(location=[33.6700, -117.7800], width='75%', height='75%')
    map_osm.add_children(folium.plugins.MarkerCluster(datapoints, popups))
    #map_osm.render()
    map_osm.save('./maps/%sMap%s.html' % (city, days))
    print '%s map complete' % city

def scheduleMap(datapoints, popups, city, days):
    p = multiprocessing.Process(target=renderMap, args=(datapoints, popups, city, days))
    p.start()
    p.join()

def createMap(db, days=0, month=None):
    if days > 0:
        week_ago =  datetime.datetime.now() - datetime.timedelta(days=days)
        week_ago = week_ago.strftime('%Y-%m-%d %H:%M')

    jobs = []
    for city in cityList:
        datapoints = []
        popups = []
        logger.debug('creating %s day map for %s' % (days, city))
        dbIncidents = db.query('SELECT * from Incidents WHERE "Date" > :daterange AND City=:city', daterange=week_ago, city=city)

        for entry in dbIncidents:
            datapoints.append((entry['Lat'], entry['Lon']))

            formatedNotes = str(entry['Notes']).replace('\r','')
            formatedNotes = cgi.escape(formatedNotes)
            html = '''<dl>
                              <dt><b> %s </b></dt>
                               <dd> Case Number: %s </dd>
                               <dd> Description: %s </dd>
                               <dd> Reported Location: %s </dd>
                              <dt>Notes</dt>
                               <dd> %s </dd>
                            </dl>''' % (entry['CaseNumber'], entry['Incident'], entry['Date'], entry['Location'], formatedNotes)

            iframe = folium.element.IFrame(html=html, width=500, height=300)
            popups.append(folium.Popup(iframe, max_width=2650))
            #popups.append(folium.Popup(html=html))
        logger.debug('appending multiprocessing job %s' % city)
        Scheduler.schedule(scheduleMap, args=[datapoints, popups, city, days])


def databaseupdate(db):
    webpages, cityIndex  = getWebpages()
    threads = [gevent.spawn(crimeParser, db, response, city) for response, city in zip(webpages, cityIndex)]
    gevent.joinall(threads)


def tableparse(iterable):
    iterator = iter(iterable)
    prev = None
    item = iterator.next()  # throws StopIteration if empty.
    for next in iterator:
        yield (prev,item,next)
        prev = item
        item = next
    yield (prev,item,None)

def arrestparse(db, casenumber):
    print 'case# %s' %casenumber
    exist = db.query('SELECT CaseNumber FROM Arrests WHERE CaseNumber=:CaseNum', CaseNum=casenumber, fetchall=True)
    try:
        if exist[0]['CaseNumber'] == casenumber:
            return
    except:
        pass

    BlotterURL = "http://ws.ocsd.org/Whoisinjail/search.aspx?FormAction=CallNo&CallNo=%s" % casenumber
    r = requests.get(BlotterURL)

    if r.status_code != requests.codes.ok:
        sys.exit()

    try:
        soup = BeautifulSoup(r.content)
    except AttributeError as e:
        logger.error(e)

    if 'ERROR - This page cannot be displayed at this time.' in soup.getText():
        print 'error on page'
        return

    table = soup.find("table", cellpadding=4)
    rows = table.findAll("tr")
    heading = rows[0].findAll('th')
    for prev, title, next in tableparse(heading):
        if title.getText() == 'Inmate Name:':
            name = " ".join(next.getText().split()).replace(' ,', ',')
            print '%s %s' % (title.getText(), name)

    for row in rows:
        cells = row.findAll("td")
        for prev, cell, next in tableparse(cells):
            #print '%s, \n%s' % (cell.getText(), next)
            if cell.getText() == "Date of Birth:":
                dob = next.getText().replace("&nbsp;", "")
                print '%s %s' % (cell.getText(), next.getText().replace("&nbsp;", ""))
            if cell.getText() == "Sex:":
                sex = next.getText().replace("&nbsp;", "")
                print '%s %s' % (cell.getText(), next.getText().replace("&nbsp;", ""))
            if cell.getText() == "Race:":
                race = next.getText().replace("&nbsp;", "")
                print '%s %s' % (cell.getText(), next.getText().replace("&nbsp;", ""))
            if cell.getText() == "Custody Status:":
                status = next.getText().replace("&nbsp;", "")
                print '%s %s' % (cell.getText(), next.getText().replace("&nbsp;", ""))
            if cell.getText() == "Height:":
                height  = next.getText().replace("&nbsp;", "")
                print '%s %s' % (cell.getText(), next.getText().replace("&nbsp;", ""))
            if cell.getText() == "Bail Amount:":
                bail = next.getText().replace("&nbsp;", "")
                print '%s %s' % (cell.getText(), next.getText().replace("&nbsp;", ""))
            if cell.getText() == "Weight:":
                weight = next.getText().replace("&nbsp;", "")
                print '%s %s' % (cell.getText(), next.getText().replace("&nbsp;", ""))
            if cell.getText() == "Hair Color:":
                hair = next.getText().replace("&nbsp;", "")
                print '%s %s' % (cell.getText(), next.getText().replace("&nbsp;", ""))
            if cell.getText() == "Housing Location:":
                location = next.getText().replace("&nbsp;", "")
                print '%s %s' % (cell.getText(), next.getText().replace("&nbsp;", ""))
            if cell.getText() == "Eye Color:":
                eye = next.getText().replace("&nbsp;", "")
                print '%s %s' % (cell.getText(), next.getText().replace("&nbsp;", ""))
            if cell.getText() == "Occupation:":
                occupation = next.getText().replace("&nbsp;", "")
                print '%s %s' % (cell.getText(), next.getText().replace("&nbsp;", ""))


    sql = '''INSERT INTO Arrests
             (CaseNumber, Name, DOB, Sex,
             Race, Status, Height, Bail,
             Weight, Hair, Location, Eye, Occupation)
             VALUES (:casenum, :name, :dob, :sex,
                     :race, :status, :height, :bail,
                     :weight, :hair, :location, :eye, :occupation)
        '''

    db.query(sql, casenum=casenumber, name=name, dob=dob, sex=sex,
                     race=race, status=status, height=height, bail=bail,
                     weight=weight, hair=hair, location=location, eye=eye, occupation=occupation
             )








