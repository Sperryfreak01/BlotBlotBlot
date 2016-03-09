import requests # https://github.com/kennethreitz/requests
import grequests
import records # https://github.com/kennethreitz/records
from BeautifulSoup import BeautifulSoup
import folium
import folium.plugins
import folium.element
import Helper
import cgi

db = records.Database('sqlite:///blot.db')
GoogleAd = ''

webpages, cityIndex  = Helper.getWebpages()
getNotes = False
noteCaseNum = ''
#with open('output.html', 'wb') as handle:
#for city in Helper.cityList:
for response,city in zip(webpages, cityIndex):
    #response = requests.request("POST", BlotterURL, data=payload, headers=headers)
    #handle.write(response.content)

    soup = BeautifulSoup(response.content)

    #table_even = Soup.findAll("tr", {'class': 'trEven'})
    table = soup.find("table", cellpadding=4)
    #print table
    #body = table.find("tbody")
    #print body
    rows = table.findAll("tr")
    #print rows
    for row in rows:
        if row.attrs[0] == (u'class', u'trEven') or row.attrs[0] == (u'class', u'trOdd'):
            #print row.attrs
            cells = row.findAll("td")
            CaseNum = cells[2].getText()
            IncidentDate = cells[0].getText()
            Description = cells[3].getText().replace("&nbsp;", "")
            #Description = Description.replace("&nbsp;", "")
            IncidentLocation = cells[4].getText()
            exist = db.query('SELECT CaseNumber FROM Incidents WHERE CaseNumber=:CaseNum', CaseNum=CaseNum, fetchall=True)
            try:
                if exist[0]['CaseNumber'] == CaseNum:
                    #print 'the Case number already exists in the database, case: %s, city:%s' %(CaseNum, Helper.cityList[city])
                    if cells[5].getText().replace("&nbsp;", "") == 'read':
                        #print 'has notes'
                        getNotes = True
                        noteCaseNum = CaseNum
                    else:
                        #print 'does not have notes'
                        getNotes = False
            except:
                getNotes = False
                #print 'Found a new incident %s' % CaseNum
                lat, lon, confidence = Helper.getLocation(IncidentLocation, Helper.cityList[city])
                db.query('INSERT INTO Incidents (CaseNumber, Incident, Location, "Date", Lat, Lon, City, CONFIDENCE) VALUES (:CaseNum, :Description, :IncidentLocation, :IncidentDate, :lat, :lon, :city, :confidence)',
                         CaseNum=CaseNum, Description=Description, IncidentLocation=IncidentLocation, IncidentDate=IncidentDate, lat=lat, lon=lon, city=city, confidence=confidence)

        if row.attrs[0] == (u'id', u'trNotes') and getNotes:
            cells = row.findAll("td")
            notes = row.getText()
            #print 'scrapped notes say: %s' % notes
            exist = db.query('SELECT Notes FROM Incidents WHERE CaseNumber=:CaseNum', CaseNum=noteCaseNum, fetchall=True)
            try:
                if exist[0]['Notes'] == notes:
                    #print 'notes are up to date'
                    pass
                else:
                    #print 'notes out of date'
                    db.query('UPDATE Incidents SET Notes=:note WHERE CaseNumber=:CaseNum', CaseNum=noteCaseNum, note=notes)
            except:
                #print 'db has no notes'
                db.query('UPDATE Incidents SET Notes=:note WHERE CaseNumber=:CaseNum', CaseNum=noteCaseNum, note=notes)

def createMap(city):


    #dbentry = db.query('SELECT * from Incidents')
    #    for entry in dbentry
    date_object = datetime.datetime.strptime(entry['Date'], '%m/%d/%Y %I:%M:%S %p')
    week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    if date_object >= week_ago:
    print 'true'
    print date_object
    print week_ago

    datapoints = []
    popups = []
    map_osm = folium.Map(location=[33.6700, -117.7800], width='75%', height='75%')
    dbIncidents = db.query('SELECT * FROM Incidents WHERE City=:Place', Place=city)
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

    map_osm.add_children(folium.plugins.MarkerCluster(datapoints, popups))
    #map_osm.render()
    map_osm.save('./maps/%smap.html' % city)
    print '%s map complete' % city


