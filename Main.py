__author__ = 'matt'
#!/usr/bin/python
# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all()
import records # https://github.com/kennethreitz/records
import Helper
import time
import Scheduler
import bottle
import Webinterface
from Scheduler import schedule, KillScheduler
import logging
import atexit

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logging.info('Starting BLOTblotBLOT')

def endprog():
    KillScheduler()
    logging.info('HOMEr service stopping')
    bottleApp.close()

db = records.Database('sqlite:///blot.db')
start = time.time()


if __name__ == '__main__':
    atexit.register(endprog)
    bottleApp = bottle.default_app()
    bottleApp.merge(Webinterface.WebApp)
    Scheduler.schedule(Helper.databaseupdate, args=[db])
    Scheduler.schedule(Helper.createMap, args=[db, 1])
    Scheduler.schedule(Helper.databaseupdate, args=[db], id='updater', trigger='interval', minutes=5)
    Scheduler.schedule(Helper.createMap, args=[db, 1], id='map1', trigger='interval', minutes=15)
    Scheduler.schedule(Helper.createMap, args=[db, 7], id='map7', trigger='interval', minutes=30)
    #Scheduler.schedule(Helper.createMap, args=[db, 14], id='map14', trigger='interval', minutes=60)
    #Scheduler.schedule(Helper.createMap, args=[db, 30], id='map30', trigger='interval', minutes=120)



    ########################################################################
    bottleApp.run(host='0.0.0.0', port=8081, debug=True, server='gevent')

