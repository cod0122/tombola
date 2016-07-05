'''
Created on 04/gen/2013

@author: alberto
'''
#!/usr/bin/env python
#-*- coding: latin-1 -*-
#import logging
#import logging.config

class Log():
    
    def __init__(self):
        self.fileLOG = open('log_messaggi.txt', 'w')
        # Configure the logging system
        #logging.config.fileConfig('logconfig.ini')        
        #logging.basicConfig(filename='tombolaApp.log',level=logging.DEBUG)
        
    def close(self):
        self.fileLOG.close()
        
    def stampa(self, a_testata='Test', *a_dati ):
        if len(a_dati) > 0:
            print(a_testata, a_dati, end='.\n', file=self.fileLOG)
        else:
            print(a_testata, end='.\n', file=self.fileLOG)
        #self.fileLOG.flush()

global ilog 
ilog = Log()  # oggetto x scrivere il LOGO
