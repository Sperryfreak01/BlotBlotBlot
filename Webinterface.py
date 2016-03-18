__author__ = 'matt'

import bottle
import logging


logger = logging.getLogger(__name__)
WebApp = bottle.Bottle()


@WebApp.error(404)
def error404(error):
    return "shit"

@WebApp.route('/')
@bottle.view('index')
def index():
    return bottle.template('Home', users= users)

@WebApp.route('/static/:path#.+#', name='static')
def static(path):
    print path
    return bottle.static_file(path, root='static')

@WebApp.get('/favicon.ico')
def get_favicon():
    return bottle.static_file('favicon.ico', root='./static/')
