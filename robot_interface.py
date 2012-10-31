# -*- coding: utf-8 -*-
#!/usr/bin/python2.6
# robot_interface.py
"""
    Dieses Modul läuft als Thread im Hintergrund
    es ist zuständig für die Kommunikation mit dem Roboter. Aufgaben werden über 
    die jobquue entgegengenommen.
    
    
    
    21.10.2011 - Grundgerüst erstellt  
    23.10.2011 - Methode zum Schlitten verfahren hinzugefügt
               - Attribute zum Interface hinzugefügt die den momentanen Zustand
                 des Roboters anzeigen
               - Interface sucht nach passendem seriellem Device selbstständig 
                 serial_device_type = ttyUSB -> bringt das erste brauchbare ttyUSB Gerät
               - abgebrochene serielle Verbindungen werden selbständig wieder hergestellt
                 der Thread wird nicht mehr abgebrochen 
    18.11.2011 - Methoden Hinzugefügt:
                  -do_pourer: einen Ausschenker verwenden
                  -do_order : eine Bestellung abwickeln
                 
                 
    TODO:   - später mal verschiedene Getränkevariationen handeln, und das ganze über eine Datenbank
              regeln...      
            - Stabilität prüfen
            - eine extra Klasse vorhalten mit einem Standardrezept? (alle anteile auf 0) 
              damit können keine undefinierten Zustände entstehen
            
"""
import threading
import Queue
import time
import os

import uart_interface
from debug import debug

    #mögliche Jobs für das Interface
jobs = {1:  'send_string',
        2:  'read_skid_pos',
        3:  'skid_goto',
        4:  'do_order',
        5:  'do_pourer',
        6:  'skid_start_pos',
        99: 'delay'}

            #Positionen für Die Ausschenker
POURER_POS = {1: 620,
              2: 463}
POS_START = 300
            
            #Ausschenker Adressierungen
POURER_CONTENT = {'whisky': 'purer1',
                  'cola': 'pourer2'}
          

class RobotInterface(threading.Thread):
    """
        Thread der die Kommunikation mit dem Roboter handhabt, und Aufträge aus der
        Auftragsliste entgegennimmt
        
    """
    def __init__(self, jobqueue, serial_device_type, baud):
        """
            :param jobqueue: objekt vom Typ Queue.Queue für die Kommunikation zwischen den Threads
            :param serial_device_type: String der Bezeichner der Seriellen Verbindung in
                                       /dev/ angibt (z.Bsp: ttyusb)
            :param baud: Baudrate für die Verbindung über serial_device_type
            
        """
        threading.Thread.__init__(self)
        self.stop_thread = False
        self.serial_device_type = serial_device_type
        self.queue = jobqueue
        self.port = False
        self.baud = baud
        self.uart = False
        self.skid_pos = 0
        self.busy = False
        self.jobdiscr = 'kein Auftrag'
        self.init_uart_conn()
        debug('Roboterinterface initiiert', 0)
    
    def find_serial_device(self, count=0):
        """
            im Verzeichnis /dev nach angemeldeten Geräten suchen.
            :param device: string der gesuchtes Gerät identifiziert (bsp ttyusb)
            :param count: der wievielte eintrag soll zurückgegebenn werden? 
        """
        search_path = os.path.join('/', 'dev')
        devices = list()
        for elem in os.listdir(search_path):
            if elem.lower().startswith(self.serial_device_type.lower()):
                devices.append(elem)
        try:
            self.port = os.path.join('/', 'dev', devices[0])  
            debug('new device: '+ self.port, count)
            return True
        except IndexError:
            debug('kein ' + self.serial_device_type + ' gefunden', 1)
            self.port = False
    
    def init_uart_conn(self):
        if self.find_serial_device():
            self.uart = uart_interface.connection(self.port, self.baud)
            return
        time.sleep(3)
            
    def connect(self):
        """
            verbinden über uart Interface mit uc
        """
        while self.uart == False:
            self.init_uart_conn()

        debug('connecting', 0)
        counter = 0
        while True:
            if self.uart.connect():
               return True
            counter += 1
            time.sleep(2)
            if counter == 2:
                break
            
        debug('serielle Verbindung verloren - versuche neue Verbindung', 1)
        self.uart = False
        self.init_uart_conn()
        self.connect()       
        
    def disconnect(self):
        """
            uart Verbindung mit uc trennen
        """
        self.uart.close()
        debug('disconnected', 0)
    
    def send_string(self, string):
        """
            string an uc senden
        """
        self.busy = True
        debug('sende string: ' + string , 0)
        self.connect()
        self.uart.echo_string(string)
        self.disconnect()
        self.busy = False
        
    def delay(self, dur):
        """
            uc pausieren lassen für dur ms
            auch der Thread wird für die Dauer des delay blockiert
        """
        self.busy = True
        self.jobdiscr = 'delay (entwicklungsspielerei)'
        debug('uc pausieren lassen für' + str(dur), 0)
        self.connect()
        self.uart.delay(dur)
        temp = ""
        while temp <> "[ready]":
            temp = self.uart.read_line()    
            debug('waiting...', 0)
        self.disconnect()
        self.busy = False
    
    def read_skid_pos(self, params=False):
        """
            aktuelle Position des Schlittens abfragen und speichern
        """
        self.busy = True
        self.jobdiscr = 'Schlittenposition ermitteln'
        debug('Schlittenposition abfragen', 0)
        self.connect()
        temp = False
        try:
            temp = self.uart.get_skid_pos()
            self.skid_pos = int(temp)
            temp =  'ermittelt:', self.skid_pos
            debug(temp, 0)
        except ValueError:
            debug('ungültige Daten empfangen', 1)
        except TypeError:
            debug('ungültige Daten empfangen', 1)
        
        self.disconnect()
        self.busy = False
        debug('pos: ' + str(self.skid_pos), 0)
        
    def skid_goto(self, value):
        self.busy = True
        self.jobdiscr = 'neue Position anfahren'
        self.connect()
        debug('sende neue Schlittenposition', 0)
        self.uart.skid_goto(value)
        temp = ""
        while temp <> "[skid_ready]":
            temp = self.uart.read_line()
            if temp <> "[skid_ready]":
                debug(str(temp), 0)
                self.skid_pos = int(temp)
        self.skid_pos = value
        self.disconnect()
        self.busy = False
    
    def skid_start_pos(self, dummy):
        """
            Schlitten in Starposition fahren
            variable dummy ist egal - wird für den automatismus benötigt 
            Methoden dieser Klass über ein dict anzusprechen
        """
        self.busy = True
        self.connect()
        debug('fahre Startposition an')
        self.skid_goto(POS_START)
        self.disconnect()
        self.busy = False
        
    def do_pourer(self, pourer, delay=50):
        """
            einen Dosierer Betätigen
            übergeben werden Dosierer sowie Verzögerungszeit (Wartezeit in ms)
        """
        self.busy = True
        self.jobdiscr = 'Dosierer ' + str(pourer) + ' betätigen'
        self.connect()
        debug('betätige Dosierer', 0)
        debug(str(delay))
        
            #TODO: zu verwendende Methode entweder aus Dict suchen, oder aber die Methode direkt übergeben 
        if pourer == 'pourer_1':
            self.uart.pourer_1(delay)
        if pourer == 'pourer_2':
            self.uart.pourer_2(delay)
            
            #TODO: warten bis Roboter sich wieder meldet. Vorerst wird nur gewartet bis er wieder erreichbar
            #      sein sollte.
        time.sleep((delay+50)/100.0)
        self.disconnect()
        self.busy = False
        
        
    def do_order(self, recipe):
        """
            ein Rezept abarbeiten. Ein rezept wird als Dict übergeben. Enthalten sein sollten folgende Key-Value Paare
            revipe = {name: 
                      whisky:
                      cola}
        """
        self.busy = True
        self.jobdiscr = recipe['name']
        
        if recipe['whisky'] > 0:
            self.skid_goto(POURER_POS[1])
            for elem in xrange(0, recipe['whisky']):
                self.do_pourer('pourer_1', 600)
                time.sleep(1)
        
        if recipe['cola'] > 0:
            self.skid_goto(POURER_POS[2])
            self.skid_goto(POURER_POS[2])
            for elem in xrange(0, recipe['cola']):
                self.do_pourer('pourer_2', 600)
                time.sleep(1)
                
        self.skid_goto(POS_START)
        self.busy = False
    
    def run(self):
        """
            Arbeitsschleife des Worker Threads...
            warten auf jobs aus der jobqueue und abarbeiten
        """
        debug('Roboterinterface gestartet', 0)
        while not self.stop_thread:
            debug('suche job ', 0)
            self.jobdiscr = 'idle'
            try:
                job_id, val = self.queue.get(timeout = 1)
                jobstr = 'job: ', str(job_id), '-', str(val)
                debug(jobstr, 0)
                
                if hasattr(self, jobs.get(job_id)):
                    getattr(self, jobs.get(job_id))(val)
                
            except Queue.Empty:
                    # wenn auftragsliste leer - Schlittenposition abfragen
                self.read_skid_pos()
            except ValueError:
                debug('ungültiger Job empfangen', 5)
            
            time.sleep(4)
        
        
        