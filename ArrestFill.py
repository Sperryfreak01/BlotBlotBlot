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

session = requests.Session()
r = session.get(BlotterURL)

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
    'postman-token': "db78fe47-9410-5c06-11b9-759d6524136a"
    }
getNotes = False
noteCaseNum = ''
#with open('output.html', 'wb') as handle:
for city in cityList:
    payload = {'SortBy': '',
           '__EVENTARGUMENT': '',
           '__EVENTTARGET': '',
           '__EVENTVALIDATION': EventValidation,
           '__SCROLLPOSITIONX': '0',
           '__SCROLLPOSITIONY': '0',
           '__VIEWSTATE': ViewState,
           '__VIEWSTATEGENERATOR': ViewStateGen,
           'btn7Days.x': '15',
           'btn7Days.y': '8',
           'ddlCity': city}


    response = requests.request("POST", BlotterURL, data=payload, headers=headers)
    soup = BeautifulSoup(response.content)

    table = soup.find("table", cellpadding=4)
    rows = table.findAll("tr")

    for row in rows:
        if row.attrs[0] == (u'class', u'trEven') or row.attrs[0] == (u'class', u'trOdd'):
            cells = row.findAll("td")
            CaseNum = cells[2].getText()
            exist = db.query('SELECT CaseNumber FROM Incidents WHERE CaseNumber=:CaseNum', CaseNum=CaseNum, fetchall=True)
            try:
                if exist[0]['CaseNumber'] == CaseNum:
                    print 'the Case number already exists in the database, case: %s, city:%s' %(CaseNum, cityList[city])
                    if cells[5].getText().replace("&nbsp;", "") == 'read':
                        print 'has notes'
                        getNotes = True
                        noteCaseNum = CaseNum
                    else:
                        print 'does not have notes'
                        getNotes = False

            except:
                getNotes = False
                print 'incident is new, not adding thats a differnt script'
        if row.attrs[0] == (u'id', u'trNotes') and getNotes:
            cells = row.findAll("td")
            print 'notes say: %s' % row.getText()
            notes = row.getText()
            db.query('UPDATE Incidents SET Notes=:note WHERE CaseNumber=:CaseNum', CaseNum=noteCaseNum, note=notes)


