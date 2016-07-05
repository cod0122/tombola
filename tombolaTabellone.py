#!/usr/bin/env python
#-*- coding: latin-1 -*-

try:
    import  pygame, os, time
    from pygame.locals import *
    #import pygame._view
    from tombolaConfig import *
except ImportError as message:
    print("Impossibile caricare il modulo. {0}".format(message))
    raise SystemExit
 

class RettArrot:

    def drawRoundRect(self, surface, color, rect, width, xr, yr):
        
        clip = surface.get_clip()
        
        # left and right
        surface.set_clip(clip.clip(rect.inflate(0, -yr*2)))
        pygame.draw.rect(surface, color, rect.inflate(1-width,0), width)

        # top and bottom
        surface.set_clip(clip.clip(rect.inflate(-xr*2, 0)))
        pygame.draw.rect(surface, color, rect.inflate(0,1-width), width)

        # top left corner
        surface.set_clip(clip.clip(rect.left, rect.top, xr, yr))
        pygame.draw.ellipse(surface, color, pygame.Rect(rect.left
                                , rect.top, 2*xr, 2*yr), width)

        # top right corner
        surface.set_clip(clip.clip(rect.right-xr, rect.top, xr, yr))
        pygame.draw.ellipse(surface, color, pygame.Rect(rect.right-2*xr
                                , rect.top, 2*xr, 2*yr), width)

        # bottom left
        surface.set_clip(clip.clip(rect.left, rect.bottom-yr, xr, yr))
        pygame.draw.ellipse(surface, color, pygame.Rect(rect.left
                                , rect.bottom-2*yr, 2*xr, 2*yr), width)

        # bottom right
        surface.set_clip(clip.clip(rect.right-xr
                                            , rect.bottom-yr, xr, yr))
        pygame.draw.ellipse(surface, color
                    , pygame.Rect(rect.right-2*xr
                                , rect.bottom-2*yr, 2*xr, 2*yr), width)

        surface.set_clip(clip)


class DisegnaCerchio:
    def disegna(self, a_surface, a_colore, a_raggio, a_x, a_y, a_spessore=1):
        pygame.draw.circle(a_surface, a_colore, (a_x, a_y), a_raggio, a_spessore)

    
class Tabellone:
    """ Gestione del Tabellone """

    def __init__(self, dispalySurface, Config):
        self._Config = Config
        self._SCREEN = dispalySurface
        self._RettArrot = RettArrot()
        self._DisegnaCerchio = DisegnaCerchio()
        self._dimSchermo = self._Config.risoluzVideo
        #--- dimensioni dello SCHERMO
        self._width, self._height = self._dimSchermo[0], self._dimSchermo[1] 
        self.sizeScreen =  self._width, self._height

        self._xSquare = 0
        self._ySquare = 0
        #--- array di 100 stato numero sucito/non uscito (1/0/-1=non settato)
        self._set_InitFlagNumUsciti()

        self._flgBlink = False
        #--- flag di CENTONE esposto oppure meno
        #self.flagCentone = False
 
        """Dimensione dei Font""" 
        self._dimFont = Config.dimFont

        """variabili segnalazione Vittorie (0=si, 2=no)"""
        self._quaternaOK = 2
        self._cinquinaOK = 2
        self._decinaOK = 2
        self._tombolaOK = 2
        
        """valori per fare il blinking del ultimo numero uscito sul tabellone"""
        self._squareTombolaBlink = None
        self._numeroBlink = None    
        self._cur_time = time.time()
        self._prev_time = self._cur_time

        #--- pos iniziale del tabellone 
        self._posTabellone = [int(self._width * 0.01), int(self._height * 0.01)]  
        
    
    def set_OccupazioneTabellone(self, a_tabelloneFull=False):
        #--- dimensioni e posizione del Tabellone dei numeri
        if a_tabelloneFull: # dimensione Full screen
            self._occupTabelloneX = 1.28 #--- occup larg tab: 100% schermo
            self._occupTabelloneY = 0.87 #--- occup alt tab: 90% schermo
        else:
            self._occupTabelloneX = 0.80  #--- occup larg tab: 65% schermo
            self._occupTabelloneY = 0.85  #--- occup alt tab: 85% schermo
        #--- Quadratino singolo della tombola
        self._largSquare = (self._width * self._occupTabelloneX) * 0.07 #0.08 
        self._altSquare = (self._height * self._occupTabelloneY) / 9.75 #10.25 #9 
        self._spazioTraSquareX = self._largSquare * 0.1   
        self._spazioTraSquareY = self._altSquare * 0.05 #0.1   
        self._spazioTraGruppiSquareX = self._largSquare * 0.1  
        self._spazioTraGruppiSquareY = self._altSquare * 0.05 #0.1  
        
        self.on_disegnaLogo() #--- espone il LOGO

        
    def _set_InitFlagVincite(self):
        """variabili segnalazione Vittorie (0=si, 2=no)"""
        self._quaternaOK = 2
        self._cinquinaOK = 2
        self._decinaOK = 2
        self._tombolaOK = 2


    def _set_InitFlagNumUsciti(self):
        """ Array flag stato numero x evitare di ridisegnare tutte le volte
        il quadrato (1=uscito/0=non uscito/-1=non settato) """
        self._tabFlagNumUsciti = [-1 for i in range(101)]


    def set_nuovoGioco(self):
        """Cosa da fare x inzio partita"""
        self._set_InitFlagVincite()
        self.on_disegnaAreaVincite()
        
        
    def set_quaterna(self):
        if self._quaternaOK == 2: # se Spento
        #    self._quaternaOK = 1  # mette quadratrino in lampeggio
        #elif self._quaternaOK == 1: # se in Lammpeggio
            self._quaternaOK = 0  # mette quadratrino,  OK - vincita
        else:
            self._quaternaOK = 2  # toglie quadratrino

        
    def set_cinquina(self):
        if self._cinquinaOK == 2:
        #    self._cinquinaOK = 1  # mette quadratrino in lampeggio
        #elif self._cinquinaOK == 1: # se in Lammpeggio
            self._cinquinaOK = 0  # mette quadratrino
        else:
            self._cinquinaOK = 2  # toglie quadratrino

        
    def set_decina(self):
        if self._decinaOK == 2:
        #    self._decinaOK = 1  # mette quadratrino in lampeggio
        #elif self._decinaOK == 1: # se in Lammpeggio
            self._decinaOK = 0  # mette quadratrino
        else:
            self._decinaOK = 2  # toglie quadratrino

        
    def set_tombola(self):
        if self._tombolaOK == 2:
        #    self._tombolaOK = 1  # mette quadratrino in lampeggio
        #elif self._tombolaOK == 1: # se in Lammpeggio
            self._tombolaOK = 0  # mette quadratrino
        else:
            self._tombolaOK = 2  # toglie quadratrino

        
    def ifTombolaCompletata(self):
        if self._tombolaOK == 0:
            return True
        else:
            return False
            
    def ifBlinkAttivo(self):
        if self._quaternaOK == 1 or self._cinquinaOK == 1 \
                    or self._decinaOK == 1 or self._tombolaOK == 1: 
            return True
        else:
            return False

        
    def on_disegnaSfondo(self):
        """ riempie lo sfondo """
        #_squareXYZ = [1, 1, self._dimSchermo[0], self._dimSchermo[1]] 
        #_squareTombola = pygame.Rect(_squareXYZ)
        #self._RettArrot.drawRoundRect(
        #       self._SCREEN, CONST.KCOL_NERO, _squareTombola, 0 
        #       , self._dimSchermo[0], self._dimSchermo[1])
        #print ('DBG on_disegnaSfondo ')
        self._SCREEN.fill(CONST.KCOL_NERO) #


    def _getDimLogo(self):
        """Get dimensioni Logo"""
        _dimLogo = [135 * self._Config.risCoeffX, 60 * self._Config.risCoeffY]
        return _dimLogo
    def on_disegnaLogo(self):
        """Espone Logo"""
        #--- oggetto Logo dimensioni e posizione
        _imgLogo = 'logo_tmb.png'
        _dimLogo = self._getDimLogo()
        _logoImgload = pygame.image.load(os.path.join(
                                    CONST.KPATH_IMG, _imgLogo)).convert()
        _imgSurfaceObj = self.on_aspectScale(_logoImgload
                                                    , (_dimLogo))
        _rectLogo = _imgSurfaceObj.get_rect()
        _posLogo = [int(self._width - _rectLogo.width)
                                    , int(self._height - _rectLogo.height)]
        self._SCREEN.blit(_imgSurfaceObj, (_posLogo))
        

    def on_disegnaTabelloneOLD(self, a_numeriUsciti, a_ultimoNumUscito=0):
        """ disegna il tabellone"""
            #dim tabellone 
        self._dimTabellone = [0, 0] 
        _numeroTombola=0
        _numSquareX=0
        _numSquareY=0
        _posSquareX=0
        _posSquareY=self._posTabellone[1]
        _fontNumero = pygame.font.Font('FrankfurtGothic.ttf'
                                        , self._dimFont['fontNumero'])
        #_fontNumero = pygame.font.Font('freesansbold.ttf'
        #_fontNumero = pygame.font.Font('courbd.ttf'
        #_fontNumero = pygame.font.Font('serpents.ttf'
        
        print ('DBG on_disegnaTabellone ultimoNumUscito' , a_ultimoNumUscito)
        #import pdb;pdb.set_trace() # DEBUGGING
        _posInizioX=self._posTabellone[0] 
        
        _posSquareX = _posInizioX
        for _yNumeroSquare in range(9):
            _numSquareY += 1
            if _numSquareY > 3:
                _numSquareY = 1
                _posSquareY += self._spazioTraGruppiSquareY
            _numSquareX = 0
            for _xNumeroSquare in range(10):
                _numSquareX += 1
                if _numSquareX > 5:
                    _numSquareX = 0
                    _posSquareX += self._spazioTraGruppiSquareX
                #--- disegna i singoli quadratini del tabellone     
                _squareXYZ = [_posSquareX, _posSquareY
                                , self._largSquare, self._altSquare] 
                _squareTombola = pygame.Rect(_squareXYZ)
                #--- posizione X successiva
                _posSquareX += (self._largSquare + self._spazioTraSquareX) 
                # verifica se numero e' tra gli usciti 
                _trovato = 0
                _numeroTombola += 1
                if a_ultimoNumUscito == 0:
                    self._numeroBlink = None
                if _numeroTombola == a_ultimoNumUscito:
                    #ult.3 par: 0=no bordi; n,n=arrotondare angoli 
                    self._RettArrot.drawRoundRect(self._SCREEN
                        , CONST.KCOL_GIALLO, _squareTombola, 0, 8, 8) 
                    _surfaceNumero = _fontNumero.render(
                        str(_numeroTombola), True, CONST.KCOL_NERO
                        , CONST.KCOL_GIALLO) 
                    self._squareTombolaBlink = _squareTombola #salva posizione box x lampeggio
                    self._numeroBlink = str(_numeroTombola) #salva numero x lampeggio
                    _trovato = 1
                    #self._tabFlagNumUsciti[_numeroTombola] = _trovato
                    _rectNumero = _surfaceNumero.get_rect()
                    _posCenter = _squareTombola.center
                    self._SCREEN.blit(_surfaceNumero
                                , (_posCenter[0] - _rectNumero[2]/2
                                , _posCenter[1] - _rectNumero[3]/2.5) )#_rectNumero[3]/2) )
                else:
                    if _numeroTombola in a_numeriUsciti: 
                        _trovato = 1
                    # verifica se e' cambiato lo stato per ridisegno
                    if self._tabFlagNumUsciti[_numeroTombola] != _trovato \
                               or self._numeroBlink == str(_numeroTombola) \
                               or a_ultimoNumUscito == 0:
                        #if _numeroTombola == a_ultimoNumUscito:
                        #    self._tabFlagNumUsciti[_numeroTombola] = -1 #qui deve poi rifare 
                        #else:
                        self._tabFlagNumUsciti[_numeroTombola] = _trovato
                        #--- scrive il quadratino      
                        if _trovato == 1:
                            #if _numeroTombola == a_ultimoNumUscito:
                            #    self._RettArrot.drawRoundRect(self._SCREEN
                            #        , CONST.KCOL_GIALLO, _squareTombola, 0, 8, 8) 
                            #    _surfaceNumero = _fontNumero.render(
                            #        str(_numeroTombola), True, CONST.KCOL_BIANCO
                            #        , CONST.KCOL_GIALLO) 
                            #    self._squareTombolaBlink = _squareTombola #salva posizione box x lampeggio
                            #    self._numeroBlink = str(_numeroTombola) #salva numero x lampeggio
                            #else:
                            self._RettArrot.drawRoundRect(self._SCREEN
                                , CONST.KCOL_ROSSO, _squareTombola, 0, 8, 8) 
                            _surfaceNumero = _fontNumero.render(
                                str(_numeroTombola), True, CONST.KCOL_BIANCO
                                , CONST.KCOL_ROSSO) 
                        else:
                            #ult.3 par: 0=no bordi; n,n=arrotondare angoli 
                            self._RettArrot.drawRoundRect(self._SCREEN
                                , CONST.KCOL_TRASPARENTE, _squareTombola, 0, 8, 8) 
                        #--- scrive il numero      
                        #print ('DBG on_disegnaTabellone 2 _numeroTombola e ultimoNumUscito' , _numeroTombola, a_ultimoNumUscito)
                        #if _trovato == 1 and _numeroTombola != a_ultimoNumUscito:
                        #    _surfaceNumero = _fontNumero.render(
                        #            str(_numeroTombola), True, CONST.KCOL_BIANCO
                        #            , CONST.KCOL_ROSSO) 
                        #else:
                            #if _numeroTombola == ultimoNumUscito:
                            #    if not self._flgBlink: # x fare lampeggiare 
                            #        _surfaceNumero = _fontNumero.render(
                            #            str(_numeroTombola), True, CONST.KCOL_NERO
                            #            , CONST.KCOL_GIALLO) 
                            #    else:
                            #        _surfaceNumero = _fontNumero.render(
                            #            str(_numeroTombola), True, CONST.KCOL_BIANCO
                            #            , CONST.KCOL_ROSSO) 
                            #else:
                        #if _trovato != 1:  # se Numero non ancora estratto
                            _surfaceNumero = _fontNumero.render(
                                    str(_numeroTombola), True, CONST.KCOL_NERO
                                    , CONST.KCOL_TRASPARENTE) 
                            #self._numeroBlink = None
                        _rectNumero = _surfaceNumero.get_rect()
                        _posCenter = _squareTombola.center
                        self._SCREEN.blit(_surfaceNumero
                                    , (_posCenter[0] - _rectNumero[2]/2
                                    , _posCenter[1] - _rectNumero[3]/2.5) )#_rectNumero[3]/2) )
                                
                _ultimaPosTabelloneX = _posSquareX
           #--- posizione X e Y successiva
            _posSquareX = _posInizioX
            _posSquareY += (self._altSquare + self._spazioTraSquareY) 

        self._dimTabellone[0] = _ultimaPosTabelloneX - self._posTabellone[0] 
        self._dimTabellone[1] = _posSquareY - self._posTabellone[1] 

        
    def on_disegnaTabellone(self, a_numeriUsciti, a_ultimoNumUscito=0, a_centone=False, a_forzaEsponi=False):
        """ disegna il tabellone
        forzaEsponi = True per accendere cmq il numero"""
            #dim tabellone 
        self._dimTabellone = [0, 0] 
        _nrRigheCaselle=9
        _numeroTombola=0
        _numSquareX=0
        _numSquareY=0
        _posSquareX=0
        _posSquareY=self._posTabellone[1]
        _coloreNumeroOff = CONST.KCOL_NERO
        _coloreNumeroOn = CONST.KCOL_BIANCO
        _fontNumero = pygame.font.Font('FrankfurtGothic.ttf'
                                        , self._dimFont["fontNumero"])
        if a_centone:
            _nrRigheCaselle = 10
        #print ('DBG on_disegnaTabellone ultimoNumUscito' , a_ultimoNumUscito)
        #import pdb;pdb.set_trace() # DEBUGGING
        _posInizioX=self._posTabellone[0] 
        
        _posSquareX = _posInizioX
        for _yNumeroSquare in range(_nrRigheCaselle):
            _numSquareY += 1
            if _numSquareY > 3:
                _numSquareY = 1
                _posSquareY += self._spazioTraGruppiSquareY
            _numSquareX = 0

            for _xNumeroSquare in range(10):
                _numSquareX += 1
                if _numSquareX > 5:
                    _numSquareX = 0
                    _posSquareX += self._spazioTraGruppiSquareX
                #--- disegna i singoli quadratini del tabellone     
                _squareXYZ = [_posSquareX, _posSquareY
                                , self._largSquare, self._altSquare] 
                _squareTombola = pygame.Rect(_squareXYZ)
                #--- posizione X successiva
                _posSquareX += (self._largSquare + self._spazioTraSquareX) 
                # verifica se numero e' tra gli usciti 
                _trovato = 0
                _numeroTombola += 1
                if _numeroTombola == 100:
                    _fontNumero = pygame.font.Font('FrankfurtGothic.ttf'
                                        , int(self._dimFont["fontNumero"]*0.8))
                if _numeroTombola > 90:
                    _coloreNumeroOff = CONST.KCOL_BLU
                    _coloreNumeroOn = CONST.KCOL_BLU
                if a_ultimoNumUscito == 0:
                    self._numeroBlink = None
                if _numeroTombola == a_ultimoNumUscito:
                    #ult.3 par: 0=no bordi; n,n=arrotondare angoli 
                    self._RettArrot.drawRoundRect(self._SCREEN
                        , CONST.KCOL_GIALLO, _squareTombola, 0, 8, 8) 
                    _surfaceNumero = _fontNumero.render(
                        str(_numeroTombola), True, _coloreNumeroOff
                        , CONST.KCOL_GIALLO) 
                    self._squareTombolaBlink = _squareTombola #salva posizione box x lampeggio
                    self._numeroBlink = _numeroTombola #salva numero x lampeggio
                    _trovato = 1
                    #self._tabFlagNumUsciti[_numeroTombola] = _trovato
                    _rectNumero = _surfaceNumero.get_rect()
                    _posCenter = _squareTombola.center
                    self._SCREEN.blit(_surfaceNumero
                                , (_posCenter[0] - _rectNumero[2]/2
                                , _posCenter[1] - _rectNumero[3]/2.5) )#_rectNumero[3]/2) )
                else:
                    if _numeroTombola in a_numeriUsciti or a_forzaEsponi: 
                        _trovato = 1
                    # verifica se e' cambiato lo stato per ridisegno
                    if self._tabFlagNumUsciti[_numeroTombola] != _trovato \
                               or self._numeroBlink == _numeroTombola \
                               or a_ultimoNumUscito == 0:
                        self._tabFlagNumUsciti[_numeroTombola] = _trovato
                        #--- scrive il quadratino      
                        if _trovato == 1:
                            self._RettArrot.drawRoundRect(self._SCREEN
                                , CONST.KCOL_ROSSO, _squareTombola, 0, 8, 8) 
                            _surfaceNumero = _fontNumero.render(
                                str(_numeroTombola), True, _coloreNumeroOn
                                , CONST.KCOL_ROSSO) 
                        else:
                            #ult.3 par: 0=no bordi; n,n=arrotondare angoli 
                            self._RettArrot.drawRoundRect(self._SCREEN
                                , CONST.KCOL_TRASPARENTE, _squareTombola, 0, 8, 8) 
                            #--- scrive il numero      
                            _surfaceNumero = _fontNumero.render(
                                    str(_numeroTombola), True, _coloreNumeroOff
                                    , CONST.KCOL_TRASPARENTE) 
                            #self._numeroBlink = None
                        _rectNumero = _surfaceNumero.get_rect()
                        _posCenter = _squareTombola.center
                        self._SCREEN.blit(_surfaceNumero
                                    , (_posCenter[0] - _rectNumero[2]/2
                                    , _posCenter[1] - _rectNumero[3]/2.5) )#_rectNumero[3]/2) )
                                
                _ultimaPosTabelloneX = _posSquareX
           #--- posizione X e Y successiva
            _posSquareX = _posInizioX
            _posSquareY += (self._altSquare + self._spazioTraSquareY) 

        self._dimTabellone[0] = _ultimaPosTabelloneX - self._posTabellone[0] 
        self._dimTabellone[1] = _posSquareY - self._posTabellone[1] 
                        

    def on_blinkUltimoNumero(self):
        _fontNumero = pygame.font.Font('FrankfurtGothic.ttf'
                                        , self._dimFont['fontNumero'])
        if self._numeroBlink == 100:
            _fontNumero = pygame.font.Font('FrankfurtGothic.ttf'
                                    , int(self._dimFont["fontNumero"]*0.8))
        if self._squareTombolaBlink != None and self._numeroBlink != None:
            if self._flgBlink: # x fare lampeggiare 
                _coloreSfondo = CONST.KCOL_GIALLO
                _coloreNumero = CONST.KCOL_NERO
            else:
                _coloreSfondo = CONST.KCOL_ROSSO
                _coloreNumero = CONST.KCOL_BIANCO
            if self._numeroBlink > 90:
                _coloreNumero = CONST.KCOL_BLU

            self._RettArrot.drawRoundRect(self._SCREEN
                             , _coloreSfondo, self._squareTombolaBlink, 0, 8, 8) 
            _surfaceNumero = _fontNumero.render(
                                str(self._numeroBlink), True, _coloreNumero
                             , _coloreSfondo) 
            _rectNumero = _surfaceNumero.get_rect()
            _posCenter = self._squareTombolaBlink.center
            self._SCREEN.blit(_surfaceNumero
                                , (_posCenter[0] - _rectNumero[2]/2
                                , _posCenter[1] - _rectNumero[3]/2.5) )
            
            self._refreshFlgBlink() # tratta il flgBlink x lampeggio

                                           
    def clearBoxCentone(self):
        """ Nasconde i box del Centone dal tabellone"""
        #print ('DBG clearBoxCentone ')
        #self.flagCentone = False
        self._set_InitFlagNumUsciti()
        _posSquareY = self._dimTabellone[1] - self._altSquare
        _posSquareX = self._posTabellone[0] 
        #_numSquareX=0
        _clearRect = pygame.Rect(_posSquareX,_posSquareY, (self._largSquare*10) \
            + (self._spazioTraSquareX*10), self._altSquare + (self._spazioTraSquareY*2))
        pygame.draw.rect(self._SCREEN, CONST.KCOL_NERO, _clearRect, 0)
        #for _xNumeroSquare in range(10):
        #    _numSquareX += 1
        #    if _numSquareX > 5:
        #        _numSquareX = 0
        #        _posSquareX += self._spazioTraGruppiSquareX
        #    #--- disegna i singoli quadratini del tabellone     
        #    _squareXYZ = [_posSquareX, _posSquareY
        #                    , self._largSquare, self._altSquare] 
        #    _squareTombola = pygame.Rect(_squareXYZ)
        #    #--- posizione X successiva
        #    _posSquareX += (self._largSquare + self._spazioTraSquareX) 
        #        #--- scrive il quadratino      
        #    self._RettArrot.drawRoundRect(self._SCREEN
        #                        , CONST.KCOL_NERO, _squareTombola, 0, 8, 8) 

    
    def on_disegnaCentoneOLD(self, numeriUsciti, ultimoNumUscito=0):
        """ disegna i Numeri del CENTONE nel tabellone"""
        #self.flagCentone = True
        _numeroTombola=90
        _numSquareX=0
        _posSquareX=0
        _posSquareY = self._dimTabellone[1] + self._spazioTraGruppiSquareY * 2
        #_fontNumero = pygame.font.Font('freesansbold.ttf'
        _fontNumero = pygame.font.Font('FrankfurtGothic.ttf'
                                        , self._dimFont["fontNumero"])
        #_fontNumero100 = pygame.font.Font('freesansbold.ttf'
        _fontNumero = pygame.font.Font('FrankfurtGothic.ttf'
                                        , int(self._dimFont["fontNumero"]*0.8))
        _posInizioX=self._posTabellone[0] 
        _posSquareX = _posInizioX
        for _xNumeroSquare in range(10):
            _numSquareX += 1
            if _numSquareX > 5:
                _numSquareX = 0
                _posSquareX += self._spazioTraGruppiSquareX
            #--- disegna i singoli quadratini del tabellone     
            _squareXYZ = [_posSquareX, _posSquareY
                            , self._largSquare, self._altSquare] 
            _squareTombola = pygame.Rect(_squareXYZ)
            #--- posizione X successiva
            _posSquareX += (self._largSquare + self._spazioTraSquareX) 
            # verifica se numero e' tra gli usciti 
            _trovato = 0
            _numeroTombola += 1
            if _numeroTombola in numeriUsciti: 
                _trovato = 1
            # verifica se e' cambiato lo stato per ridisegno
            if self._tabFlagNumUsciti[_numeroTombola] != _trovato:
                if _numeroTombola == ultimoNumUscito:
                    self._tabFlagNumUsciti[_numeroTombola] = -1 #qui deve poi rifare 
                else:
                    self._tabFlagNumUsciti[_numeroTombola] = _trovato
                #--- scrive il quadratino      
                if _trovato == 1:
                    #ult.3 par: 0=no bordi; n,n=arrotondare angoli 
                    if _numeroTombola == ultimoNumUscito:
                        self._RettArrot.drawRoundRect(self._SCREEN
                            , CONST.KCOL_GIALLO, _squareTombola, 0, 8, 8) 
                    else:
                        self._RettArrot.drawRoundRect(self._SCREEN
                            , CONST.KCOL_ROSSO, _squareTombola, 0, 8, 8) 
                else:
                    #ult.3 par: 0=no bordi; n,n=arrotondare angoli 
                    self._RettArrot.drawRoundRect(self._SCREEN
                        , CONST.KCOL_TRASPARENTE
                        , _squareTombola, 0, 8, 8) 
            #--- scrive il numero      
                if _trovato == 1 and _numeroTombola != ultimoNumUscito:
                    if _numeroTombola == 100:
                        _surfaceNumero = _fontNumero100.render(
                            str(_numeroTombola), True, CONST.KCOL_BLU
                            , CONST.KCOL_ROSSO) 
                    else:
                        _surfaceNumero = _fontNumero.render(
                            str(_numeroTombola), True, CONST.KCOL_BLU
                            , CONST.KCOL_ROSSO) 
                else:
                    if _numeroTombola == ultimoNumUscito:
                        if _numeroTombola == 100:
                            _surfaceNumero = _fontNumero100.render(
                                str(_numeroTombola), True, CONST.KCOL_BLU
                                , CONST.KCOL_GIALLO) 
                        else:
                            _surfaceNumero = _fontNumero.render(
                                str(_numeroTombola), True, CONST.KCOL_BLU
                                , CONST.KCOL_GIALLO) 
                    else:
                        if _numeroTombola == 100:
                            _surfaceNumero = _fontNumero100.render(
                                str(_numeroTombola), True, CONST.KCOL_BLU
                                , CONST.KCOL_TRASPARENTE) 
                        else:
                            _surfaceNumero = _fontNumero.render(
                                str(_numeroTombola), True, CONST.KCOL_BLU
                                , CONST.KCOL_TRASPARENTE) 
                _rectNumero = _surfaceNumero.get_rect()
                _posCenter = _squareTombola.center
                self._SCREEN.blit(_surfaceNumero
                            , (_posCenter[0] - _rectNumero[2]/2
                            , _posCenter[1] - _rectNumero[3]/2) )
           #--- posizione X e Y successiva
        _posSquareX = _posInizioX


    def on_disegnaBoxNumeroUscito(self): 
        #--- box 
        self._rectBoxNumUscito = pygame.Rect(self._posTabellone[0]
                                                                    + self._dimTabellone[0] 
                                            , self._posTabellone[1]
                                            , int((self._width - self._dimTabellone[0])
                                                *0.96)
                                            , int(self._dimTabellone[1]*0.57)) 
                                            #, int(self._dimTabellone[0]*0.36)
        self._RettArrot.drawRoundRect(self._SCREEN, CONST.KCOL_BLU
                                            , self._rectBoxNumUscito, 2 , 10,  10) 


    def on_puliziaAreaVincite(self):
        """ Pulizia della Riga indicazione Vincite """
        #_fontObj = pygame.font.Font('freesansbold.ttf'
        _fontObj = pygame.font.Font('serpents.ttf'
                                    , self._dimFont["fontVincite"])
        #--- calcola l'occupazione delle scritte con una fittizia
        _tmbSurfaceObj = _fontObj.render('XXXXXXXXX', True
                    , CONST.KCOL_VERDE, CONST.KCOL_NERO)
        _rectTmbObj = _tmbSurfaceObj.get_rect()
        #--- pos dicitura Vincite
        _risCoeff = self._Config.risCoeff
        _x = (self._posTabellone[0] * 1.15)  
        if self._Config.centone == True:
            _y = int(self._height - _rectTmbObj.height*2.15) 
        else:
            _y = int(self._height - _rectTmbObj.height*1.15) 

        _dimBoxVincite =  [(_rectTmbObj.height*0.70), (_rectTmbObj.width*0.90)
                                            , int(15 * _risCoeff), int(15 * _risCoeff)]
        _posBoxVincite = [_x, _y]
        _posVincite =  [_posBoxVincite[0] + int(_dimBoxVincite[0] * 1.25), int(_y)]
        #--- Pulizia di tutto il rigone fino al Logo     
        _dimLogo = self._getDimLogo()
        _clearRect = pygame.Rect(0,_posBoxVincite[1], self._width - _dimLogo[0], int(15 * _risCoeff) * 2)
        pygame.draw.rect(self._SCREEN, CONST.KCOL_NERO, _clearRect, 0)
        #_textSurfaceObj, (_posVincite[0], _posVincite[1]))

        #--- QUATERNA
        pygame.draw.rect(self._SCREEN
                                    , CONST.KCOL_NERO 
                                    , (_posBoxVincite[0]
                                       , _posBoxVincite[1]
                                       , _dimBoxVincite[0]*1.10
                                       , _dimBoxVincite[1]*1.10)
                                    ,0 )
        _textSurfaceObj = _fontObj.render('Quaterna', True
                    , CONST.KCOL_NERO, CONST.KCOL_NERO)
        self._SCREEN.blit(_textSurfaceObj
                    , (_posVincite[0], _posVincite[1]))
        #--- Calcolo posizione X successiva (BOX e Dicitura)
        _rectTextSurfaceObj = _textSurfaceObj.get_rect()
        _posBoxVincite[0] =  _posVincite[0] + _rectTextSurfaceObj.width \
                                        + int(_dimBoxVincite[0] * 0.50) 
        _posVincite[0] = _posBoxVincite[0]  + _dimBoxVincite[0] * 2.50 
        #--- CINQUINA
        pygame.draw.rect(self._SCREEN
                                    , CONST.KCOL_NERO 
                                    , (_posBoxVincite[0]
                                       , _posBoxVincite[1]
                                       , _dimBoxVincite[0]*1.10
                                       , _dimBoxVincite[1]*1.10)
                                    ,0 )
        _textSurfaceObj = _fontObj.render('Cinquina', True
                    , CONST.KCOL_NERO, CONST.KCOL_NERO)
        self._SCREEN.blit(_textSurfaceObj
                    , (_posVincite[0], _posVincite[1]))
        #--- Calcolo posizione X successiva (BOX e Dicitura)
        _rectTextSurfaceObj = _textSurfaceObj.get_rect()
        _posBoxVincite[0] =  _posVincite[0] + _rectTextSurfaceObj.width \
                                        + int(_dimBoxVincite[0] * 0.50) 
        _posVincite[0] = _posBoxVincite[0]  + _dimBoxVincite[0] * 2.50 
        #--- DECINA
        pygame.draw.rect(self._SCREEN
                                    , CONST.KCOL_NERO 
                                    , (_posBoxVincite[0]
                                       , _posBoxVincite[1]
                                       , _dimBoxVincite[0]*1.10
                                       , _dimBoxVincite[1]*1.10)
                                    ,0 )
        _textSurfaceObj = _fontObj.render('Decina', True
                    , CONST.KCOL_NERO, CONST.KCOL_NERO)
        self._SCREEN.blit(_textSurfaceObj
                    , (_posVincite[0], _posVincite[1]))
        #--- Calcolo posizione X successiva (BOX e Dicitura)
        _rectTextSurfaceObj = _textSurfaceObj.get_rect()
        _posBoxVincite[0] =  _posVincite[0] + _rectTextSurfaceObj.width \
                                        + int(_dimBoxVincite[0] * 0.50) 
        _posVincite[0] = _posBoxVincite[0]  + _dimBoxVincite[0] * 3.50 
        #--- TOMBOLA
        pygame.draw.rect(self._SCREEN
                                    , CONST.KCOL_NERO 
                                    , (_posBoxVincite[0]
                                       , _posBoxVincite[1]
                                       , _dimBoxVincite[0]*1.10
                                       , _dimBoxVincite[1]*1.10)
                                    ,0 )
        _textSurfaceObj = _fontObj.render('TOMBOLA', True
                    , CONST.KCOL_NERO, CONST.KCOL_NERO)
        self._SCREEN.blit(_textSurfaceObj, (_posVincite[0], _posVincite[1]))


    def on_disegnaAreaVincite(self):
        """ Riga indicazione Vincite """
        #freesansbold
        _fontObj = pygame.font.Font('serpents.ttf'
                                    , self._dimFont["fontVincite"])
        #--- calcola l'occupazione delle scritte con una fittizia
        _tmbSurfaceObj = _fontObj.render('XXXXXXXXX', True
                    , CONST.KCOL_VERDE, CONST.KCOL_NERO)
        _rectTmbObj = _tmbSurfaceObj.get_rect()
        #--- pos dicitura Vincite
        _risCoeff = self._Config.risCoeff
        _x = (self._posTabellone[0] * 1.15)  
        if self._Config.centone == False:
            _y = int(self._height - _rectTmbObj.height*2.15) 
        else:
            _y = int(self._height - _rectTmbObj.height*1.15) 

        #_width = self._dimTabellone[1] 
        _dimBoxVincite =  [int(_rectTmbObj.height*0.70), int(_rectTmbObj.width*0.90)
                            , int(15 * _risCoeff), int(15 * _risCoeff)] #int(1 * _risCoeff)]
        _posBoxVincite = [_x, _y]
        _posVincite =  [_posBoxVincite[0] + int(_dimBoxVincite[0] * 1.25)
                                        , int(_y)]
        _rectVincite = pygame.Rect(_posBoxVincite[0]
                    , _posBoxVincite[1], _dimBoxVincite[0]
                    , _dimBoxVincite[1]) 
                
        #--- Pulizia di tutto il rigone fino al Logo     
        #if not self._flgBlink:
        #    _dimLogo = self._getDimLogo()
        #    _clearRect = pygame.Rect(0,_posBoxVincite[1], self._width - _dimLogo[0], int(15 * _risCoeff) * 2)
        #    pygame.draw.rect(self._SCREEN, CONST.KCOL_NERO, _clearRect, 0)

        #pygame.draw.rect(self._SCREEN
        #                            , CONST.KCOL_NERO 
        #                            , (_posBoxVincite[0]
        #                               , _posBoxVincite[1]
        #                               , _dimBoxVincite[0]*1.10
        #                               , _dimBoxVincite[1]*1.10)
        #                            ,0 )
        #self._RettArrot.drawRoundRect(self._SCREEN
        #            , CONST.KCOL_NERO , _rectVincite, 0
        #            , _dimBoxVincite[2], _dimBoxVincite[3])
        #            
        #--- QUATERNA
        _colore = CONST.KCOL_NERO # nessuna vincita
        if self._quaternaOK == 0:  # vincita eseguita
            _colore = CONST.KCOL_ROSSO 
        elif self._quaternaOK == 1: # vincita in controllo
            if self._flgBlink:
                _colore = CONST.KCOL_GIALLO 
            else:
                _colore = CONST.KCOL_ROSSO 
        self._DisegnaCerchio.disegna(self._SCREEN, _colore, _dimBoxVincite[3], int(_posVincite[0] - _dimBoxVincite[3] * 1.25), int(_rectVincite[1] + _dimBoxVincite[3]*0.90), 0)
        _textSurfaceObj = _fontObj.render('Quaterna', True
                    , CONST.KCOL_VERDE, CONST.KCOL_NERO)
        self._SCREEN.blit(_textSurfaceObj
                    , (_posVincite[0], _posVincite[1]))
        #--- Calcolo posizione X successiva (BOX e Dicitura)
        _rectTextSurfaceObj = _textSurfaceObj.get_rect()
        _posBoxVincite[0] =  _posVincite[0] + _rectTextSurfaceObj.width \
                                        + int(_dimBoxVincite[0] * 0.50) 
        _posVincite[0] = _posBoxVincite[0]  + _dimBoxVincite[0] * 3.50 
        #--- CINQUINA
        _rectVincite = pygame.Rect(_posBoxVincite[0]
                    , _posBoxVincite[1], _dimBoxVincite[0]
                    , _dimBoxVincite[1]) 
        self._RettArrot.drawRoundRect(self._SCREEN, CONST.KCOL_NERO 
                    , _rectVincite, 0, _dimBoxVincite[2]
                    , _dimBoxVincite[3])
        _colore = CONST.KCOL_NERO # nessuna vincita
        if self._cinquinaOK == 0:  # vincita eseguita
            _colore = CONST.KCOL_ROSSO 
        elif self._cinquinaOK == 1: # vincita in controllo
            if self._flgBlink:
                _colore = CONST.KCOL_GIALLO 
            else:
                _colore = CONST.KCOL_ROSSO 
        self._DisegnaCerchio.disegna(self._SCREEN, _colore, _dimBoxVincite[3], int(_posVincite[0] - _dimBoxVincite[3] * 1.25), int(_rectVincite[1] + _dimBoxVincite[3]*0.90), 0)
        _textSurfaceObj = _fontObj.render('Cinquina', True
                    , CONST.KCOL_VERDE, CONST.KCOL_NERO)
        self._SCREEN.blit(_textSurfaceObj
                    , (_posVincite[0], _posVincite[1]))
        #--- Calcolo posizione X successiva (BOX e Dicitura)
        _rectTextSurfaceObj = _textSurfaceObj.get_rect()
        _posBoxVincite[0] =  _posVincite[0] + _rectTextSurfaceObj.width \
                                        + int(_dimBoxVincite[0] * 0.50) 
        _posVincite[0] = _posBoxVincite[0]  + _dimBoxVincite[0] * 3.50 
        #--- DECINA
        _rectVincite = pygame.Rect(_posBoxVincite[0]
                    , _posBoxVincite[1], _dimBoxVincite[0]
                    , _dimBoxVincite[1]) 
        self._RettArrot.drawRoundRect(self._SCREEN, CONST.KCOL_NERO 
                    , _rectVincite, 0, _dimBoxVincite[2]
                    , _dimBoxVincite[3])
        _colore = CONST.KCOL_NERO # colore di nessuna vincita (default)
        if self._decinaOK == 0:  # vincita eseguita
            _colore = CONST.KCOL_ROSSO 
        elif self._decinaOK == 1: # vincita in controllo
            if self._flgBlink:
                _colore = CONST.KCOL_GIALLO 
            else:
                _colore = CONST.KCOL_ROSSO 
        self._DisegnaCerchio.disegna(self._SCREEN, _colore, _dimBoxVincite[3], int(_posVincite[0] - _dimBoxVincite[3] * 1.25), int(_rectVincite[1] + _dimBoxVincite[3]*0.90), 0)
        _textSurfaceObj = _fontObj.render('Decina', True
                    , CONST.KCOL_VERDE, CONST.KCOL_NERO)
        self._SCREEN.blit(_textSurfaceObj
                    , (_posVincite[0], _posVincite[1]))
        #--- Calcolo posizione X successiva (BOX e Dicitura)
        _rectTextSurfaceObj = _textSurfaceObj.get_rect()
        _posBoxVincite[0] =  _posVincite[0] + _rectTextSurfaceObj.width \
                                        + int(_dimBoxVincite[0] * 0.50) 
        _posVincite[0] = _posBoxVincite[0]  + _dimBoxVincite[0] * 4.50 
        #--- TOMBOLA
        _rectVincite = pygame.Rect(_posBoxVincite[0]
                                , _posBoxVincite[1], _dimBoxVincite[0]
                                , _dimBoxVincite[1]) 
        #self._RettArrot.drawRoundRect(self._SCREEN, CONST.KCOL_NERO 
        #                        , (_rectVincite[0], _rectVincite[1]
        #                        , _rectVincite[2]*1.10, _rectVincite[3]*1.10)
        #                        , 0, _dimBoxVincite[2]
        #                        , _dimBoxVincite[3])
        self._RettArrot.drawRoundRect(self._SCREEN, CONST.KCOL_NERO
                                      , _rectVincite, 0, _dimBoxVincite[2]
                                      , _dimBoxVincite[3])
        _colore = CONST.KCOL_NERO # nessuna vincita
        if self._tombolaOK == 0:  # vincita eseguita
            _colore = CONST.KCOL_ROSSO 
        elif self._tombolaOK == 1: # vincita in controllo
            if self._flgBlink:
                _colore = CONST.KCOL_GIALLO 
            else:
                _colore = CONST.KCOL_ROSSO 
        self._DisegnaCerchio.disegna(self._SCREEN, _colore, _dimBoxVincite[3], int(_posVincite[0] - _dimBoxVincite[3] * 1.25), int(_rectVincite[1] + _dimBoxVincite[3]*0.90), 0)
        _textSurfaceObj = _fontObj.render('TOMBOLA', True
                    , CONST.KCOL_VERDE, CONST.KCOL_NERO)
        self._SCREEN.blit(_textSurfaceObj
                    , (_posVincite[0], _posVincite[1]))
        # inverte il flag di lampeggio
        self._refreshFlgBlink()
        #self._flgBlink = not self._flgBlink  


    def on_scriveNumeroUscito(self, a_numeroUscito): 
        """ Espone l'ultimo Numero Uscito """
        #--- dicitura 'Numero Uscito' -------------------------------------------------
        _fontObj = pygame.font.Font('freesansbold.ttf'
                                , self._dimFont['fontNumeriUsciti'])
        _dicitSurfaceObj = _fontObj.render('Numero Uscito'
                    , True, CONST.KCOL_VERDE, CONST.KCOL_NERO)
        _dicitRectObj = _dicitSurfaceObj.get_rect()
       #--- pos dicitura Numero Uscito 
        _dicitPos = [self._rectBoxNumUscito[0]
                                    + self._rectBoxNumUscito[2] /2
                                   , self._rectBoxNumUscito.top 
                                    + _dicitRectObj[3]]
        _dicitRectObj.center = _dicitPos
        #--- Il numero  #'freesansbold.ttf', 60) -------------------------------
        _fontObj = pygame.font.Font('courbd.ttf'
                                            ,self._dimFont["fontNumeroUscito"]) 
        #--- Area del numero uscito
        _numSurfaceObj = _fontObj.render('{0:02}'.format(a_numeroUscito) 
                            , True, CONST.KCOL_GIALLO, CONST.KCOL_NERO)
        _textRectObj = _numSurfaceObj.get_rect()
        _numPos = [self._rectBoxNumUscito[0]
                                    + (self._rectBoxNumUscito[2] 
                                        - _textRectObj.width) /2
                                   , self._posTabellone[1] 
                                    + (self._rectBoxNumUscito[3] 
                                        - _textRectObj.height) /10
                                    + _dicitRectObj[3]
                                    ]
        #--- Pulizia del numero precedente
        _numSurfaceObjPulizia = _fontObj.render('   ' 
                            , True, CONST.KCOL_GIALLO, CONST.KCOL_NERO)
        _textRectObjPulizia = _numSurfaceObjPulizia.get_rect()
        _numPosPulizia = [self._rectBoxNumUscito[0]
                                    + (self._rectBoxNumUscito[2] 
                                        - _textRectObjPulizia.width) /2
                                   , self._posTabellone[1] 
                                    + (self._rectBoxNumUscito[3] 
                                        - _textRectObjPulizia.height) /10
                                    + _dicitRectObj[3]
                                    ]
        #--- Pulizia (rettangolo riempito a nero ZERO finale significa pieno e no bordato)
        pygame.draw.rect(self._SCREEN
                                    , CONST.KCOL_NERO 
                                    ,(self._rectBoxNumUscito[0] * 1.05, _numPosPulizia[1]
                                    , self._rectBoxNumUscito[2] * 0.90, _dicitRectObj[3])
                                    , 0 )
        self._SCREEN.blit(_numSurfaceObjPulizia, (_numPosPulizia[0] , _numPosPulizia[1])) 

        #self._SCREEN.blit(_numClrSurfaceObj
        #                        , (_numPos[0] , _numPos[1])) 
        #--- espone il numero se maggiore di zero
        if a_numeroUscito > 0:
            self._SCREEN.blit(_numSurfaceObj, (_numPos[0] , _numPos[1])) 
        self._SCREEN.blit(_dicitSurfaceObj, _dicitRectObj)

    
    def on_scriveUltimiNumeriUsciti(self, utlimiNumeriUsciti):
        """ Espone SOLO gli ultimi  Numeri Usciti """
        _numDaEsporre = 6
 
        _risCoeffX = self._Config.risCoeffX
        _risCoeffY = self._Config.risCoeffY
        _rectDicitNumTrarrUsciti = [int(self._rectBoxNumUscito[0]
                                                    + (self._rectBoxNumUscito[2] 
                                                         - (_numDaEsporre * 6 * _risCoeffX)))
                                                , int(self._rectBoxNumUscito[1] 
                                                    + self._rectBoxNumUscito[3] 
                                                    - (45 * _risCoeffY))
                                                , int(self._dimFont["fontNumeriUsciti"] * 2.5 * _risCoeffX)  
                                                , int(22 * _risCoeffX)
                                                , int(37 * _risCoeffX)]
        _posX = _rectDicitNumTrarrUsciti[0]  
        _posY = _rectDicitNumTrarrUsciti[1]
        if len(utlimiNumeriUsciti) < _numDaEsporre:
            _numDaEsporre = len(utlimiNumeriUsciti) 
        
        _fontObj = pygame.font.Font('courbd.ttf'
                                , self._dimFont["fontNumeriUsciti"])
        _textSurfaceObj = _fontObj.render(
                    '{0:02}.'.format(99), True
                    , CONST.KCOL_NERO, CONST.KCOL_NERO)
        _rectSurfaceObj = _textSurfaceObj.get_rect() 
            
        #--- Pulizia (rettangolo riempito a nero ZERO finale significa piento e no bordato)
        pygame.draw.rect(self._SCREEN
                                    , CONST.KCOL_NERO 
                                    , (self._rectBoxNumUscito[0] * 1.02, _posY -7
                                    , self._rectBoxNumUscito[2] * 0.90, _rectSurfaceObj.height+7)
                                    ,0 )
        #_fontObj = pygame.font.Font('courbd.ttf'
        #                        , self._dimFont["fontNumeriUsciti"])
        #_textSurfaceObj = _fontObj.render(
        #            '{0:02}.'.format(99), True
        #            , CONST.KCOL_NERO, CONST.KCOL_NERO)
        #_rectSurfaceObj = _textSurfaceObj.get_rect() 
        #_posClearX = _posX 
        #_tot = _numDaEsporre - 1
        #for _ctr in range (_tot):
        #    _posClearX -= _rectDicitNumTrarrUsciti[3]
        #    self._SCREEN.blit(_textSurfaceObj, (_posClearX, _posY -7))
        _posX -= _rectSurfaceObj.width * 1.10
        #print ('utlimiNumeriUsciti :',  utlimiNumeriUsciti)
        # non voglio veder l'ultimo "numero uscito" in questo elenco
        _tot = _numDaEsporre - 1
        for _ctr in range (_tot):
            _numero = utlimiNumeriUsciti[_ctr +1]
            # dal secondo giro in poi mette 'trattino' e 'numero'
            if _ctr != 0:  
                _textSurfaceObj = _fontObj.render(
                            '{0:02}.'.format(_numero), True
                            , CONST.KCOL_GIALLO, CONST.KCOL_NERO)
            else:
                _textSurfaceObj = _fontObj.render(
                            '{0:02}'.format(_numero), True
                            , CONST.KCOL_GIALLO, CONST.KCOL_NERO)
            self._SCREEN.blit(_textSurfaceObj, (_posX, _posY -7))
            _posX -= _rectSurfaceObj.width * 1.10


    def on_scriveStatoTombola(self, a_statoDesc=''): 
        """ Espone la dicitura dello Stato del Gioco """
        #--- dicitura
        if a_statoDesc == None:
            a_statoDesc = ' '
        _fontObj = pygame.font.Font('serpents.ttf'
                                        , self._dimFont["fontStato"])
        _textSurfaceObj = _fontObj.render( 
                                '{:<18}'.format(a_statoDesc), True
                                , CONST.KCOL_VERDE, CONST.KCOL_NERO)
        #--- oggetto descrizione Stato
        #print ('DBG on_scriveStatoTombola: ', a_statoDesc)
        _width =  int((self._width - self._dimTabellone[0] - self._posTabellone[0])*0.90)
        #_posDicitStato = [self._posTabellone[0] + int(self._dimTabellone[0] + _width*0.10)
                          #self._posTabellone[1] + int(self._dimTabellone[1]*1.05)]
        _dimLogo = self._getDimLogo()
        _posDicitStato = [int(self._width * 0.85 - (_dimLogo[0]))
                          , int(self._height - (_textSurfaceObj.get_rect().height) *2)] 
        self._SCREEN.blit(_textSurfaceObj, (_posDicitStato[0], _posDicitStato[1]))

        if not self._Config.centone:
            self.on_disegnaLogo() #--- espone il LOGO


    def on_scriveNomePartita(self, nomeGioco='', a_nomePNG=''
                                                 , startDataOra=''): 
        """ Espone riquadro con immagine della partita """
        print ('DBG on_scriveNomePartita ')
        #--- dicitura nome gioco
        #_fontObj = pygame.font.Font('freesansbold.ttf'
        _fontObj = pygame.font.Font('serpents.ttf'
                                    , self._dimFont["fontDicitGioco"])
        #_textSurfaceObj = _fontObj.render('  ' , True, CONST.KCOL_NERO
        #                                           , CONST.KCOL_NERO)
        #--- largezza del box
        _width =  self._rectBoxNumUscito[2] * 0.96
        _height =  _width  / 16*9 # box a dimensione 16:9 come il TV 
        #--- box dell'immagine
        _rectBoxNomeGioco = pygame.Rect(self._posTabellone[0]  
                                                   + self._dimTabellone[0] 
                                                   + int(_width *0.02)
                                                , self._rectBoxNumUscito[1] 
                                                   + self._rectBoxNumUscito[3] 
                                                   + int(_height *0.05)
                                            , _width
                                            , _height)
        #--- box pulizia prima di fare l'immagine
        _rectClrBoxNomeGioco = _rectBoxNomeGioco
        #_rectClrBoxNomeGioco[2] = self._dimTabellone[0] - self._posTabellone[0]
        pygame.draw.rect( self._SCREEN,  CONST.KCOL_NERO,  _rectClrBoxNomeGioco)
 
        #--- immagine + box
        #        try:
        _pngImgload = pygame.image.load(
                      os.path.join(CONST.KPATH_IMG, a_nomePNG)).convert_alpha()
        #        except pygame.error, pygame.message:
        #            print 'Immagine non caricata. File:', nomePNG
        #            raise SystemExit, message        

        #--- pulizia dello spazio per l'immagine
        #self._RettArrot.drawRoundRect(self._SCREEN, CONST.KCOL_NERO
        #                , _rectBoxNomeGioco, 0 , 10
        #                , 10) 
        #--- scala l'immagine 
        #_imgSurfaceObj = self.on_aspectScale(_pngImgload
        #                , (_rectBoxNomeGioco[2] * 0.96
        #                 , _rectBoxNomeGioco[3] * 0.96))
        _imgSurfaceObj = pygame.transform.scale(_pngImgload
                        , (int(_rectBoxNomeGioco[2] * 0.96)
                         , int(_rectBoxNomeGioco[3] * 0.92)))
        #--- box 
        _rectBox = _rectBoxNomeGioco
        #_rectBox.width = int(_imgSurfaceObj.get_width() * 1)
        self._RettArrot.drawRoundRect(self._SCREEN, CONST.KCOL_BLU
                            , _rectBox
                            , 0 , 10, 10)
        #--- blit dell'immagine 
        self._SCREEN.blit(_imgSurfaceObj
                    , (_rectBoxNomeGioco[0] + int((_rectBoxNomeGioco[2] - _imgSurfaceObj.get_width()) /2)
                    , _rectBoxNomeGioco[1] + int((_rectBoxNomeGioco[3] - _imgSurfaceObj.get_height()) /2)))
        #--- Nome gioco in sovrapposizione dell'immagine
        _textSurfaceObj = _fontObj.render('{}'.format(nomeGioco) \
                                    , True, CONST.KCOL_BIANCO, CONST.KCOL_TXT_TRAPARENTE)
        _rectTextSurfaceObj = _textSurfaceObj.get_rect()
        self._SCREEN.blit(_textSurfaceObj   
                    , (_rectBoxNomeGioco[0] 
                    + int(_rectBoxNomeGioco[2] - _rectTextSurfaceObj.width * 1.35)
                    , _rectBoxNomeGioco[1] 
                    + int(_rectBoxNomeGioco[3]  - _rectTextSurfaceObj.height * 1.20)))
        

    def on_aspectScale(self, a_img, _dimPNG):
        """ Scala 'img' x essere contenuto in un box bx/by. 
        Mantiene l'aspetto originale senza distorsioni """
        ix,iy = a_img.get_size()
        if ix > iy:
            # fit to width
            scale_factor = _dimPNG[0]/float(ix)
            sy = scale_factor * iy
            if sy > _dimPNG[1]:
                scale_factor = _dimPNG[1]/float(iy)
                sx = scale_factor * ix
                sy = _dimPNG[1]
            else:
                sx = _dimPNG[0]
        else:
            # fit to height
            scale_factor = _dimPNG[1]/float(iy)
            sx = scale_factor * ix
            if sx > _dimPNG[0]:
                scale_factor = _dimPNG[0]/float(ix)
                sx = _dimPNG[0]
                sy = scale_factor * iy
            else:
                sy = _dimPNG[1]
    
        return pygame.transform.scale(a_img, (int(sx),int(sy)))


    def _refreshFlgBlink(self):
        """cambia il flag per fare il lampeggio"""
        _temp = self._cur_time
        self._cur_time = time.time()
        _elapsed_time = self._cur_time - self._prev_time
        #print('DBG _refreshFlgBlink _elapsed_time:', _elapsed_time)
        if _elapsed_time > 0.7:  # superato tot secondi inverte il flag
            self._flgBlink = not self._flgBlink  # inverte il flag di lampeggio
            self._prev_time = _temp
        
