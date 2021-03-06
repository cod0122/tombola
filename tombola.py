#!/usr/bin/env python
#-*- coding: latin-1 -*-
try:
    from time import gmtime, strftime
    from tombolaLog import *
    from tombolaConfig import * 
    #import shelve
    #import cPickle as pickle
    import pickle
    import random
except ImportError as message:
    print("Impossibile caricare il modulo. {0}".format(message))
    raise SystemExit


class FileBMP():
    """ gestione file BMP """

    def __init__(self, a_cartella='.'):
        self.icartella = a_cartella 
        self.itipoFile = ('.png', '.bmp','.jpg','gif','tif')

    def getListFileBMP(self):
        lfileBMP = []
        lidx = 0
        for file in os.listdir(self.icartella):
            ilog.stampa('DBG getFilePNG file: ', [file])
            #print ('DBG getFilePNG file: ', file)
            if file.endswith(self.itipoFile):
                lfileBMP.insert(lidx, file)
                lidx = lidx + 1
        return lfileBMP            


class Tombola():
    """Gestione tombola """

    def __init__(self):
        """a_nome = nome gioco tombola"""   
        # Cambiare la versione se cambia l'oggetto!!!!!!!!!!!
        self.versione='1.8'  
        self._nomeGioco=''
        self._startDataOra=''
        self._progressivoUtlimo=0
        self._ultimoNumero=0
        self._numeriTombola = dict()
        self._statoTombola=0
        #--- Carica File dei Nomi Partita 
        self._caricaNomiFileGioco()

        """self._idNomiGioco = {'1':'antilope','2':'aquila','3':'cervo'
                             ,'4':'cinciallegra','5':'corvo' 
                             ,'6':'fenicottero','7':'gorilla','8':'lupo'
                             ,'9':'pulcinella di mare'
                             ,'10':'rana','11':'riccio'
                             ,'12':'tartaruga'
                             ,'13':'topo'
                             ,'14':'upupa'
                             ,'15':'tombola'}
        self._nomiGioco = {'antilope':'antilope.png'
                            ,'aquila':'aquila.png','cervo':'cervo.png'
                            ,'cinciallegra':'cinciallegra.png'
                            ,'corvo':'corvo.png' 
                            ,'fenicottero':'fenicottero.png'
                            ,'gorilla':'gorilla.png','lupo':'lupo.png'
                            ,'pulcinella di mare':'pulcinelladimare.png'
                            ,'rana':'rana.png','riccio':'riccio.png'
                            ,'tartaruga':'tartaruga.png'
                            ,'topo':'topo.png'
                            ,'upupa':'upupa.png'
                            ,'tombola':('tombola.png', 'tombola.bmp'
                                              , 'tombola.jpg', 'tombola.tif', 'tombola.gif')}"""

    def startNuovaTombola(self):
        """Inizio nuova Tombola"""
        #--- cerca nome di default 'tombola....' con eventuale info personalizzata
        self._idNomeGioco = self.getIdNomeGioco()
        self._nomeGioco =  self._nomiGioco[self._idNomeGioco]
        self.startTombola(self._nomeGioco)

    def startTombola(self, a_nomeGioco=''):
        """lancio tombola """
        if a_nomeGioco=='':
            if self._nomeGioco == '':
                self.startNuovaTombola()  #occhio e' ricursiva
                return
        self._idNomeGioco = self.getIdNomeGioco(self._nomeGioco)
        self._setStartDataOra()
        self._inizializza()

    def _inizializza(self):
        """inizializza il tabellone (tutti i 90/100 numeri della tombola)"""
        self._progressivoUtlimo = 0
        self._numeriTombola.clear()
        self._ultimoNumero=0
        self._statoTombola=1 # 1=inizio gioco

    def _caricaNomiFileGioco(self):
        #--- Carica File dei Nomi Partita 
        self._FileBMP = FileBMP(CONST.KPATH_IMG)
        self._NomiFileGioco = self._FileBMP.getListFileBMP() #elenco dei file bmp
        self._nomiGioco = [str(nomeFile[:-4]) for nomeFile in self._NomiFileGioco]
        self._idNomeGioco = 0

    def setNumeroUscito(self, a_numero):
        """riceve il numero da operatore"""
        # controlla se il nr esiste gia'
        if not (self.ifNumeroUscito(a_numero)):  
            self._progressivoUtlimo += 1
            self._numeriTombola[a_numero] = self._progressivoUtlimo
            self._setUltimoNumero(a_numero)
            self._numeriTombola = self.resetNegativi(0
                                        , self._numeriTombola)
        else: #mette / toglie  numero in bilico (=negativo) 
            l_numero = 0
            l_returnList = list()
            self._numeriTombola[a_numero] *= -1
            # recupera il penultimo numero uscito 
            l_returnList = self.getUltimiNumeri(1)
            if len(l_returnList) > 0:
                l_numero = l_returnList[0]
            self._setUltimoNumero(l_numero)

    def resetNegativi(self, a_numero=0, numeriTombola={0:0}):
        """pone a ZERO tutti i numeri 'in bilico' ovvero i negativi"""
        retNumeriTombola = dict()
        if a_numero == 0:
            retNumeriTombola = ({chiave:valore for chiave
                    , valore in numeriTombola.items() if valore > 0})  
        else:
            retNumeriTombola[a_numero] = 0
        return retNumeriTombola

    def resetNumero(self, a_numero=0):
        """Inizializza il numero indicato a zero"""
        if a_numero == 0:
            pass
        else: 
            self._numeriTombola[a_numero] = 0

    def getUltimiNumeri(self, a_ultimiNumeri=1):
        """torna un list con gli ultimi numeri usciti x default 
        torna l'ultimo, se ZERO torna tutti i numeri"""
        l_returnList = list()
        l_numeriOrdList = list()
        l_range = 0

        # Torna tutti i numeri Ordinati dall'ultima uscita 
        #                           inditero fino al primo uscito
        l_numeriOrdList = self._ordinaDizionarioXvalore(
                                                self._numeriTombola)  
        #Se richiesti + num di quelli usciti oppure Richiedo TUTTO 
        if a_ultimiNumeri > len(l_numeriOrdList) or a_ultimiNumeri == 0:
            l_range = len(l_numeriOrdList)
        else:
            l_range = a_ultimiNumeri
        # estrae solo quelli che servono
        l_returnList = l_numeriOrdList[:l_range]  

        return l_returnList[:]

    def _ordinaDizionarioXvalore(self, a_dizionario):
        l_returnList = list() 
        l_sortList = list() 
        l_numeriTombola_vk = dict()
        # inverte valore e chiave: la pos di uscita diventa la chiave
        l_numeriTombola_vk = {valore:chiave for chiave, valore 
                        in self._numeriTombola.items() if valore > 0} 
        # mette le chiavi in una lista (le posizioni di uscita)
        #     devo fare il cast in LIST altrimenti lo considera un DICT
        l_sortList = list(l_numeriTombola_vk.keys()) 
        l_sortList.sort()  # ordine la posizioni di uscita (crescente)
        if len(l_sortList) > 1: 
            # sort inverso dell'uscita dei NUMERI (ordine decrescente) 
            l_sortList.reverse()  
        for ind in l_sortList:
            # metto i NUMERI usciti nel LIST 
            l_returnList.append(l_numeriTombola_vk[ind])   

        return l_returnList

    def ifNumeroUscito(self, a_numero):
        """verifica se il numero e' uscito ed esposto (>0) 
        oppure appena rimosso (<0)"""
        if self._numeriTombola.get(a_numero, 0) == 0:
            return False 
        else:
            return True

    def _setUltimoNumero(self, a_numero):
        self._ultimoNumero = a_numero
        #dbgprint("ULTIMO NUMERO:", self._ultimoNumero)

    def _setStartDataOra(self):
        self._startDataOra=strftime(" %d %b %Y %H:%M ", gmtime())

    def getStartDataOra(self):
        return self._startDataOra

    def getUltimoNumero(self):
        return self._ultimoNumero

    def setStatoTombolaStart(self): #inizia gioco
        self._setStatoTombola(1)
    def setStatoTombolaInput(self): #attende completam input del numero
        self._setStatoTombola(2)
    def setStatoTombolaAttivo(self): #stato normale
        self._setStatoTombola(3)
    #in stallo, ad esempio durante lampeggio quaterna, cinquina, tombola
    def setStatoTombolaCheck(self):
        self._setStatoTombola(4)
    def setStatoTombolaFine(self): #Fine TOMBOLA!
        self._setStatoTombola(5)
    def setStatoTombolaExit(self): #esce dal pgm
        self._setStatoTombola(6)
    def setStatoTombolaPausa(self): #gioco in pausa
        self._setStatoTombola(7)
    def setStatoTombolaImg(self): #gioco in pausa x visualizza immagini
        self._setStatoTombola(8)
    def setStatoTombolaReset(self): #Reset tab x preparare nuovo gioco
        self._setStatoTombola(9)

    def ifStatoTombolaPausa(self): 
        if self._statoTombola == 4 or self._statoTombola == 8:
            return True
        else:
            return False 

    def ifStatoTombolaImg(self): 
        if self._statoTombola == 8:
            return True
        else:
            return False 

    def _setStatoTombola(self, a_stato=1):
        self._statoTombola = a_stato
    def getStatoTombola(self):
        return self._statoTombola

    def getNomeGioco(self):
        if self._nomeGioco == 'tombola':
            return ''
        else:
            return self._nomeGioco

    def getNomeFileGiocoImg(self):
        _nomeFileGioco = self._NomiFileGioco[self._idNomeGioco] # torna il nome file
        if not os.path.isfile(CONST.KPATH_IMG + _nomeFileGioco): # se manca il file
            self._caricaNomiFileGioco() # ricarica tutti i file
            self._idNomeGioco = self.getIdNomeGioco(self._nomeGioco)
            self._nomeGioco =  self._nomiGioco[self._idNomeGioco]
            _nomeFileGioco = self._NomiFileGioco[self._idNomeGioco] # torna il nome file
        return _nomeFileGioco 

    def getIdNomeFileGiocoImg(self, a_idNomeGioco=''):
        return self._NomiFileGioco[a_idNomeGioco]

    def getIdNomeGioco(self, a_nomeGioco='tombola'):
        try:
            __idNomeGioco = self._nomiGioco.index(a_nomeGioco)
        except ValueError:
        #--- altrimenti carica un'immagine random
            __idNomeGioco = random.randrange(1,len(self._nomiGioco)) 
        return __idNomeGioco

    def getStatoTombolaDesc(self):
        if self._statoTombola == 1:
            return 'partiamo?                  '
        elif self._statoTombola == 2:
            return '..attesa numero...    '
        elif self._statoTombola == 3:
            if self.getUltimoNumero() > 0:
                return 'stiamo giocando...    '
            else:
                return 'allora partiamo?        '
        elif self._statoTombola == 4:
            return 'CONTROLLO               '
        elif self._statoTombola == 5:
            return 'fine gioco !               '
        elif self._statoTombola == 6:
            return 'in uscita...               '
        elif self._statoTombola == 7 or self._statoTombola == 8:
            return '   IN  PAUSA             '
        elif self._statoTombola == 9:
            return 'controllo tabellone...  '



class TombolaStato ():
    """Gestione Stato della Tombola """

    def __init__(self):
        try:
            #l_Tombola = Tombola()
            #--- oggetto x salvare lo stato della Tombola
            # shelve.open("tmb_salvata")  
            _shelveTmb = open("tmb_salvata", 'rb') 
            pickle.Unpickler(_shelveTmb)
            #_Pickler = pickle.Unpickler(_shelveTmb)
            #l_Tombola = _Pickler.load()

        except IOError as complaint:
            ilog.stampa('Errore oggetto per salvataggio dello stato: ',  complaint)
            self.resetStato()
        except:
            self.resetStato()

    def salvaStato(self, a_Tombola):
        """Salva lo stato della Tombola"""
        #_shelveTmb = shelve.open("tmb_salvata")  
        # shelve.open("tmb_salvata")  
        _shelveTmb = open("tmb_salvata", 'wb') 
        _Pickler = pickle.Pickler(_shelveTmb)
        _Pickler.dump(a_Tombola)
        _shelveTmb.close()

    def resetStato(self):
        """Resetta lo stato della Tombola"""
        a_Tombola = Tombola()
        #_shelveTmb = shelve.open("tmb_salvata")  
        _shelveTmb = open("tmb_salvata", 'wb') 
        #_shelveTmb["tombola"] = a_Tombola
        #_shelveTmb["versione"] = a_Tombola.versione
        a_Tombola.versione = '0.0'
        _Pickler = pickle.Pickler(_shelveTmb, pickle.HIGHEST_PROTOCOL)
        _Pickler.dump(a_Tombola)
        _shelveTmb.close()

    def ripriStato(self):
        """Ripristina lo stato della Tombola se l'oggetto 
        ha sempre la stessa versione"""
        l_Tombola = Tombola()
        #_shelveTmb = shelve.open("tmb_salvata")  
        _shelveTmb = open("tmb_salvata", 'rb') 
        _Pickler = pickle.Unpickler(_shelveTmb)
        l_Tombola_old = _Pickler.load()
        if l_Tombola.versione == l_Tombola_old.versione: 
            l_Tombola = l_Tombola_old 
            _shelveTmb.close()
        return l_Tombola

