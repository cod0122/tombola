#!/usr/bin/env python
#-*- coding: latin-1 -*-

try:
    import sys, pygame,  serial, time,  random
    from tombolaLog import *
    from tombolaTabellone import *
    from tombola import *
    from tombolaConfig import *
    from tombolaPub import *
    from pygame.locals import *
    import threading
    #import Queue
#    import pygame._view
    #import RPi.GPIO as GPIO
except ImportError as message:
    print("Impossibile caricare il modulo. {0}".format(message))
    raise SystemExit
 



class BufferNumeri:
    
    def __init__(self):
        self._BNumeri = []
        self._idxBufferInp=-1
        self._idxBufferOut=-1

    def _addNumero(self, anum=0):   # carica un numero nel buffer 
        self._idxBufferInp = self._idxBufferInp + 1
        self._BNumeri.insert(self._idxBufferInp, anum)
        if self._idxBufferInp > 900:
            if self._idxBufferOut > 0:
                self._comprimeBuffer()

    def _comprimeBuffer(self):    
        # comprime il buffer x evitare che diventi troppo grande 
        _lBAppoggio = self._BNumeri[
                            self._idxBufferOut:self._idxBufferInp] 
        self._BNumeri = _lBAppoggio
        self._idxBufferOut=0
        self._idxBufferInp=self._idxBufferOut - self._idxBufferInp

    def _getNumero(self):  # preleva il numero dal buffer se c'e'
        _lnumero = 0
        if self._idxBufferInp > self._idxBufferOut:
            self._idxBufferOut = self._idxBufferOut + 1
            _lnumero = self._BNumeri[self._idxBufferOut]
            ilog.stampa('_getNumero: ', [_lnumero])
        return _lnumero




class thSerialPort (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self._iserial = serial.Serial("/dev/ttyAMA0", 2400, timeout=0.2)    
        self._iserial.open 

    def run(self):
        ilog.stampa('Start THREADING', [])
        self.alive = True
        #_numeroInput=0

        while True:
            #if not App._ilockRS232.locked():  # se semaforo VERDE
            self._onGetDaRS232()


    def _onGetDaRS232(self):
        """ get da Serial Port Raspberry PI  """
        try:
            #_rxdati = serial.Serial ("/dev/ttyAMA0", 2400, timeout=0.2)

            #get da porta seriale e trasforma in stringa
            _BufferInput = self._iserial.readline().decode("utf-8")  

            if len(_BufferInput) > 0:

                #mette in una lista senza virgola 
                _listDato = _BufferInput.split(',') 
                #print ('DBG _listDato:', *_listDato, file=_fileLOG)
                for _datoStr in _listDato: #scorre la lista 
                    #rimuove i char di eol dal mumero     
                    _dato = _datoStr.strip().strip('/n/r')    

                    if _dato.isnumeric():
                        _numeroInput = int(_dato)
                        #Inserisce numero nel BUFFER di lavoro 
                        iBufferNumeri._addNumero(_numeroInput)   
                        #break;   #trovato il numero esco daf ciclo

        except OSError as err:
            ilog.stampa('_onGetDaRS232: Errore OSError: ', err)
            # [Errno 11] Resource temporarily unavailable
  #          print ('Errore risorsa GPIO (4) non disponibile')
            pass
        except serial.SerialException as errInput:
            print (
            '_onGetDaRS232: Errore Input senza dati. Proseguo comunque')
            ilog.stampa('_onGetDaRS232: Errore Input: ', errInput)
            pass
        except:
            print ('_onGetDaRS232: Errore generico. Proseguo comunque')
            print ('errore:{0};{0};{0}.' 
                                .format (sys.exec_info[0]
                                ,sys.exec_info[1],sys.exec_info[2]))
            raise
            
        finally:
            pass

    def stop(self):
        self._iserial.close
        self.alive = False
#exitFlag



#--- Classe PRINCIPALE ------------------------------------------------
class App:
    
    def __init__(self):
        self._running = True
        self._flagDisplayUpdate = False
        self._display_surf = None
        self._Config = Config() # Funzioni di Configurazione Tombola
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup (4,GPIO.IN)        # dati
        #self._ilockRS232 = threading.Lock()

       
    def _onInizializza(self, a_risoluzVideo, a_tipoDisplay):
        self._Config.risoluzVideo = a_risoluzVideo
        self._Config.tipoDisplay = a_tipoDisplay
        self._numeriUsciti = []
        self._numeroUscito=0
        self._primoNumeroGiaRicevuto = False
        self._nuovaPartitaConferma = False  
        self._tabelloneCompleto = False
        self._giocoInPausa = False
        #--- prepara Window (init + set_mode) ------------------------
        _size = self._Config.set_modeVideo() 

        ilog.stampa('Risoluzione video scelta: '
                                , [self._Config.risoluzVideo])
        
        if a_tipoDisplay == 'F':
            #, pygame.FULLSCREEN, 32)
            self._SCREEN = pygame.display.set_mode(_size) 
        elif a_tipoDisplay == 'N':
            self._SCREEN = pygame.display.set_mode(
                                            _size, pygame.NOFRAME) 
        else:
            self._SCREEN = pygame.display.set_mode(
                                            _size, pygame.RESIZABLE)  
        
        ilog.stampa('Risoluzione accettata self._SCREEN: '
                                                , [self._SCREEN])

        self._clock = pygame.time.Clock()
        pygame.mouse.set_visible(False)
        #--------------------------------------------------------------
            
        #--- definisce oggetti principali
        self._Tombola = Tombola() # Funzioni della Tombola
        self._Tabellone = Tabellone(self._SCREEN, self._Config) 
        self._TombolaStato = TombolaStato()
        self._ctrLampeggiante=0
        #self._SCREEN.fill(CONST.KCOL_BIANCO)  # colore di sfondo
        #--- Per visualizzare la Pubblilita'
        self.iPubblica = Pubblica(self._SCREEN, self._Config) 

        #print ('DBG _onInizializza _arg_tipoInput: ', _arg_tipoInput)
        if _arg_tipoInput == 'G' or _arg_tipoInput == 'E': 
            ilog.stampa('DBG _onInizializza LANCIA THREAD', [])
            #print ('DBG _onInizializza LANCIA THREAD')
            ithSerialPort.start()
 
            #self._queueLock = threading.Lock()
            # coda x il thread dove bufferizzare i numeri usciti
            #self._numEstrattiQueue = Queue.Queue(10) 

    def onStart(self):
        #--- settaggi iniziali e disegna il tabellone 
        #--- Inizialmente parte sempre ripristinando l'ultima partita
        self._Tombola = self._TombolaStato.ripriStato()
        self._Tombola.startTombola()
        self._Tabellone.on_disegnaTabellone(self._numeriUsciti)
        #if self._Tombola.getIdNomeGioco() == 0:
        #    self._Tombola.startTombola()
         
        self._Tabellone.on_disegnaBoxNumeroUscito() 
        _nomeGioco = self._Tombola.getNomeGioco()
        self._Tabellone.on_scriveNomePartita(_nomeGioco
                       , self._Tombola.getNomeFileGiocoImg()
                       , self._Tombola.getStartDataOra())
        self._onEsponiTabellone()
        #self._onDisegnaCentone()
        self._Tabellone.on_disegnaAreaVincite()
        self._Tombola.setStatoTombolaStart()
        self._Tabellone.on_scriveStatoTombola(
                                self._Tombola.getStatoTombolaDesc())
        self._attivaDisplayUpdate()
      
    def _onGetNumeroInput(self):
        """ get dalla Coda dei dati da Serial Port Raspberry PI  """
        try:
            _numeroInput = 0
            
            #iApp.ilockRS232.acquire()
            if _arg_tipoInput == 'G' or _arg_tipoInput == 'E': 
                #--- acquisisce i numeri del BUFFER (coda RS232)
                _numeroInput = iBufferNumeri._getNumero()    

            if _numeroInput == 0:
                if _arg_tipoInput == 'K' or _arg_tipoInput == 'E': 
                    #--- get numero da tastiera
                    for event in pygame.event.get():   
                        _numeroInput = self._onEventDaTastiera(event)

            #ilog.stampa('_onGetNumeroInput: ', [_numeroInput])
            #iApp.ilockRS232.release()

        except OSError as err:
            ilog.stampa('_onGetNumeroInput: OSError. \
                                Proseguo comunque', err)
            # [Errno 11] Resource temporarily unavailable
            #print ('Errore risorsa GPIO (4) non disponibile')
            pass
        except serial.SerialException as errInput:
            ilog.stampa('_onGetNumeroInput: Errore Input senza dati. \
                                Proseguo comunque', errInput)
            pass
        except:
            ilog.stampa('Errore: '
              , [sys.exec_info[0], sys.exec_info[1], sys.exec_info[2]])

            raise

        finally:
            #self._numEstrattiQueue.clear()
            #self._queueLock.release()
            return _numeroInput

      
    """ 
    def _onGetDaRS232(self):
        # get da Serial Port Raspberry PI  
        try:
            _numeroInput=0
            #_rxdati = serial.Serial ("/dev/ttyAMA0", 2400, timeout=0.2)
            _BufferInput = self._iserial.readline().decode("utf-8")
            #print ("{0}" .format (_BufferInput), file=_fileLOG)
            #_fileLOG.flush()

            if len(_BufferInput) > 0:
               #print('DBG _BufferInput: ', _BufferInput, file=_fileLOG)
               #_fileLOG.flush()

               _listDato = _BufferInput.split(',') 
               #print ('DBG _listDato:', *_listDato, file=_fileLOG)
               for _datoStr in _listDato: #scorre la lista 
               #_dato = _listDato
               #--- estrazioone dei numeri 
                  _dato = _datoStr.strip().strip('/n/r')

                  if _dato.isnumeric():
                        #print ('DBG _dato: ', _dato, file=_fileLOG)
                        #_fileLOG.flush()
                        _numeroInput = int(_dato)
                        break;   #trovato il numero esco daf ciclo

        except OSError as err:
            # [Errno 11] Resource temporarily unavailable
  #          print ('Errore risorsa GPIO (4) non disponibile')
            pass
        except serial.SerialException as errInput:
            print ('Errore Input senza dati. Proseguo comunque')
            pass
        except:
            print ('Errore generico. Proseguo comunque')
            print ('errore:{0};{0};{0}.' .format (sys.exec_info[0]
                        ,sys.exec_info[1],sys.exec_info[2]))
            raise

        finally:
            return _numeroInput
    """
     
    def _onEventDaGpio(self, _channel):
        """ evento da Gpio Raspberry PI  """
        try:
            _numeroGpio=0
            #print ("GPIO.input")
            _x=GPIO.input (4)             # polling clk
            if _x==True:
                _rxdati = serial.Serial ("/dev/ttyAMA0"
                                                , 2400, timeout=0.2)
                _BufferInput=_rxdati.readline().decode("utf-8")
                _BufferInput.strip()
                #print ("{0}" .format (_BufferInput))
                if len(_BufferInput) > 0:
                    #--- mette in una lista senza l'aterisco 
                    _listDato = _BufferInput.split('*') 
                    #print ("_listDato:{0}" .format (_listDato))
                    for _dato in _listDato: #scorre la lista 
                        #--- estrazioone dei numeri 
                        if _dato.isnumeric():
                            _numeroGpio = int(_dato)

        except OSError as err:
            ilog.stampa('_onEventDaGpio: OSError. \
                                Proseguo comunque', err)
            # [Errno 11] Resource temporarily unavailable
            #print ('Errore risorsa GPIO (4) non disponibile')
            pass
        except serial.SerialException as errInput:
            print ('Errore Input senza dati. Proseguo comunque')
            ilog.stampa('_onEventDaGpio: Errore Input: ', errInput)
            
            pass
        except:
            print ('Errore generico. Proseguo comunque')
            print ('errore:{0};{0};{0}.' 
                        .format (sys.exec_info[0],sys.exec_info[1]
                                    ,sys.exec_info[2]))
            raise
             
        return _numeroGpio


    def _onTrattaNumeroUscito(self, _numeroInput=0):
                    
        ilog.stampa('_numeroInput: ', [_numeroInput])
        if _numeroInput > 0:
            if _numeroInput == CONST.KTASTO_EXIT:
                self._tastoUscita()
            elif _numeroInput == CONST.KTASTO_IMG:
                self._tastoImg()
            # se non sono in pausa x mostrare le img
            elif not self._Tombola.ifStatoTombolaImg():    
                if _numeroInput == CONST.KTASTO_PAUSA:
                    self._tastoPausa()
                #solo se non sono in pausa
                elif not self._Tombola.ifStatoTombolaPausa(): 

                    if _numeroInput <= self._Config.numMaxTombola:
                        self._setNumeroInUscita(_numeroInput)

                if _numeroInput > self._Config.numMaxTombola:
                    if _numeroInput == CONST.KTASTO_NUOVO_GIOCO:  
                        self._tastoNuovoGioco()
                    elif _numeroInput == CONST.KTASTO_QUATERNA:
                        self._tastoSetQuaterna()
                    elif _numeroInput == CONST.KTASTO_CINQUINA:
                        self._tastoSetCinquina()
                    elif _numeroInput == CONST.KTASTO_DECINA:
                        self._tastoSetDecina()
                    elif _numeroInput == CONST.KTASTO_TOMBOLA:
                        self._tastoSetTombola()
                    elif _numeroInput == CONST.KTASTO_CENTONE:
                        self._tastoCentone()
 
    
    def _onEventDaTastiera(self, event):
        """ controlla eventi da tastiera  """  
        _numeroUscito = 0
        
        if event.type == pygame.QUIT:
            self._tastoUscita()
            
        elif event.type == pygame.KEYDOWN:
            tasti_premuti = pygame.key.get_pressed()
            if tasti_premuti[pygame.K_ESCAPE] \
                       or (tasti_premuti[pygame.K_LALT] \
                           and tasti_premuti[pygame.K_F4]):
                _numeroUscito = CONST.KTASTO_EXIT
                #self._tastoUscita()

                
            elif not self._Tabellone.ifBlinkAttivo() \
                    and not self._Tabellone.ifTombolaCompletata() \
                    and not self._giocoInPausa \
                    and (tasti_premuti[pygame.K_0]  
                         or tasti_premuti[pygame.K_1] 
                         and (not self._primoNumeroGiaRicevuto 
                              or self._numeroUscito < self._Config.numMaxTombola) 
                         or tasti_premuti[pygame.K_2] 
                         and (not self._primoNumeroGiaRicevuto 
                              or self._numeroUscito < self._Config.numMaxTombola)
                         or tasti_premuti[pygame.K_3] 
                         and (not self._primoNumeroGiaRicevuto 
                              or self._numeroUscito < self._Config.numMaxTombola)
                         or tasti_premuti[pygame.K_4] 
                         and (not self._primoNumeroGiaRicevuto 
                              or self._numeroUscito < self._Config.numMaxTombola)
                         or tasti_premuti[pygame.K_5] 
                         and (not self._primoNumeroGiaRicevuto 
                              or self._numeroUscito < self._Config.numMaxTombola)
                         or tasti_premuti[pygame.K_6] 
                         and (not self._primoNumeroGiaRicevuto 
                              or self._numeroUscito < self._Config.numMaxTombola)
                         or tasti_premuti[pygame.K_7] 
                         and (not self._primoNumeroGiaRicevuto 
                              or self._numeroUscito < self._Config.numMaxTombola)
                         or tasti_premuti[pygame.K_8] 
                         and (not self._primoNumeroGiaRicevuto 
                              or self._numeroUscito < self._Config.numMaxTombola)
                         or tasti_premuti[pygame.K_9] 
                         and (not self._primoNumeroGiaRicevuto 
                              or self._numeroUscito < self._Config.numMaxTombola)): 
                #ogni numero tombola e' fatto da 2 numeri, es 01,57,... 
                if self._primoNumeroGiaRicevuto:   
                    self._primoNumeroGiaRicevuto = False
                    self.onSetSecondoNumeroRicevuto(tasti_premuti)
                    _numeroUscito = self._numeroUscito
                else:
                    # se nome gioco non presente lo inserisco in automat
                    #if self._Tombola.getIdNomeGioco() == 0: 
                    #    self.onNuovoGioco()
                    self._primoNumeroGiaRicevuto = True
                    # verifica e imposta il PRIMO numero da tastiera
                    self.onSetPrimoNumeroRicevuto(tasti_premuti) 
                    self._Tombola.setStatoTombolaInput()
                    self._Tabellone.on_scriveStatoTombola(
                                   self._Tombola.getStatoTombolaDesc())
                    
            elif tasti_premuti[pygame.K_BACKSPACE] \
                                           and not self._giocoInPausa:
                if not self._Tabellone.ifBlinkAttivo() \
                        and not self._Tabellone.ifTombolaCompletata():
                    self._primoNumeroGiaRicevuto = False    
                    self.primoNumero = False
            elif tasti_premuti[pygame.K_DELETE] \
                                           and not self._giocoInPausa:
                if not self._Tabellone.ifBlinkAttivo() \
                         and not self._Tabellone.ifTombolaCompletata():
                    # se primo numero gia' digitato resetto il flag         
                    if self._primoNumeroGiaRicevuto:    
                        self._primoNumeroGiaRicevuto = False       
                    else:
                        # cancella ultimo numero-Va indietro tipo Ctrl-Z
                        self.onToglieUltimoNumero()     
                        self._tabelloneCompleto = False
                        
            elif (tasti_premuti[pygame.K_F1] \
                                     or tasti_premuti[pygame.K_q]):
                self._primoNumeroGiaRicevuto = False   
                _numeroUscito = CONST.KTASTO_QUATERNA
                #self._tastoSetQuaterna()
            elif (tasti_premuti[pygame.K_F2] \
                                     or tasti_premuti[pygame.K_c]):
                self._primoNumeroGiaRicevuto = False    
                _numeroUscito = CONST.KTASTO_CINQUINA
                #self._tastoSetCinquina()
            elif (tasti_premuti[pygame.K_F3] \
                                     or tasti_premuti[pygame.K_d]):
                self._primoNumeroGiaRicevuto = False   
                _numeroUscito = CONST.KTASTO_DECINA
                #self._tastoSetDecina()
            elif (tasti_premuti[pygame.K_F4] \
                                     or tasti_premuti[pygame.K_t]):
                self._primoNumeroGiaRicevuto = False    
                _numeroUscito = CONST.KTASTO_TOMBOLA
                #self._tastoSetTombola()
            #--- PARTITA in PAUSA!!!
            elif (tasti_premuti[pygame.K_F10] \
                                      or tasti_premuti[pygame.K_p]):   
                _numeroUscito = CONST.KTASTO_PAUSA
            #--- Visualizza le IMMAGINI
            elif tasti_premuti[pygame.K_i]:   
                _numeroUscito = CONST.KTASTO_IMG
            #--- Nuova PARTITA !!!
            elif (tasti_premuti[pygame.K_F6] \
                                      or tasti_premuti[pygame.K_n]):   
                _numeroUscito = CONST.KTASTO_NUOVO_GIOCO
            #--- Gioco: Centone o 90
            elif tasti_premuti[pygame.K_x]: 
                _numeroUscito = CONST.KTASTO_CENTONE

            #--- Ripristino TUTTO Tabellone (utile se crash iprovviso)                  
            elif tasti_premuti[pygame.K_F11]:  
                self._primoNumeroGiaRicevuto = False    
                self._Tombola = self._TombolaStato.ripriStato()
                self.onStartGioco()
            #--- se INVIO allora piglia in automatico un nuovo numero
            elif tasti_premuti[pygame.K_RETURN]:  
                _numeroUscito = self._estraeNumeroInAutom()
                
            else:
                self._primoNumeroGiaRicevuto = False
                if not self._Tabellone.ifBlinkAttivo() \
                        and not self._Tabellone.ifTombolaCompletata() \
                        and not self._giocoInPausa:
                   self._Tombola.setStatoTombolaAttivo()
                   self._Tabellone.on_scriveStatoTombola(
                                  self._Tombola.getStatoTombolaDesc())

        return _numeroUscito

    def onSetPrimoNumeroRicevuto(self, tasti_premuti):
        if tasti_premuti[pygame.K_0]:
            self._numeroUscito = 0
        elif tasti_premuti[pygame.K_1]:
            self._numeroUscito = 10
        elif tasti_premuti[pygame.K_2]:
            self._numeroUscito = 20
        elif tasti_premuti[pygame.K_3]:
            self._numeroUscito = 30
        elif tasti_premuti[pygame.K_4]:
            self._numeroUscito = 40
        elif tasti_premuti[pygame.K_5]:
            self._numeroUscito = 50
        elif tasti_premuti[pygame.K_6]:
            self._numeroUscito = 60
        elif tasti_premuti[pygame.K_7]:
            self._numeroUscito = 70
        elif tasti_premuti[pygame.K_8]:
            self._numeroUscito = 80
        elif tasti_premuti[pygame.K_9]:
            self._numeroUscito = self._Config.numMaxTombola
    def onSetSecondoNumeroRicevuto(self, tasti_premuti):
        if tasti_premuti[pygame.K_0]:
            self._numeroUscito += 0
        elif tasti_premuti[pygame.K_1]:
            self._numeroUscito += 1
        elif tasti_premuti[pygame.K_2]:
            self._numeroUscito += 2
        elif tasti_premuti[pygame.K_3]:
            self._numeroUscito += 3
        elif tasti_premuti[pygame.K_4]:
            self._numeroUscito += 4
        elif tasti_premuti[pygame.K_5]:
            self._numeroUscito += 5
        elif tasti_premuti[pygame.K_6]:
            self._numeroUscito += 6
        elif tasti_premuti[pygame.K_7]:
            self._numeroUscito += 7
        elif tasti_premuti[pygame.K_8]:
            self._numeroUscito += 8
        elif tasti_premuti[pygame.K_9]:
            if self._numeroUscito < self._Config.numMaxTombola:
                self._numeroUscito += 9
                
                
    def _tastoUscita(self):
        if _arg_tipoInput != 'K': 
            if ithSerialPort.isAlive():
                ithSerialPort.stop()
                ithSerialPort._stop()
        self._running = False
        self._TombolaStato.salvaStato(self._Tombola)

        self._resetDisplayUpdate()
        self._Tombola.setStatoTombolaExit()
        self._Tabellone.on_scriveStatoTombola(
                                   self._Tombola.getStatoTombolaDesc())

    def _tastoNuovoGioco(self):
        if self._nuovaPartitaConferma:
            self._nuovaPartitaConferma = False
            self._primoNumeroGiaRicevuto = False    
            self.onNuovoGioco()
        else:
            self._nuovaPartitaConferma = True
            self._Tombola.setStatoTombolaReset()
            self._Tabellone.on_scriveStatoTombola(
                                   self._Tombola.getStatoTombolaDesc())

        if _arg_tipoInput == 'G' or _arg_tipoInput == 'E': 
            _tasto = 0 
            # se e' stato premuto il tasto nuova partita...
            while self._nuovaPartitaConferma \
                                and _tasto != CONST.KTASTO_NUOVO_GIOCO: 
                # fa semplicemente video in attesa della nuova partita
                self.onSplatter()  
                self.onRender()
                _tasto = self._onGetNumeroInput()

    def _tastoPausa(self):
        self._Tombola.setStatoTombolaPausa()
        self._Tabellone.on_scriveStatoTombola(
                                   self._Tombola.getStatoTombolaDesc())
        _tasto = 0 
        # in pausa... in play solo ripigiando il tasto 
        while _tasto != CONST.KTASTO_PAUSA: 
            _tasto = self._onGetNumeroInput()
        self._Tombola.setStatoTombolaAttivo()
        self._Tabellone.on_scriveStatoTombola(
                                self._Tombola.getStatoTombolaDesc())

    def _tastoImg(self):
        if self._Tombola.ifStatoTombolaImg():
            self._Tombola.setStatoTombolaAttivo() 
            self._Tabellone.on_disegnaSfondo()
            _nomeGioco = self._Tombola.getNomeGioco()
            self._Tabellone.on_scriveNomePartita(_nomeGioco
                            , self._Tombola.getNomeFileGiocoImg()
                            , self._Tombola.getStartDataOra())
            self._onEsponiTabellone()
            #self._onDisegnaCentone()
            self._Tabellone.on_disegnaAreaVincite()
        else:
            # mette la tombola in pausa x immagini
            self._Tombola.setStatoTombolaImg()  
            #print ('DBG _tastoImg setStatoTombolaImg')
         
    def _tastoSetQuaterna(self):
        self._Tabellone.set_quaterna()
        self._setStatoVincite()
        self._Tabellone.on_disegnaAreaVincite()
        self._attivaDisplayUpdate()
    def _tastoSetCinquina(self):
        self._Tabellone.set_cinquina()
        self._setStatoVincite()
        self._Tabellone.on_disegnaAreaVincite()
        self._attivaDisplayUpdate()
    def _tastoSetDecina(self):
        self._Tabellone.set_decina()
        self._setStatoVincite()
        self._Tabellone.on_disegnaAreaVincite()
        self._attivaDisplayUpdate()
    def _tastoSetTombola(self):
        self._Tabellone.set_tombola()
        self._Tabellone.on_disegnaAreaVincite()
        if self._Tabellone.ifTombolaCompletata():
            self._Tombola.setStatoTombolaFine()
            self._Tabellone.on_scriveStatoTombola(
                                self._Tombola.getStatoTombolaDesc())
        else:
            self._Tombola.setStatoTombolaAttivo()
            self._Tabellone.on_scriveStatoTombola(
                                self._Tombola.getStatoTombolaDesc())
        self._attivaDisplayUpdate()
    def _setStatoVincite(self):
        if self._Tabellone.ifBlinkAttivo():
             self._Tombola.setStatoTombolaCheck()
        else:
             self._Tombola.setStatoTombolaAttivo()
        self._Tabellone.on_scriveStatoTombola(
                                   self._Tombola.getStatoTombolaDesc())
            

    def _tastoCentone(self):
        """Tasto Centone premuto"""
        self._Config.setCentone()
        self._numeroUscito = self._Tombola.getUltimoNumero()
        self._numeriUsciti = self._Tombola.getUltimiNumeri(0) 
        self._onDisegnaCentone()
        self._Tabellone.on_disegnaAreaVincite()
        self._attivaDisplayUpdate()
        
    def _onDisegnaCentone(self):
        """spegne/accende il Centone"""
        if self._Config.centone == False:
            if self._Config.centone != self._Tabellone.flagCentone:
                self._Tabellone.on_puliziaAreaVincite()
                self._Tabellone.clearBoxCentone()
        else:
            if self._Config.centone != self._Tabellone.flagCentone:
                self._Tabellone.on_puliziaAreaVincite()
            self._Tabellone.on_disegnaCentone(self._numeriUsciti, self._numeroUscito)
        
    def _setNumeroInUscita(self, _numero=0):
        self._Tombola.setStatoTombolaAttivo()
        self._Tabellone.on_scriveStatoTombola(
                                self._Tombola.getStatoTombolaDesc())
        # in questo resetto sempre il flag
        self._primoNumeroGiaRicevuto = False    
        if not self._Tabellone.ifBlinkAttivo() \
                        and not self._Tabellone.ifTombolaCompletata():
            # se nome gioco non presente lo inserisco in automatico
            #if self._Tombola.getNomeGioco() == '': 
            #    self.onNuovoGioco()
            if _numero == 0:
                _numero = self._estraeNumeroInAutom()
            if _numero > 0:
                self._numeroUscito = _numero
                self._setNuovoNumero()
            else:
                self._tabelloneCompleto = True
                self._Tombola.setStatoTombolaFine()
                self._Tabellone.on_scriveStatoTombola(
                                  self._Tombola.getStatoTombolaDesc())


    def _estraeNumeroInAutom(self):
       """ estrae un numero random """
       # random di un numero compreso 1 - 90 o 100
       _numeroRnd = random.randrange(1,(self._Config.numMaxTombola + 1))
       _ctr = 1
       # esce dal ciclo solo se un numero mai uscito      
       while (self._Tombola.ifNumeroUscito(_numeroRnd)) and _ctr <= self._Config.numMaxTombola: 
           _numeroRnd = random.randrange(1,(self._Config.numMaxTombola + 1)) 
           _ctr += 1
       # se non ha trovato alcun numero non ancora uscito azzera    
       if _ctr > self._Config.numMaxTombola:   
           _numeroRnd = 0
       return _numeroRnd


    def _setNuovoNumero(self):
        self._Tombola.setNumeroUscito(self._numeroUscito)
        self._onEsponiTabellone()    
        self._TombolaStato.salvaStato(self._Tombola)

    def onToglieUltimoNumero(self):
        self._numeroUscito = self._Tombola.getUltimoNumero()
        self._Tombola.setNumeroUscito(self._numeroUscito)
        self._onEsponiTabellone()    
        self._TombolaStato.salvaStato(self._Tombola)
        return self._numeroUscito
        
    
    def onNuovoGioco(self):    
        self._Tombola.startNuovaTombola()
        _nomeGioco = self._Tombola.getNomeGioco()
        self._Tabellone.set_nuovoGioco()
        self._Tabellone.on_scriveNomePartita(_nomeGioco
                          , self._Tombola.getNomeFileGiocoImg()
                          , self._Tombola.getStartDataOra())
        self._onEsponiTabellone()    
        self._Tombola.setStatoTombolaStart()
        self._Tabellone.on_scriveStatoTombola(
                                 self._Tombola.getStatoTombolaDesc())
        self._tabelloneCompleto = False
        self._attivaDisplayUpdate()
      
    def onStartGioco(self):    
        self.onStart()
        #self._onEsponiTabellone()
 

    def _onEsponiTabellone(self):    
        self._numeroUscito = self._Tombola.getUltimoNumero()
        # get di tutti i numeri usciti
        self._numeriUsciti = self._Tombola.getUltimiNumeri(0) 
        self._Tabellone.on_disegnaTabellone(self._numeriUsciti, self._numeroUscito)
        self._onDisegnaCentone()
        self._Tabellone.on_disegnaBoxNumeroUscito() 
        self._Tabellone.on_scriveNumeroUscito(self._numeroUscito)
        self._numeriUsciti = self._Tombola.getUltimiNumeri(7)
        self._Tabellone.on_scriveUltimiNumeriUsciti(self._numeriUsciti)
        self._attivaDisplayUpdate()                   

    def _onLampeggio(self):
        """ Gestione dei campi da fare in blinking """
        if self._Tabellone.ifBlinkAttivo():
            self._Tombola.setStatoTombolaCheck()
            self._Tabellone.on_scriveStatoTombola(
                                  self._Tombola.getStatoTombolaDesc())
            self._ctrLampeggiante += 1
            if self._ctrLampeggiante == 20: #velocita' lampeggio
                self._ctrLampeggiante = 0 
                self._Tabellone.on_disegnaAreaVincite()
            self._attivaDisplayUpdate()
            #self.onRender()
        #else:
            #if self._Tombola.ifStatoTombolaPausa():
                #self._Tombola.setStatoTombolaAttivo()
                #self._Tabellone.on_scriveStatoTombola(
                #self._Tombola.getStatoTombolaDesc())
                
           
    def onLoop(self):
        pass
    def onRender(self):
        #print ("onRender")
        self._resetDisplayUpdate()
        pygame.display.update()
        

    def onSplatter(self):  
        """ fa semplicemente un giochetto video in attesa 
        della nuova partita """
        if self._tabelloneCompleto:
            if self.onToglieUltimoNumero() > 0:
                pass
            else:
                self._tabelloneCompleto = False
                self._nuovaPartitaConferma = False
                self._primoNumeroGiaRicevuto = False    
                self.onNuovoGioco()
        else:
            _numero = self._estraeNumeroInAutom()
            if _numero > 0:
                self._numeroUscito = _numero
                self._setNuovoNumero()
            else:
                self._tabelloneCompleto = True
                self._Tabellone.on_scriveStatoTombola(
                                  self._Tombola.getStatoTombolaDesc())
        self._attivaDisplayUpdate()

    def onCleanup(self):
        pygame.quit()
        sys.exit()

    def _ifDisplayUpdate(self):
        return self._flagDisplayUpdate 
    def _attivaDisplayUpdate(self):
        #print ("_attivaDisplayUpdate")
        self._flagDisplayUpdate = True
    def _resetDisplayUpdate(self):
        self._flagDisplayUpdate = False


    #--------------- PRIMA FUNZIONE CHIAMATA --------------------------
    def onExecute(self, a_arg_risoluzVideo, a_arg_tipoDisplay):
        
        self._onInizializza(a_arg_risoluzVideo, a_arg_tipoDisplay)
        #sys.settrace(iApp._onGetDaQueueRS232 )       
        # arg 1 = indicazione tipo input G=GPIO/RS232 - K=TASTIERA 
        #         - I=solo visualizza Immagini
        if _arg_tipoInput != 'I': 
            if self.onStart() == False:
                self._running = False

        """ CICLO PRINCIPALE PROGRAMMA """
        while ( self._running ):
        
            _numeroUscito = 0   # codice del TASTO premuto

            self._clock.tick(40) # Limita a non piu' di 40 frame al secondo
            self._onLampeggio()
               
            #if self._nuovaPartitaConferma: 
               #self.onSplatter()  
                
            #if _arg_tipoInput == 'K': 
                #for event in pygame.event.get():   
                    #_numeroUscito = self._onEventDaTastiera(event)
            #else:
                #self._onEventDaGpio() # prende il numero da GPIO
                # add rising edge detection on a channel
                #GPIO.add_event_detect(4, GPIO.RISING
                #             , callback=self._onEventDaGpio) 
                    
            #self.onLoop()

            #self.onRender()
            if self._ifDisplayUpdate():
                self.onRender()
                if _arg_tipoInput == 'I' \
                                or self._Tombola.ifStatoTombolaImg(): 
                    _l_startTime = time.time()
                    _l_elapsedTime = 0
                    #print ('DBG _l_startTime: ',  _l_startTime)
                    # in attesa... o che non si premi un qls tasto
                    while _numeroUscito == 0 \
                             and _l_elapsedTime \
                                    < self.iPubblica.getTempoImg(): 
                        _numeroUscito = self._onGetNumeroInput()
                        _l_elapsedTime = time.time() - _l_startTime
                        
                    #time.sleep(self.iPubblica.getTempoImg())        

            # arg 1 = indicazione tipo input G=GPIO/RS232 - K=TASTIERA
            #if _arg_tipoInput == 'G': 
                # blocca qui l'esecuzione fino all'evento
                #GPIO.wait_for_edge(4, GPIO.RISING) 
                #if pygame.QUIT in (e.type for e in pygame.event.get()):
                #    self._tastoUscita()
                #else:
                #print('DBG onExecute ', end='.\n', file=_fileLOG)
                #_fileLOG.flush()
            if _numeroUscito == 0:
                #get dei tasti/numeri premuti
                _numeroUscito = self._onGetNumeroInput()    
                #x i numeri da GPIO
                #_numeroUscito = self._onEventDaGPIO(4)     
                #for _numeroUscito in _numeriUsciti:
                
            if _numeroUscito > 0:
                self._onTrattaNumeroUscito( _numeroUscito )
                self._attivaDisplayUpdate()                   
                # add rising edge detection on a channel (ignorax200ms)  
                #old GPIO.add_event_detect(4, GPIO.RISING
                #, callback=self._onEventDaGpio, bouncetime=200) 

            if _arg_tipoInput == 'I' \
                               or self._Tombola.ifStatoTombolaImg(): 
                ilog.stampa(
                     'App - Chiama self.iPubblica.onPubblicaImg()', [])
                self.iPubblica.onPubblicaImg() 
                ilog.stampa(
                'App - Fine Chiama self.iPubblica.onPubblicaImg()', [])
                self._attivaDisplayUpdate()                   

        self.onCleanup()
    #------------------- PRIMA FUNZIONE CHIAMATA ----------------------


if __name__ == "__main__" :
    #_fileLOG = open("log_messaggi.txt", "w")
    
    # arg 1 = indicazione tipo input G=GPIO/RS232
    #                  - K=TASTIERA - E=RS232 e TASTIERA 
    #                  - I=SOLO IMMAGINI    
    _arg_tipoInput = '' 
    # arg 2 = indicazione della risoluzione video: 
    #         es. 0,0 (default) altrimento 1024,768 ecc...
    _arg_risoluzVideo = [0, 0]
    # arg 3 = tipo schermata F=fullscreen, N=no frame, R=resizable 
    _arg_tipoDisplay = '' 

    if len(sys.argv) > 1: #solo tipo di INPUT
        _arg_tipoInput = str(sys.argv[1]).upper()
    if len(sys.argv) > 2: #input e dimensione dello screen es. 640 480
        risoluzVideo = (sys.argv[2]).split(',')
        if risoluzVideo[0].isdigit() and risoluzVideo[1].isdigit():
            _arg_risoluzVideo = int(risoluzVideo[0]), int(risoluzVideo[1]) 
        else:
            raise "ERRORE DATI RISOLUZIONE, DIGITARE AD ESEMPIO 1024,768 "
    if len(sys.argv) > 3: #tutti i parametri
        _arg_tipoDisplay = str(sys.argv[3]).upper()

    # oggetto x gestire il buffer dei numeri usciti
    iBufferNumeri = BufferNumeri() 
    
    if _arg_tipoInput != 'K' and _arg_tipoInput > ' ': 
        ithSerialPort = thSerialPort(1, 'thLeggeRS232') 
   
    global iApp 
    iApp = App()
    
    ilog.stampa('Argomenti iniziali: ' 
             , [_arg_tipoInput, _arg_risoluzVideo, _arg_tipoDisplay])

    #almeno devono essere indicati input e dim dello screen es. 640 480
    if len(sys.argv) > 2: 
        iApp.onExecute(_arg_risoluzVideo, _arg_tipoDisplay)
    else:
        print('Indicare i seguenti parametri: ')
        print('1- il Tipo di Input: G=SERIAL PORT; K=tastiera; ',
                         'E=RS232 e TASTIERA; I=solo mostra Immagini')
        print('2- la Risoluzione Video X,Y: '
                     '\n Le tue Risoluzione Video sono: \n {0}'  
                        , str(iApp._Config.allMyRisoluzVideo) ) 
        print('3- il Tipo Schermata: F=Fullscreen '
                                    ', N=no frame, R=resize;')
        print('ESEMPIO: sudo python3 tombolaApp e 1660,1200 f ')

    
    #_fileLOG.close()
    ilog.close()

