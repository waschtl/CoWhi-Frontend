#!/usr/bin/python
# -*- coding: utf-8 -*-
#uart_interface.py

"""
    kommunikation über den seriellen Port (UART) mit dem Coctailrobboter. 
    
    23.10.2011 - löschen unnötiger Methoden
                 löschen überflüssiger Print- statements
    TODO:    -- Programmteil über Konsole sauber beenden lassen?
                    - scheint sich nur aufzuhängen wenn ein Auftrag noch nicht
                      beendet ist, evtl Aufträge nicht ewig gültig sein lassen?

            - echo_string wieder einführen?
"""

import serial

from debug import debug

    # timeout beim empfangen von Daten
SERIAL_TIMEOUT = 1
LINE_END = "\n"

#Labels für das Protokoll
    #abgehende Labels
LABEL_ECHO = "[echo]"
LABEL_ECHO_STRING = "[echo_string]"
LABEL_INTEGER = "[int]"
LABEL_SKID_GO = "[skid_go]"
LABEL_POURER_1 = "[pourer_1]"
LABEL_POURER_2 = "[pourer_2]"
LABEL_GET_SKID_POS = "[skid_pos]"
LABEL_DELAY = "[delay]"

    #ankommende Labels
LABEL_EXPECT_STRING = "[expect_string]"
LABEL_EXPECT_INT = "[expect_int]"


class connection(object):
    
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        
    def connect(self):
        """
            Verbindung über seriellen Port herstellen
        """
        try:
            self.conn = serial.Serial(self.port, 
                                      self.baudrate,
                                      timeout=SERIAL_TIMEOUT)
            return True
        
        except Exception, msg:
            self.conn = False
            debug(msg, 2)
            return False
        
    def close(self):
        self.conn.close()
        
    def write_line(self, string):
        self.conn.write(string)
        self.conn.write(LINE_END)
    
    def read_line(self):
        return self.conn.readline().rstrip('\n')
           
    def send_int(self, value):
        """
            einen Integer an den Mikrocontroller über den Seriellen Port senden
        """
        self.write_line(LABEL_INTEGER)
        debug("Anfrage läuft - warte auf Rückmeldung")
        if self.read_line() == LABEL_EXPECT_INT:
            self.write_line(str(value))
            return True
        else:
            debug("Fehler bei senden von integer", 2)
            return False
    
    def get_skid_pos(self):
        self.write_line(LABEL_GET_SKID_POS)
        debug("Anfrage läuft - warte auf Rückmeldung")
        return self.read_line()

    def skid_goto(self, pos):
        """
            Befehl für eine neue Schlittenposition senden
        """
        self.write_line(LABEL_SKID_GO)
        debug("Anfrage läuft - warte auf Rückmeldung")
        if self.read_line() == LABEL_EXPECT_INT:
            self.write_line(str(pos))
            return True
        else:
            debug("Fehler bei senden von neuer Schlittenposition", 2)
            return False
        
    def pourer_1(self, delay):
        """
            Dosierer 1 betätigen und für delay - ms offen halten
        """
        self.write_line(LABEL_POURER_1)
        debug("Anfrage läuft - warte auf Rückmeldung")
        if self.read_line() == LABEL_EXPECT_INT:
            self.write_line(str(delay))
            return True
        else:
            debug("Fehler bei senden von Dosiererinformationen", 2)
            return False
        
    def pourer_2(self, delay):
        """
            Dosierer 2 betätigen und für delay - ms offen halten
        """
        self.write_line(LABEL_POURER_2)
        debug("Anfrage läuft - warte auf Rückmeldung")
        if self.read_line() == LABEL_EXPECT_INT:
            self.write_line(str(delay))
            return True
        else:
            debug("Fehler bei senden von Dosiererinformationen", 2)
            return False
        
    def delay(self, delay):
        """
            zum Entwickeln den Roboter einfach nach einer verzögerung von delay
            weitermachen lassen...
            TODO: wird nicht im produktivbetrieb benötigt - entfernen
        """
        self.write_line(LABEL_DELAY)
        debug("Anfrage läuft - warte auf Rückmeldung")
        if self.read_line() == LABEL_EXPECT_INT:
            self.write_line(str(delay))
        else:
            debug("Fehler bei senden von verzögernung", 2)
            print "fehler beim senden von verzögerung"
            return False
        
            