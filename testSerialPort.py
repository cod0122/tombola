#!/usr/bin/env python
#-*- coding: latin-1 -*-

import sys, pygame, random, serial, time

_iserial = serial.Serial("/dev/ttyAMA0", 2400, timeout=0.2)
#					   port='/dev/ttyAMA0',
#					   baudrate = 2400, 
#					   parity=serial.PARITY_NONE,
#					   stopbits=serial.STOPBITS_ONE,
#					   bytesize=serial.EIGHTBITS,
#					   timeout=0.3
#					)
#"/dev/ttyAMA0", 2400, timeout=1)    
_iserial.open 
 
try:
    print ('RS232 in ascolto....')
    temp=0
    k_numeroX = ''
    k_numero = 0
    while True:
        _xdati = _iserial.read(1)
        if _xdati[:1] > b'':
            k_numeroX = str(ord(_xdati[:1]))
            if not (k_numeroX.isdigit()):
                print ('ERRORE DATO NON NUMERICO ', k_numeroX)
            else:
                k_numero = int(k_numeroX)
                if k_numero > 200:
                    print (k_numero)
                    temp=0
                else:
                    if (k_numero - temp) > 1:
                        print ('ERRORE DATO NON IN SEQUENZA DA ', temp, ' SALTA A ', k_numero)
                        temp=k_numero
                    else:
                        #print (k_numero)
                        temp=k_numero
	  
except KeyboardInterrupt:
   _iserial.close()
