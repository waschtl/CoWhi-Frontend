#!/usr/bin/python
# -*- coding: utf-8 -*-
#debug.py
"""
    ein wenig Debuggen in eigenen Projekten 
    das soll kein Ersatz für das logging Modul werden - wenns kniffeliger wird nehmen
    wir das natürlich... ;)
    ... aber ich hab immerhin rausgefunden wie das läuft...
"""
import sys

DEBUG = True
DEBUG_LEVEL = 0
DEBUG_LEVEL_DICT = {0: 'Meldung',
                    1: 'Warnung',
                    2: 'Fehler'}

def currentframe():
    """
        Return the frame object for the caller's stack frame.
    """
    try:
        raise Exception
    except:
        return sys.exc_traceback.tb_frame.f_back

def get_func_name(*args, **kwargs):
    """
        den aufrufenden Funktionsnamen zurückgeben
    """
    f = currentframe()
    f = f.f_back
    f = f.f_back
    return f.f_code.co_name


def debug(message, level=0):
    """
        ein paar Debugging- Meldungen auswerfen
    """
    if DEBUG:
        if level >= DEBUG_LEVEL:
            print 'debug [%s]- (%s) - %s' % (DEBUG_LEVEL_DICT[level], get_func_name(), message)