#!/usr/bin/env python
#-*- coding: latin-1 -*-

try:
    import pygame, os    
    from tombola import FileBMP
    from tombolaTabellone import *
    from tombolaConfig import *
    from pygame.locals import *
    from tombolaLog import *
    #import pygame._view
    import subprocess
except ImportError as message:
    print("Impossibile caricare il modulo. {0}".format(message))
    raise SystemExit

    
class RunJob():

    def jobImportaDaUSB(self):
        # rimozione dei file vecchi
        subprocess.call([CONST.KPATH_JOB + '/copiafiledaUSB.sh', 'remove'])   
        # monta la chiavetta USB e copia i file e poi la smonta
        lrc = subprocess.call(['sudo', CONST.KPATH_JOB + '/copiafiledaUSB.sh'
                                , 'mount', 'sda1'])   
        #print ("DBG jobImportaDaUSB lrc: ", lrc)
        return lrc

    def jobPDFtoIMG(self):
        # converte tutti i file da PDF a BITMAP
        lrc = subprocess.call([CONST.KPATH_JOB + '/convertePDFtoJPG.sh'])   
        #print ("DBG jobPDFtoJPG lrc: ", lrc)
        return lrc

    def contaFile(self):
        lpath = '.' + CONST.KPATH_JOB + '/appoggio' 
        lfile_cont = sum(os.path.isfile(os.path.join(lpath, f)) \
                                        for f in os.listdir(lpath))
        #print ('DBG contaFile lrc: ', lpath, ' n.', lfile_cont)
        return lfile_cont
        

class Pubblica:

    def __init__(self, a_dispalySurface, a_Config, a_Tabellone):
        self._SCREEN = a_dispalySurface
        self._Config = a_Config
        self._tabellone = a_Tabellone #(self._SCREEN, self._Config)  
        """ tempo durata immagine 5 secondi il default 
        get secondi dal nome File, i primi 5 char (max 99999)"""
        self._tempoImg=5  

    def onInizializza(self):
        self._posImgPubblica = [int(self._tabellone._posTabellone[0] 
                        + self._tabellone.sizeScreen[0] * 0.1)
                        , int(self._tabellone._posTabellone[1] 
                        + self._tabellone.sizeScreen[1] * 0.1)]
        self._dimImgPubblica = self._Config.dimPubblicazioneIMG
        self.iRunJob = RunJob()
        self.iidxImgPubblicate = 0
        self._FileBMP = FileBMP(CONST.KPATH_PUB)
        self.iFileBMP = []
        self._RettArrot = RettArrot()
        self.caricaImg()

    def caricaImg(self):
        ilog.stampa('Pubblica - Carica Immagini', [])
        if self.iRunJob.jobImportaDaUSB() == 0:
            if self.iRunJob.contaFile() > 0:
                self.iRunJob.jobPDFtoIMG()
        ilog.stampa('Pubblica - Fine Carica Immagini', [])

    def onPubblicaImg(self): 
        """ Espone i file Immagine """
        #--- immagine + box
        #try:
        _altreImg = self.onPubblicaNextImg()    
        ilog.stampa('Pubblica - onPubblicaImg 1', [])
        # se non ci sono altre immagini resetto il contatore 
        #                                   per ricominciare da capo
        if not _altreImg: 
            self.iidxImgPubblicate = 0
        #_altreImg = True
        #while _altreImg:
            #_altreImg = self.onPubblicaNextImg()    
            #time.sleep(5)        
        #print ('DBG onPubblicaImg esce ')

        #except pygame.error, pygame.message:
            #print 'Immagine non caricata. File:', nomePNG
            #raise SystemExit, message        

    def onPubblicaNextImg(self): 
        """ Pubblica l'immagine successiva e torna a False se era
        l'ultima altrimenti a True se ce ne sono altre """
        _idxImg = 0
        #--- se elenco file vuoto allora prova a prendere i nomi 
        #---                            dei file se esistono
        ilog.stampa('onPubblicaNextImg: ', self.iidxImgPubblicate)
        if self.iidxImgPubblicate == 0: 
            self.iFileBMP = self._FileBMP.getListFileBMP() #elenco dei file Immagini da pubblicare
            #self.iFileBMP = self._FileBMP.listFileBMP
            self.iidxImgPubblicate = len(self.iFileBMP)

        if self.iidxImgPubblicate == 0:
            return False  # NON CI SONO  IMMAGINI
        
        #ricava l'indice dell'immagine da prendere 
        _idxImg = len(self.iFileBMP) - self.iidxImgPubblicate  
        # get dalla lista dell'immagine da mostrare
        _FileBMP = self.iFileBMP[_idxImg] 
        #print ('DBG onPubblicaNextImg iFileBMP: ', _FileBMP
        #           , ' iFileBMP.icartella: ', self.iFileBMP.icartella)
        ilog.stampa('Pubblica - onPubblicaNextImg 1: ', [_FileBMP])

        # imposta il num di secondi di esposizione di questa immagine
        self.setTempoImg(_FileBMP)  

        _pngImgload = pygame.image.load(os.path.join(
                    self.iFileBMP.icartella, _FileBMP)).convert_alpha()
        ilog.stampa('Pubblica - onPubblicaNextImg 2: '
                                    , [self._dimImgPubblica[0]
                                    , self._dimImgPubblica[1]])
        _xShift = -140 #45
        _yShift = -85 #75
        #--- pulizia dello spazio per l'immagine
        _small_rect = pygame.Rect(self._posImgPubblica[0] + _xShift
                    , self._posImgPubblica[1] + _yShift
                    , self._dimImgPubblica[0] + 21 
                    , self._dimImgPubblica[1] + 21 ) 
        self._RettArrot.drawRoundRect(self._tabellone._SCREEN
                            , CONST.KCOL_NERO, _small_rect, 0 
                            , self._dimImgPubblica[2]
                            , self._dimImgPubblica[3]) 
        #--- scala l'immagine 
        ilog.stampa('Pubblica - onPubblicaNextImg 3: '
                        , [_pngImgload, (self._dimImgPubblica[0]-20)
                        , (self._dimImgPubblica[1]-60)])
        _imgSurfaceObj = self._tabellone.on_aspectScale(_pngImgload
            , (self._dimImgPubblica[0]-20, self._dimImgPubblica[1]-60))
        #_imgSurfaceObj = _pngImgload
        #--- box 
        _small_rect = pygame.Rect(self._posImgPubblica[0] 
                            + _xShift, self._posImgPubblica[1] 
                            + _yShift, self._dimImgPubblica[0]-5
                            , self._dimImgPubblica[1]-35)
        ilog.stampa('Pubblica - onPubblicaNextImg 4: '
                        , [_pngImgload, (self._dimImgPubblica[0]-20)
                        , (self._dimImgPubblica[1]-60)])
        self._RettArrot.drawRoundRect(self._tabellone._SCREEN
                        , CONST.KCOL_ROSSO, _small_rect, 0 
                        , self._dimImgPubblica[2]
                        , self._dimImgPubblica[3])
        #--- blit dell'immagine 
        _x, _y = self._Config.risoluzVideo
        _x1, _y1 = _imgSurfaceObj.get_rect().size 
        
        ilog.stampa('Pubblica - onPubblicaNextImg 4: '
                            , [_x1, ' ', _y1, ' File: ', _FileBMP])
        self._SCREEN.blit(_imgSurfaceObj, ((_x - _x1)/2
                            , self._posImgPubblica[1] + _yShift+10))

        ilog.stampa('Pubblica - onPubblicaNextImg FINE', [])
        self.iidxImgPubblicate = self.iidxImgPubblicate - 1
        if self.iidxImgPubblicate == 0:
            return False  # NON CI SONO PIU' ALTRE IMMAGINI
            #print ('DBG onPubblicaImg esce ')
        else:
            return True  # CI SONO ALTRE IMMAGINI
        
    def setTempoImg(self, a_nomeFile=''):
        """ Imposta il num secondi dal nome file 
        nella variabile _tempoImg """
        l_lstr = []
        if len(a_nomeFile) > 5:
            for l_str in a_nomeFile[:5]:
                if l_str.isnumeric():
                    l_lstr.append(l_str)
        else:
            for l_str in a_nomeFile:
                if l_str.isnumeric():
                    l_lstr.append(l_str)
  
        l_appo = ''.join(l_lstr)
        if l_appo.isnumeric():
            self._tempoImg = int(l_appo)
        else:
            self._tempoImg = 5


    def getTempoImg(self):
        """ Torna il num secondi dal nome file nella variabile _tempoImg """
        if self._tempoImg == 0:
            return 5 # il default
        else:
            return self._tempoImg  
