# -*- coding: utf-8 -*-
#!/usr/bin/python2.6
# main.py
"""
    Projekt für eine erste Webfrontend- Version für CoWhi.

    Zugriff auf alle wichtigen Funktionen des CoWhi über ein Webfrontend.
    Die Kommunikation des Webfrontend mit dem Mikrocontroller erfolgt über das Modul
    uart_interface.py 
    
    Als python-HTML- Framework wird bottle verwendet.
    Das Webfrontend sollte möglichst auch von mobilenn Clients verwendet werden können. 
    Dafür muss zuerst ein brauchbares Framework gefunden werden. - wir versuchen es mit sencha touch
    
    TODO:
     [done] - Minimalistisches Beispiel mit Hilfe von Bottle erstellen.
     [done] - Configuration über Configdatei (main.ini)
     [done] - Statische Verzeichnisse für JavaScript und css einbinden
     [done] - templatesystem jinja2 einbinden
     [done] - erweitern des Beispiels um erste Kommunikation mit Handling der Verbindung
     [done] - erweitern um ein Framework um ein hübsches Frontend zu erhalten. 
     [done] - Interaktion mit Roboter über serperaten Thread abhandeln (direktes feedback bei Webinterface erhalten)
     [done] - Kommunikation von interface und Roboterthread
     [done] - automatisch ermitteln wie der Adapter heisst (/dev/ttyUSBx)
            - debugging ohne das uart_interface möglich machen...
                - wie soll sich ein dummy interface verhalten?
                    a: alle Aufträge einfach quittieren
                    b: Aufträge simulieren
            - ist jinja2 überflüssig? kann das alles über JavaScript erledigt werden?
     
    
"""
import ConfigParser
import os
import Queue

from bottle import route, post, run,  debug,  response,  request, CheetahTemplate as template
from bottle import TEMPLATE_PATH as TEMPLATE_PATH,  send_file,  PasteServer
from jinja2 import Environment, evalcontextfilter, PackageLoader, BaseLoader, Markup, escape

import robot_interface
from debug import debug

_version__ = '0.2'

INI_FILENAME = 'main.ini'
APPDIR = os.path.dirname(os.path.abspath(__file__))

#Konfiguration einlesen
config = ConfigParser.ConfigParser()
config.read(INI_FILENAME)

    #TODO: verwenden der Parameter aus main.ini
TEMPLATE_DIR = os.path.join(APPDIR, config.get('bottle',  'template_dir'))
IMAGE_DIR = os.path.join(APPDIR, config.get('bottle',  'image_dir'))
CSS_DIR = os.path.join(APPDIR, config.get('bottle',  'css_dir'))
JAVASCRIPT_DIR = os.path.join(APPDIR, config.get('bottle',  'javascript_dir'))

    #nur lokalen Server Starten, oder auch externe Anfragen bedienen?
    #lokaler Server auf Port 8080
    # ansonsten auf Port 80
LOCAL = False
    #Debuggen für Entwicklung?
DEVELOPMENT = True


    #Konfiguration von Jina2 inclusive Filter und Syntax für Variablen
class MyLoader(BaseLoader):

    def __init__(self, path):
        self.path = path

    def get_source(self, environment, template):
        path = os.path.join(self.path, template)
        if not os.path.exists(path):
            raise TemplateNotFound(template)
        mtime = os.path.getmtime(path)
        with file(path) as f:
            source = f.read().decode('utf-8')
        return source, path, lambda: mtime == os.path.getmtime(path)
    
@evalcontextfilter
def nl2br(eval_ctx, value):
    temp = list()
    for elem in escape(value).split('\n'):
        temp.append(unicode(elem))
    return Markup('<br/>'.join(temp))

    # environment für Jinja anlegen
env = Environment(line_statement_prefix="#",
                  variable_start_string="${",
                  variable_end_string="}",
                  autoescape = True,
                  loader=MyLoader(TEMPLATE_DIR))

env.filters['nl2br'] = nl2br


"""
    Statische Verzeichnisse definieren
"""
@route('/css/:filename#.*#')
def static_css(filename):
    """
        ausliefern von statischen Dateien - css- Dateien
    """
    send_file(filename, root=CSS_DIR)

@route('/image/:filename#.*#')
def static_img(filename):
    """
        ausliefern von statischen Dateien - Bilder
    """
    send_file(filename,  root=IMAGE_DIR)

@route('/javascript/:filename#.*#')
def static_javascript(filename):
    """
        ausliefern von statischen Dateien - Javasript
    """
    send_file(filename,  root=JAVASCRIPT_DIR)
    
"""
    dynamische Seiten
"""    

@route('/sencha')
def sencha_main():
    response.content_type = 'text/html; charset=utf8'
    template = env.get_template('index2.tpl')
    return template.render()

@route('/ajax/get_state')
def get_state():
    """
        Anzahl der ausstehenden Jobs und zusätzliche 
        Informationen vom robbi als json senden 
    """
    response.content_type = 'text/html; charset=utf8'
    json = dict()
    json ['numberJobs'] = 1
    if q.qsize() == 1:
        json ['jobString'] = '' + str(1) + ' Auftrag in der Jobliste'
    else:
        json ['jobString'] = '' + str(q.qsize()) + ' Aufträge in der Jobliste'
    json ['activeJob'] = robbi.jobdiscr
    json ['skidPos'] = robbi.skid_pos
    return json

@post('/ajax/set_skid')
def set_skid():
    """
        direktes Anfahren einer neuen Schlittenposition
    """
    debug('setzte neue Schlittenposition: ' + str(request.POST['newPos']), 0)
    q.put((3, int(request.POST['newPos'])))
    return 'skid pos set'

@route('/ajax/set_start_pos')
def set_start_pos():
    """
        den Schlitten in Startposition fahren
    """
    response.content_type = 'text/html; charset=utf8'
    q.put((6, 'dummy'))
    return 'setting position'

@post('/ajax/set_order')
def set_order():
    """
        eine Bestellung entgegennehmen
    """
    debug('empfange bestellung', 0)
    recipe = {}
    recipe['name'] = request.POST['name']
    recipe['whisky'] = int(request.POST['whisky']) 
    recipe['cola'] = int(request.POST['cola'])
    for elem in recipe:
        debug( elem + ':' + str(recipe[elem]), 0)
    q.put((4, recipe))
    return 'order set'
    


def main():
    """
        TDOD die globalen q und robbi evtl mal loswerden?
             --> alternative überlegen
    """
    global q 
    global robbi
    q = Queue.Queue()
    robbi = robot_interface.RobotInterface(q, 'ttyUSB', 9600)
    robbi.start()  

    if LOCAL:
        if DEVELOPMENT:
            debug.DEBUG = True
        else:
            debug.DEBUG = False
        run(reloader=False,  server=PasteServer,  port=8080)
    if LOCAL == False:
        if DEVELOPMENT:
            debug.DEBUG = True
        else:
            debug.DEBUG = False
        run(reloader=False,  host='0.0.0.0',  server=PasteServer,  port=80)  
        
        #Thread für RoboterInterface töten
    robbi.stop_thread = True
    
    
if __name__ == "__main__":
    main()