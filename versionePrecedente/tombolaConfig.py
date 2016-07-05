'''
Created on 04/gen/2013

@author: alberto
'''
#!/usr/bin/env python
#-*- coding: latin-1 -*-
import  pygame, os
from tombolaLog import *


#--- definizione delle COSTANTI
class COSTANTI(object):
    KTASTO_NUOVO_GIOCO = 210 #101
    KTASTO_CENTONE = 201
    KTASTO_QUATERNA = 202 #104
    KTASTO_CINQUINA = 203 #105
    KTASTO_DECINA = 204 #106
    KTASTO_TOMBOLA = 205 #110
    KTASTO_PAUSA = 211
    KTASTO_EXIT = 250 #199
    KTASTO_IMG = 230 #200
    KTASTO_TABFULL = 231 #tabellone espanso su tutto lo spazio on/off
    KCOL_TRASPARENTE=(255, 255, 255, 255)
    KCOL_BIANCO=(255, 255, 255)
    KCOL_NERO=(0,0,0)
    KCOL_GRIGIO=(128,128,128)
    KCOL_ACQUA=(0,255,255)
    KCOL_BLU=(0,0,255)
    KCOL_VERDE=(0,255,0)
    KCOL_ROSSO=(255,0,0)
    KCOL_GIALLO=(255,255,0)
    KCOL_TXT_TRAPARENTE= None
    KPATH_IMG = 'img'
    KPATH_PUB = 'pubblica'
    KPATH_JOB = 'job'

    def __setattr__(self, *_):
        pass

global CONST
CONST = COSTANTI()

class Config:
    """ Configurazione di alcuni campi della Tombola 
    Per prima cosa impostare il tipo di Risoluzione dello schermo 
    ad esempio:  config.risoluzVideo(0) """

    def __init__(self):
        pygame.init()
        self.__risBaseX = 1280
        self.__risBaseY= 800 
        self.__risCoeffX = 0
        self.__risCoeffY = 0
        self.__risCoeff = 0
        self.__risoluzVideo = [0, 0]
        self.__tipoDisplay = 'F'
        self.__dimFont = {}
        self.__posPrimaDicitVincite = [0, 0]
        self.__posPrimaBoxVincite = [0, 0]
        self.__posPrimaBoxNumUscito = [0, 0]
        self.__posDicitNumTrattUsciti = [0, 0]
        self.__posPrimaDicitNumTrattUsciti = [0, 0]
        self.numMaxTombola = 90 


    def setDimFont(self, a_tabTabelloneFullScreen=False):
        """dim del Font (dim base x una ris di 1280*800)""" 
        _risCoeff = self.__risCoeff
        print ('DBG setDimFont _risCoeff', _risCoeff)
        if _risCoeff < 0.5:     # es. 800x600 (0,47)
            if a_tabTabelloneFullScreen:
                self.__dimFont["fontNumero"]=48
            else:
                self.__dimFont["fontNumero"]=34
            self.__dimFont["fontNumeroUscito"]=200
            self.__dimFont["fontNumeriUsciti"]=28
            self.__dimFont["fontVincite"]=22
            self.__dimFont["fontStato"]=10
            self.__dimFont["fontDicitGioco"]=12
        elif _risCoeff < 1.0:     # es. 1024x768 (0, 77)
            if a_tabTabelloneFullScreen:
                self.__dimFont["fontNumero"]=64
            else:
                self.__dimFont["fontNumero"]=48 #30
            self.__dimFont["fontNumeroUscito"]=200
            self.__dimFont["fontNumeriUsciti"]=32
            self.__dimFont["fontVincite"]=24
            self.__dimFont["fontStato"]=14
            self.__dimFont["fontDicitGioco"]=16
        elif _risCoeff < 1.5: # es 1440x900
            if a_tabTabelloneFullScreen:
                self.__dimFont["fontNumero"]=80
            else:
                self.__dimFont["fontNumero"]=60# 46
            self.__dimFont["fontNumeroUscito"]=220
            self.__dimFont["fontNumeriUsciti"]=38
            self.__dimFont["fontVincite"]=30
            self.__dimFont["fontStato"]=20 
            self.__dimFont["fontDicitGioco"]=22
        elif _risCoeff < 2.0:     # es 1920x1080 (1,92)
            if a_tabTabelloneFullScreen:
                self.__dimFont["fontNumero"]=88
            else:
                self.__dimFont["fontNumero"]=70 #52
            self.__dimFont["fontNumeroUscito"]=240
            self.__dimFont["fontNumeriUsciti"]=42
            self.__dimFont["fontVincite"]=34
            self.__dimFont["fontStato"]=24
            self.__dimFont["fontDicitGioco"]=26
        else:   
            if a_tabTabelloneFullScreen:
                self.__dimFont["fontNumero"]=96
            else:
                self.__dimFont["fontNumero"]=80 #56
            self.__dimFont["fontNumeroUscito"]=260
            self.__dimFont["fontNumeriUsciti"]=46
            self.__dimFont["fontVincite"]=38
            self.__dimFont["fontStato"]=28
            self.__dimFont["fontDicitGioco"]=30

        #self.__dimFont["fontDicitNumUscito"]=int(32 * _risCoeff)
        #self.__dimFont["fontNumeriUscitiT"]=int(24 * _risCoeff)
    
    @property
    def risoluzVideo(self):
        return self.__risoluzVideo
        
    @risoluzVideo.setter    
    def risoluzVideo(self, a_risoluzVideo=[0, 0]):
        if a_risoluzVideo[0] == 0:
            #--- imposta risoluzione di default supportata a 32bit
            _modes = pygame.display.list_modes(32) 
            self.__risoluzVideo = _modes[0]  
        else:
            self.__risoluzVideo = a_risoluzVideo[0],  a_risoluzVideo[1]
        #--- Imposta Coeff di proporzione video
        self.__risCoeffX = self.risoluzVideo[0] / self.__risBaseX
        self.__risCoeffY = self.risoluzVideo[1] / self.__risBaseY
        self.__risCoeff = self.__risCoeffX * self.__risCoeffY
        ilog.stampa('risoluzVideo Coeff x,y: ',  self.__risCoeffX,  self.__risCoeffY)
        #--- In base al Coeff imposta anche la dim dei font
        #self.__setDimFont()

    @property 
    def risCoeff(self):
        return self.__risCoeffX * self.__risCoeffY
        
    @property 
    def risCoeffX(self):
        return self.__risCoeffX 
        
    @property 
    def risCoeffY(self):
        return self.__risCoeffY 
 
    @property 
    def allMyRisoluzVideo(self):
        _modes = pygame.display.list_modes() # modi a 32bit
        return _modes
          
    @property 
    def tipoDisplay(self):
        return self.__tipoDisplay
    @tipoDisplay.setter    
    def tipoDisplay(self, a_tipoDisplay='F'):
        self.__tipoDisplay = a_tipoDisplay
    
    @property 
    def dimFont(self):
        """dim del Font (dim base x una ris di 1280*800)""" 
        return self.__dimFont
        
   
    @property 
    def dimPubblicazioneIMG(self):
        _dimSchermo = []
        _dimSchermo = self.risoluzVideo
        _risCoeff = self.__risCoeff
        return [int(_dimSchermo[0]), int(_dimSchermo[1])
                , int(10 * _risCoeff), int(10 * _risCoeff)]

    def set_modeVideo(self):
        """Ininitializes a new pygame screen using the framebuffer"""
        try:
            _size = [0, 0]
            pygame.init()
            # Based on "Python GUI in Linux frame buffer"
            # http://www.karoltomala.com/blog/?p=679
            disp_no = os.getenv("DISPLAY")
            if disp_no:
                ilog.stampa('Sto girando sotto server X display = ' \
                        , [disp_no])
                os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
            else:
                # Check which frame buffer drivers are available
                # Start with fbcon since directfb 
                #       hangs with composite output
                drivers = ['fbcon', 'directfb', 'svgalib']
                found = False
                for driver in drivers:
                    # Make sure that SDL_VIDEODRIVER is set
                    if not os.getenv('SDL_VIDEODRIVER'):
                        os.putenv('SDL_VIDEODRIVER', driver)
                        ilog.stampa('Driver: SDL_VIDEODRIVER: ' \
                                   , [driver])
                    try:
                        pygame.display.init()
                    except pygame.error:
                        ilog.stampa('Driver non trovato in elenco: ' \
                                    , [driver])      
                        continue
                    found = True
                    break
            
                if not found:
                    #raise Exception( \
                    # 'Nessun driver video accettabile trovato!')
                    ilog.stampa( \
                        'Nessun driver video accettabile trovato! '\
                        , ['ERRORE'])
                
            _x, _y = self.risoluzVideo[0],  self.risoluzVideo[1]  
            _size = self.width, self.height = int(_x), int(_y) # es. 1280, 768
            ilog.stampa('Risoluzione pre-impostazione: ' 
                                ,  (pygame.display.Info().current_w, 
                                     pygame.display.Info().current_h))
            
            """if self._tipoDisplay == 'F':
                _SCREEN = pygame.display.set_mode(_size) 
            elif self._tipoDisplay == 'N':
                _SCREEN = pygame.display.set_mode(_size, pygame.NOFRAME)
            else:
              _SCREEN = pygame.display.set_mode(_size, pygame.RESIZABLE) 

            # = (pygame.display.Info().current_w
                    , pygame.display.Info().current_h)
            #print('Risoluzione impostata: '
                   , _size, end='.\n', file=_fileLOG); _fileLOG.flush()
            pygame.display.update()

            self._clock = pygame.time.Clock()
            pygame.mouse.set_visible(False)               
            """
            #os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
        except:
            print ('errore in impostazione Risoluzione Video: ', _size ) 
            raise

        finally:
            pass
        
        return _size

    def setCentone(self):
        """Attiva/Disattiva gioco con il CENTONE"""
        if self.numMaxTombola == 90:
            self.numMaxTombola = 100
        else:
            self.numMaxTombola = 90

    @property
    def centone(self):
        if self.numMaxTombola == 90:
            return False
        else:
            return True

    def fileExists(self,  filename):
        try:
            with open(filename) as f:
                return True
        except IOError:
            return False
    
"""   pos_x = screen_width / 2 - window_width / 2
    pos_y = screen_height - window_height
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (pos_x,pos_y)
    os.environ['SDL_VIDEO_CENTERED'] = '0'
"""
