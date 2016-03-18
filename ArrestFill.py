import requests # https://github.com/kennethreitz/requests
import records # https://github.com/kennethreitz/records
from BeautifulSoup import BeautifulSoup
from folium import plugins, folium
import geocoder
import datetime
import  logging


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
    logger = logging.getLogger(__name__)


    r = requests.get(BlotterURL)

    if r.status_code != requests.codes.ok:
        sys.exit()

    getNotes = False
    noteCaseNum = ''
    try:
        soup = BeautifulSoup(r.content)
    except AttributeError as e:
        logger.error(e)
    if 'ERROR - This page cannot be displayed at this time.' in soup.getText():
        print 'error on page'
        sql = '''INSERT INTO Arrests
             (CaseNumber, Name, DOB, Sex,
             Race, Status, Height, Bail,
             Weight, Hair, Location, Eye, Occupation)
             VALUES (:casenum, :name, :dob, :sex,
                     :race, :status, :height, :bail,
                     :weight, :hair, :location, :eye, :occupation)
        '''

        db.query(sql, casenum=casenumber, name='NULL', dob='NULL', sex='NULL',
                         race='NULL', status='NULL', height='NULL', bail='NULL',
                         weight='NULL', hair='NULL', location='NULL', eye='NULL', occupation='NULL'
                 )
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






db = records.Database('sqlite:///blot.db')
i=0
#entries = db.query('SELECT CaseNumber,Incident FROM Incidents WHERE Incident LIKE :arrestinfo', arrestinfo='%Arrest Info')
#entries = db.query('SELECT CaseNumber from Incidents WHERE Aresst=:arrest', arrest=1)
entries = db.query('''SELECT Incidents.CaseNumber
                        FROM Incidents
                        LEFT JOIN Arrests ON Arrests.CaseNumber = Incidents.CaseNumber
                        WHERE Arrests.CaseNumber IS NULL AND Incidents.Aresst = 1''')

for entry in entries:
    #splitstring = str.split(str(entry['Incident']), 'Arrest Info')
    #print splitstring[0]
    #db.query('UPDATE Incidents SET Incident=:incident, Aresst=:arrested WHERE CaseNumber=:CaseNum', CaseNum=entry['CaseNumber'], incident=splitstring[0], arrested=1)

    arrestparse(db,entry['CaseNumber'])



