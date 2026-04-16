import os, sys
from PIL import Image
from pathlib import Path  #libreria importata per estrarre facilmente l' estensione del file
import os
from abc import ABC, abstractmethod
import subprocess
import pikepdf
from funzioni import salvaConNome, trova_eseguibile, ottieni_percorso_base




#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

class fileGenerico(ABC):    #classe astratta che gestisce la factory, di questa nel main bisogna chimare solo il metodo statico
    def __init__(self,file_path):
        self.percorso=file_path
        self.nome=os.path.basename(file_path)
        self.dimensioneFile=os.path.getsize(file_path)
    @staticmethod
    def creaDaPercorso(file_path):  
        estensione=Path(file_path).suffix.lower()   #prendo l'estensione
        if estensione in mappaEstensioni:   #controllo se c' è l' estensione, con la mappa ricavo il costruttore e lo chiamo
            costruttore=mappaEstensioni[estensione]
            return costruttore(file_path)
        else:
            print('Estensione non trovata')

    def aggiungiParametriExtra(self,scelta,listaFile=None):   #medoto che di base restituisce un dizionario vuoto, ma dovrà essere sovrascritto dalle classi figlie
        return {}

    @abstractmethod
    def scegliAzione(self,scelta,percorsoCartella,extraParam={}): #costringo le classi figlie a implementarlo
        pass
    @abstractmethod
    def getAzioniDisponibili(self): #costringo le classi figlie a implementarlo
        pass

#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

class filePdf(fileGenerico):        #classe che gestisce i file pdf
    def __init__(self, file_path):
        super().__init__(file_path)
        cartella_script = ottieni_percorso_base()
        percorsi_comuni_gs = [
            os.path.join(cartella_script, "gs", "bin", "gswin64c.exe"),

            r"C:\Program Files\gs\gs*\bin\gswin64c.exe",
            r"C:\Program Files (x86)\gs\gs*\bin\gswin32c.exe"
        ]
        
        self.gs_exe = trova_eseguibile("gswin64c", percorsi_comuni_gs)

    def getAzioniDisponibili(self):
        print('Le azioni disponibili sono: \n')
        print('---->Per convertire il pdf in pdf/A premere 1')
        print('---->Per comprimere il pdf premere 2')
        print('---->Per unire i pdf premere 3')

    def scegliAzione(self,scelta,percorsoCartella='',extraParam={}):
        mappaScelte={
            1 : self._convertiInPDFA,
            2 : self._comprimiPDF, 
            3 : self._unisciPDF
        }   
        if scelta in mappaScelte:
            if extraParam:
                if scelta==2:
                    qualita=extraParam['qualita']
                    if qualita==0:
                        return
                    return mappaScelte[scelta](percorsoCartella=percorsoCartella,qualita=qualita)
            else:
                return mappaScelte[scelta](percorsoCartella=percorsoCartella)
        else:
            print('SCELTA NON GIUSTA')
            return

    def aggiungiParametriExtra(self, scelta,listaFile=None):
        if scelta==2:
            print('Scegli la qualità di compressione: \n')
            print('----->Premere 1 per qualità alta, compressione bassa')
            print('----->Premere 2 per qualità media, compressione media')
            print('----->Premere 3 per qualità bassa, compressione alta')
            qualita=int(input())
            return {'qualita' : qualita}
        elif scelta==3: #qui non si aggiunge parametri extra ma si usa la funzione per chiamarne un altra senza fare il ciclo for del main
            if listaFile:   #serve per quando si passa più file ma se ne vuole solo uno in output, quindi la funzione unisce i file in uno
                self._unisciPDF(listaFile)
                return {'stop' : True}
        else:
            return {}

    def _convertiInPDFA(self,percorsoCartella):
        if percorsoCartella=='': #un file solo
            output_path = salvaConNome(".pdf")
        else:   #gestione di più file
            nomeFile=os.path.basename(self.percorso)
            nomeFileSenzaEstensione=os.path.splitext(nomeFile)[0]
            nomeNuovo=nomeFileSenzaEstensione+'_convertitoInPDFA.pdf'
            output_path=os.path.join(percorsoCartella,nomeNuovo)
        
        if not output_path:
            return
        
        print("Conversione a PDF/A-1b")
        
        try:
            pdf = pikepdf.open(self.percorso)
            
            # Aggiungi metadati XMP per PDF/A-1b
            with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
                meta['pdfaid:part'] = '1'
                meta['pdfaid:conformance'] = 'B'
                meta['dc:format'] = 'application/pdf'
                meta['pdf:Producer'] = 'pikepdf PDF/A Converter'
            
            # Salva con ottimizzazioni
            pdf.save(
                output_path,
                linearize=True,
                compress_streams=True,
                object_stream_mode=pikepdf.ObjectStreamMode.generate
            )
            
            pdf.close()
            
            print(f"PDF/A-1b salvato: {output_path}")
            
        except Exception as e:
            print(f"Errore: {e}")

   
    def _comprimiPDF(self,percorsoCartella,qualita):
        mappaQualita={
            1 : '/prepress',
            2 : '/ebook',
            3 : '/screen'
        }

        if qualita in mappaQualita:
            if percorsoCartella=='': #un file solo
                output_path = salvaConNome(".pdf")
            else:   #gestione di più file
             nomeFile=os.path.basename(self.percorso)
             nomeFileSenzaEstensione=os.path.splitext(nomeFile)[0]
             nomeNuovo=nomeFileSenzaEstensione+'_compresso.pdf'
             output_path=os.path.join(percorsoCartella,nomeNuovo)
        
            if not output_path:
                return
            try:
                comando=[
                    self.gs_exe,
                    '-sDEVICE=pdfwrite',
                    '-dCompatibilityLevel=1.4',
                    f'-dPDFSETTINGS={mappaQualita[qualita]}',
                    '-dNOPAUSE',
                    '-dQUIET',
                    '-dBATCH',
                    f'-sOutputFile={output_path}',
                    self.percorso]
                
                subprocess.run(comando)
                print(f'Il file {os.path.basename(self.percorso)} prima pesava: {(os.path.getsize(self.percorso)/1048576):.3f} MB')
                print(f'Il file convertito {os.path.basename(output_path)} adesso pesa: {(os.path.getsize(output_path)/1048576):.3f} MB')
            except:
                print('Si è verificato un errore riprovare')
        else:
            print('ERRORE RIPROVARE')
            return

    def _unisciPDF(self,percorsiFile=[]):   
        if percorsiFile:
            if len(percorsiFile)<=1:
                print('Seleziona più pdf da unire')
                return
            output_path=salvaConNome('.pdf')
            if not output_path:
                return
            
            try:
                comando = [
                self.gs_exe,
                "-dNOPAUSE",
                "-sDEVICE=pdfwrite",
                f"-sOUTPUTFILE={output_path}",
                "-dBATCH"]
            
                # Aggiungiamo tutti i file di input alla lista del comando
                comando.extend(percorsiFile)
                subprocess.run(comando, check=True, capture_output=True)
                print(f'I pdf sono stati uniti correttamente nel file {os.path.basename(output_path)}')
            except:
                print('ERRORE,riprovare')
            

#######################################################################################################################
#######################################################################################################################      
#######################################################################################################################

class fileImm(fileGenerico):
    def __init__(self, file_path):
        super().__init__(file_path)


    def getAzioniDisponibili(self):
        print('Le azioni disponibili sono: \n')
        print('---->Per convertire l\'immagini in pdf premere 1')
        print('---->Per comprimere l\'immagine premere 2')
        print('---->Per convertire l\'immagine in jpg premere 3')

    def scegliAzione(self,scelta,percorsoCartella='',extraParam={}):
        mappaScelte={
            1 : self._convertiInPDF,
            2 : self._comprimiImmagine,
            3 : self._convertiInJPG
        }   
        if scelta in mappaScelte:
            if extraParam:  #per ora niente parametri extra, qui non si dovrebbe entrare
               return
            else:
                return mappaScelte[scelta](percorsoCartella=percorsoCartella)
        else:
            print('SCELTA NON GIUSTA')
            return

    
    def aggiungiParametriExtra(self,scelta,listaFile=None):
        if scelta==1:       #qui non si aggiunge parametri extra ma si usa la funzione per chiamarne un altra senza fare il ciclo for del main
            if listaFile:   #serve per quando si passa più file ma se ne vuole solo uno in output, quindi la funzione unisce i file in uno
               
                self._convertiInPDF(listaFile)
                return {'stop' : True}
        else:
            return {}

    def _convertiInPDF(self,listaFile=[]):
        if listaFile:
            output_path = salvaConNome('.pdf')
            if not output_path:
                return
            try:
                img1=Image.open(listaFile[0])
                if img1.mode!='RGB':
                    img1=img1.convert('RGB')
                listaAltreImmagini=[]
                for immagine in listaFile[1:]:
                    img_temp=Image.open(immagine)
                    if img_temp.mode!='RGB':
                        img_temp=img_temp.convert('RGB')
                    listaAltreImmagini.append(img_temp)
                img1.save(output_path,'PDF',save_all=True,append_images=listaAltreImmagini)
                print(f'Il file {os.path.basename(output_path)} è stato creato correttamente')
            except Exception as e:
                print(f'Errore nella creazione del pdf {e}')
        else:
            print('ERRORE,riprovare')


    def _comprimiImmagine(self,percorsoCartella):
        estensione=Path(self.percorso).suffix.lower()
        if percorsoCartella=='': #un file solo
            output_path = salvaConNome(estensione)
        else:   #gestione di più file
            nomeFile=os.path.basename(self.percorso)
            nomeFileSenzaEstensione=os.path.splitext(nomeFile)[0]
            nomeNuovo=nomeFileSenzaEstensione+'_compresso'+estensione
            output_path=os.path.join(percorsoCartella,nomeNuovo)
        if not output_path:
            return
        try:
            if estensione in ['.jpg','.jpeg']:
                with Image.open(self.percorso) as img:
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    img.save(output_path, "JPEG", optimize=True, quality=80)
            else:
                with Image.open(self.percorso) as img:
                    img.save(output_path, optimize=True)
            print(f'Il file {os.path.basename(self.percorso)} prima pesava: {(os.path.getsize(self.percorso)/1048576):.3f} MB')
            print(f'Il file convertito {os.path.basename(output_path)} adesso pesa: {(os.path.getsize(output_path)/1048576):.3f} MB')
        except:
            print('ERRORE, riprovare')
            return


    def _convertiInJPG(self,percorsoCartella):
        estensione=Path(self.percorso).suffix.lower()
        if estensione in ['.jpg', '.jpeg']:
            print(f'L\'immagine {os.path.basename(self.percorso)} è già un jpg')
            return
        if percorsoCartella=='': #un file solo
            output_path = salvaConNome(".jpg")
        else:   #gestione di più file
            nomeFile=os.path.basename(self.percorso)
            nomeFileSenzaEstensione=os.path.splitext(nomeFile)[0]
            nomeNuovo=nomeFileSenzaEstensione+'_convertitoInJPG.jpg'
            output_path=os.path.join(percorsoCartella,nomeNuovo)
        
        if not output_path:
            return

        try:
            with Image.open(self.percorso) as im:
                if im.mode in ("RGBA", "P"):
                    im = im.convert("RGB")
                im.save(output_path, "JPEG", quality=100, subsampling=0)
            print(f'Il file {os.path.basename(self.percorso)} è stato convertito correttamente in jpg')
        except:
            print('ERRORE, riprovare')
            return

#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

class fileVideo(fileGenerico):
    def __init__(self, file_path):
        super().__init__(file_path)
        cartella_script = ottieni_percorso_base() 
        
        percorsi_comuni_ffmpeg = [
            os.path.join(cartella_script, "ffmpeg.exe"), 
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"
        ]
        self.ffmpeg_exe = trova_eseguibile("ffmpeg", percorsi_comuni_ffmpeg)
        
    def scegliAzione(self,scelta,percorsoCartella,extraParam):
        mappaScelte={
            1 : self._convertiInmp4,
            2 : self._comprimiVideo 
        }   
        if scelta in mappaScelte:
            if extraParam: 
                if scelta==2:
                    qualita=extraParam['qualita']
                    if qualita!=1 and qualita!=2 and qualita!=3:
                        return
                    return mappaScelte[scelta](percorsoCartella=percorsoCartella,qualita=qualita)
            else:
                return mappaScelte[scelta](percorsoCartella=percorsoCartella)
        else:
            print('SCELTA NON GIUSTA')
            return
        
    def getAzioniDisponibili(self):
        print('Le azioni disponibili sono: \n')
        print('---->Per convertire il video in mp4 premere 1')
        print('---->Per comprimere il video premere 2')
    
    def aggiungiParametriExtra(self, scelta,listaFile=None):
        if scelta==2:
            print('Selezionare la qualità di compressione:')
            print('---->Premere 1 per compressione leggera: ')
            print('---->Premere 2 per compressione media(riduce molto il peso ma qualità accettabile): ')
            print('---->Premere 3 per compressione pesante(qualità bassa): ')
            qualita=int(input())
            return {'qualita': qualita}
        else:
            return {}

    def _convertiInmp4(self,percorsoCartella):
        estensione=Path(self.percorso).suffix.lower()
        if estensione=='.mp4':
            print(f'Il file {os.path.basename(self.percorso)} è già mp4')
            return
        if percorsoCartella=='': #un file solo
            output_path = salvaConNome(".mp4")
        else:   #gestione di più file
            nomeFile=os.path.basename(self.percorso)
            nomeFileSenzaEstensione=os.path.splitext(nomeFile)[0]
            nomeNuovo=nomeFileSenzaEstensione+'_convertitoInmp4.mp4'
            output_path=os.path.join(percorsoCartella,nomeNuovo)
        
        if not output_path:
            return


        try:
            print(f'Avvio conversione di {os.path.basename(self.percorso)}...')
            comando = [
                self.ffmpeg_exe,
                '-y',             
                '-i', self.percorso,
                '-c:v', 'libx264', 
                '-c:a', 'aac',     
                '-strict', 'experimental', 
                output_path]
            
            subprocess.run(comando,capture_output=True,text=True)
            print(f'Il file {os.path.basename(self.percorso)} è stato convertito correttamente in {os.path.basename(output_path)}')
        except:
            print('Errore, riprovare')
            return
        

    def _comprimiVideo(self,percorsoCartella,qualita):
        mappaQualita={
            1 : '23',
            2 : '28',
            3 : '35'
        }
        if qualita in mappaQualita:
            estensione=Path(self.percorso).suffix.lower()
            if percorsoCartella=='': #un file solo
                output_path = salvaConNome(estensione)
            else:   #gestione di più file
                nomeFile=os.path.basename(self.percorso)
                nomeFileSenzaEstensione=os.path.splitext(nomeFile)[0]
                nomeNuovo=nomeFileSenzaEstensione+'_compresso'+estensione
                output_path=os.path.join(percorsoCartella,nomeNuovo)
            
            if not output_path:
                return
            
            crf_scelto=mappaQualita[qualita]

            try:
                print(f'Avvio compressione di {os.path.basename(self.percorso)}...')
                comando = [
                    self.ffmpeg_exe,
                    '-y',                
                    '-i', self.percorso, 
                    '-c:v', 'libx264',  
                    '-crf', crf_scelto, 
                    '-preset', 'fast', 
                    '-c:a', 'aac',       
                    '-b:a', '128k',      
                    output_path          
                ]
                subprocess.run(comando,check=True,capture_output=True)
                print(f'Il file {os.path.basename(self.percorso)} prima pesava: {(os.path.getsize(self.percorso)/1048576):.3f} MB')
                print(f'Il file compresso {os.path.basename(output_path)} adesso pesa: {(os.path.getsize(output_path)/1048576):.3f} MB')
            
            except:
                print('ERRORE, riprovare')
        else:
            print('Scegliere una qualità giusta')
            return
        
#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

#VARIABILI GLOBALI

mappaEstensioni={       #mappa per decidere il costruttore da chiamare
            '.pdf' : filePdf,
            '.jpeg' : fileImm,
            '.png' : fileImm,
            '.HEIC' : fileImm,
            '.jpg' : fileImm,
            '.mp4' : fileVideo,
            '.mov' : fileVideo
        }

#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

def controlloOmegeneitaFile(percorsiFile):
    estensione=Path(percorsiFile[0]).suffix.lower()
    if estensione in mappaEstensioni:
        tipoFile=mappaEstensioni[estensione]
    else:
        return False
    omogeneita=True
    for x in percorsiFile:
        ext=Path(x).suffix.lower()
        if ext in mappaEstensioni:
            tipoX=mappaEstensioni[ext]
        else:
            return False
        if tipoX!=tipoFile:
            omogeneita=False
            break
    return omogeneita