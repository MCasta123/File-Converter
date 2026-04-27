import os
from PIL import Image, UnidentifiedImageError
from pathlib import Path  #libreria importata per estrarre facilmente l' extension del file
from abc import ABC, abstractmethod
import subprocess
import pikepdf
from funzioni import save_as, search_executable, get_base_path




#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

class GenericFile(ABC):    #classe astratta che gestisce la factory, di questa nel main bisogna chimare solo il metodo statico
    def __init__(self,file_path):
        self.path=file_path
        self.name=os.path.basename(file_path)
        self.file_dimension=os.path.getsize(file_path)
    @staticmethod
    def create_from_path(file_path):  
        extension=Path(file_path).suffix.lower()   #prendo l'extension
        if extension in extension_map:   #controllo se c' è l' extension, con la mappa ricavo il constructor e lo chiamo
            constructor=extension_map[extension]
            return constructor(file_path)
        else:
            print('Estensione non trovata')

    def add_extra_parameters(self,choice,file_list=None):   #medoto che di base restituisce un dizionario vuoto, ma dovrà essere sovrascritto dalle classi figlie
        return {}

    @abstractmethod
    def choose_action(self,choice,directory_path,extra_parameters=None): #costringo le classi figlie a implementarlo
        pass
    @abstractmethod
    def get_available_actions(self): #costringo le classi figlie a implementarlo
        pass

#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

class PDFFile(GenericFile):        #classe che gestisce i file pdf
    def __init__(self, file_path):
        super().__init__(file_path)
        script_directory = get_base_path()
        percorsi_comuni_gs = [
            os.path.join(script_directory, "gs", "bin", "gswin64c.exe"),

            r"C:\Program Files\gs\gs*\bin\gswin64c.exe",
            r"C:\Program Files (x86)\gs\gs*\bin\gswin32c.exe"
        ]
        
        self.gs_exe = search_executable("gswin64c", percorsi_comuni_gs)

    def get_available_actions(self):
        print('Le azioni disponibili sono: \n')
        print('---->Per convertire il pdf in pdf/A premere 1')
        print('---->Per comprimere il pdf premere 2')
        print('---->Per unire i pdf premere 3')

    def choose_action(self,choice,directory_path='',extra_parameters=None):
        if extra_parameters is None:
            extra_parameters={}
        choice_map={
            1 : self._convert_to_PDFA,
            2 : self._compress_PDF, 
            3 : self._merge_PDF
        }   
        if choice in choice_map:
            if extra_parameters:
                if choice==2:
                    quality=extra_parameters['quality']
                    if quality==0:
                        return
                    return choice_map[choice](directory_path=directory_path,quality=quality)
            else:
                return choice_map[choice](directory_path=directory_path)
        else:
            print('SCELTA NON GIUSTA')
            return

    def add_extra_parameters(self, choice,file_list=None):
        if choice==2:
            print('Scegli la qualità di compressione: \n')
            print('----->Premere 1 per qualità alta, compressione bassa')
            print('----->Premere 2 per qualità media, compressione media')
            print('----->Premere 3 per qualità bassa, compressione alta')
            quality=int(input())
            return {'quality' : quality}
        elif choice==3: #qui non si aggiunge parametri extra ma si usa la funzione per chiamarne un altra senza fare il ciclo for del main
            if file_list:   #serve per quando si passa più file ma se ne vuole solo uno in output, quindi la funzione unisce i file in uno
                self._merge_PDF(file_list)
                return {'stop' : True}
        else:
            return {}

    def _convert_to_PDFA(self,directory_path):
        if directory_path=='': #un file solo
            output_path = save_as(".pdf")
        else:   #gestione di più file
            file_name=os.path.basename(self.path)
            file_name_without_extension=os.path.splitext(file_name)[0]
            new_name=file_name_without_extension+'_convertitoInPDFA.pdf'
            output_path=os.path.join(directory_path,new_name)
        
        if not output_path:
            return
        
        print("Conversione a PDF/A-1b")
        
        try:
            with pikepdf.open(self.path,'r') as pdf:
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
                
                
                print(f"PDF/A-1b salvato: {output_path}")
            
        except pikepdf.PdfError as e:
            print(f"PDF corrotto o non leggibile: {e}")
        except OSError as e:
            print(f"Errore di lettura/scrittura file: {e}")

   
    def _compress_PDF(self,directory_path,quality):
        quality_map={
            1 : '/prepress',
            2 : '/ebook',
            3 : '/screen'
        }

        if quality in quality_map:
            if directory_path=='': #un file solo
                output_path = save_as(".pdf")
            else:   #gestione di più file
             file_name=os.path.basename(self.path)
             file_name_without_extension=os.path.splitext(file_name)[0]
             new_name=file_name_without_extension+'_compresso.pdf'
             output_path=os.path.join(directory_path,new_name)
        
            if not output_path:
                return
            try:
                command=[
                    self.gs_exe,
                    '-sDEVICE=pdfwrite',
                    '-dCompatibilityLevel=1.4',
                    f'-dPDFSETTINGS={quality_map[quality]}',
                    '-dNOPAUSE',
                    '-dQUIET',
                    '-dBATCH',
                    f'-sOutputFile={output_path}',
                    self.path]
                
                subprocess.run(command, check=True)
                print(f'Il file {os.path.basename(self.path)} prima pesava: {(os.path.getsize(self.path)/1048576):.3f} MB')
                print(f'Il file convertito {os.path.basename(output_path)} adesso pesa: {(os.path.getsize(output_path)/1048576):.3f} MB')
            except subprocess.CalledProcessError as e:
                print(f'Errore ghostscript : {e}')
            except FileNotFoundError as e:
                print('Eseguibile di ghostscript non trovato')
            except OSError as e:
                print(f'Errore di disco : {e}') 
            

        else:
            print('ERRORE RIPROVARE')
            return

    def _merge_PDF(self,files_paths=None):   
        if files_paths is None:
            files_paths=[]
        if files_paths:
            if len(files_paths)<=1:
                print('Seleziona più pdf da unire')
                return
            output_path=save_as('.pdf')
            if not output_path:
                return
            
            try:
                command = [
                self.gs_exe,
                "-dNOPAUSE",
                "-sDEVICE=pdfwrite",
                f"-sOUTPUTFILE={output_path}",
                "-dBATCH"]
            
                # Aggiungiamo tutti i file di input alla lista del command
                command.extend(files_paths)
                subprocess.run(command, check=True, capture_output=True)
                print(f'I pdf sono stati uniti correttamente nel file {os.path.basename(output_path)}')
            except subprocess.CalledProcessError as e:
                print(f'Errore ghostscript : {e}')
            except FileNotFoundError as e:
                print('Eseguibile di ghostscript non trovato')
            except OSError as e:
                print(f'Errore di disco : {e}') 
            

#######################################################################################################################
#######################################################################################################################      
#######################################################################################################################

class ImageFile(GenericFile):
    def __init__(self, file_path):
        super().__init__(file_path)


    def get_available_actions(self):
        print('Le azioni disponibili sono: \n')
        print('---->Per convertire l\'immagini in pdf premere 1')
        print('---->Per comprimere l\'immage premere 2')
        print('---->Per convertire l\'immage in jpg premere 3')

    def choose_action(self,choice,directory_path='',extra_parameters=None):
        if extra_parameters is None:
            extra_parameters={}
        choice_map={
            1 : self._convert_to_PDF,
            2 : self._immage_compress,
            3 : self._converto_to_JPG
        }   
        if choice in choice_map:
            if extra_parameters:  #per ora niente parametri extra, qui non si dovrebbe entrare
               return
            else:
                return choice_map[choice](directory_path=directory_path)
        else:
            print('SCELTA NON GIUSTA')
            return

    
    def add_extra_parameters(self,choice,file_list=None):
        if choice==1:       #qui non si aggiunge parametri extra ma si usa la funzione per chiamarne un altra senza fare il ciclo for del main
            if file_list:   #serve per quando si passa più file ma se ne vuole solo uno in output, quindi la funzione unisce i file in uno
               
                self._convert_to_PDF(file_list)
                return {'stop' : True}
        else:
            return {}

    def _convert_to_PDF(self,file_list=None):
        if file_list is None:
            file_list=[]
        if file_list:
            output_path = save_as('.pdf')
            if not output_path:
                return
            try:
                img1=Image.open(file_list[0])
                if img1.mode!='RGB':
                    img1=img1.convert('RGB')
                other_immage=[]
                for immage in file_list[1:]:
                    img_temp=Image.open(immage)
                    if img_temp.mode!='RGB':
                        img_temp=img_temp.convert('RGB')
                    other_immage.append(img_temp)
                img1.save(output_path,'PDF',save_all=True,append_images=other_immage)
                print(f'Il file {os.path.basename(output_path)} è stato creato correttamente')
            except UnidentifiedImageError as e:
                print(f'Errore nell\' apertura dell\'immagine : {e}')
            except OSError as e:
                print(f'Errore nel salvataggio del file {e}')
            finally:    #blocco che si assicura che a prescindere tutte le immagini aperte vengano chiuse
                for img in other_immage:
                    img.close()
                img1.close()

        else:
            print('ERRORE,riprovare')


    def _immage_compress(self,directory_path):
        extension=Path(self.path).suffix.lower()
        if directory_path=='': #un file solo
            output_path = save_as(extension)
        else:   #gestione di più file
            file_name=os.path.basename(self.path)
            file_name_without_extension=os.path.splitext(file_name)[0]
            new_name=file_name_without_extension+'_compresso'+extension
            output_path=os.path.join(directory_path,new_name)
        if not output_path:
            return
        try:
            if extension in ['.jpg','.jpeg']:
                with Image.open(self.path) as img:
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    img.save(output_path, "JPEG", optimize=True, quality=80)
            else:
                with Image.open(self.path) as img:
                    img.save(output_path, optimize=True)
            print(f'Il file {os.path.basename(self.path)} prima pesava: {(os.path.getsize(self.path)/1048576):.3f} MB')
            print(f'Il file convertito {os.path.basename(output_path)} adesso pesa: {(os.path.getsize(output_path)/1048576):.3f} MB')
        except UnidentifiedImageError as e:
            print(f'Errore nell\' apertura dell\'immagine : {e}')
        except OSError as e:
            print(f'Errore nel salvataggio del file {e}')


    def _converto_to_JPG(self,directory_path):
        extension=Path(self.path).suffix.lower()
        if extension in ['.jpg', '.jpeg']:
            print(f'L\'immage {os.path.basename(self.path)} è già un jpg')
            return
        if directory_path=='': #un file solo
            output_path = save_as(".jpg")
        else:   #gestione di più file
            file_name=os.path.basename(self.path)
            file_name_without_extension=os.path.splitext(file_name)[0]
            new_name=file_name_without_extension+'_convertitoInJPG.jpg'
            output_path=os.path.join(directory_path,new_name)
        
        if not output_path:
            return

        try:
            with Image.open(self.path) as im:
                if im.mode in ("RGBA", "P"):
                    im = im.convert("RGB")
                im.save(output_path, "JPEG", quality=100, subsampling=0)
            print(f'Il file {os.path.basename(self.path)} è stato convertito correttamente in jpg')
        except UnidentifiedImageError as e:
            print(f'Errore nell\' apertura dell\'immagine : {e}')
        except OSError as e:
            print(f'Errore nel salvataggio del file {e}')

#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

class VideoFile(GenericFile):
    def __init__(self, file_path):
        super().__init__(file_path)
        script_directory = get_base_path() 
        
        percorsi_comuni_ffmpeg = [
            os.path.join(script_directory, "ffmpeg.exe"), 
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"
        ]
        self.ffmpeg_exe = search_executable("ffmpeg", percorsi_comuni_ffmpeg)
        
    def choose_action(self,choice,directory_path,extra_parameters=None):
        if extra_parameters is None:
            extra_parameters={}
        choice_map={
            1 : self._convert_to_mp4,
            2 : self._video_compress 
        }   
        if choice in choice_map:
            if extra_parameters: 
                if choice==2:
                    quality=extra_parameters['quality']
                    if quality!=1 and quality!=2 and quality!=3:
                        return
                    return choice_map[choice](directory_path=directory_path,quality=quality)
            else:
                return choice_map[choice](directory_path=directory_path)
        else:
            print('SCELTA NON GIUSTA')
            return
        
    def get_available_actions(self):
        print('Le azioni disponibili sono: \n')
        print('---->Per convertire il video in mp4 premere 1')
        print('---->Per comprimere il video premere 2')
    
    def add_extra_parameters(self, choice,file_list=None):
        if choice==2:
            print('Selezionare la qualità di compressione:')
            print('---->Premere 1 per compressione leggera: ')
            print('---->Premere 2 per compressione media(riduce molto il peso ma qualità accettabile): ')
            print('---->Premere 3 per compressione pesante(qualità bassa): ')
            quality=int(input())
            return {'quality': quality}
        else:
            return {}

    def _convert_to_mp4(self,directory_path):
        extension=Path(self.path).suffix.lower()
        if extension=='.mp4':
            print(f'Il file {os.path.basename(self.path)} è già mp4')
            return
        if directory_path=='': #un file solo
            output_path = save_as(".mp4")
        else:   #gestione di più file
            file_name=os.path.basename(self.path)
            file_name_without_extension=os.path.splitext(file_name)[0]
            new_name=file_name_without_extension+'_convertitoInmp4.mp4'
            output_path=os.path.join(directory_path,new_name)
        
        if not output_path:
            return


        try:
            print(f'Avvio conversione di {os.path.basename(self.path)}...')
            command = [
                self.ffmpeg_exe,
                '-y',             
                '-i', self.path,
                '-c:v', 'libx264', 
                '-c:a', 'aac',     
                '-strict', 'experimental', 
                output_path]
            
            subprocess.run(command,capture_output=True,text=True,check=True)
            print(f'Il file {os.path.basename(self.path)} è stato convertito correttamente in {os.path.basename(output_path)}')
        except subprocess.CalledProcessError as e:
                print(f'Errore ffmpeg : {e}')
        except FileNotFoundError as e:
                print('Eseguibile di ffmpeg non trovato')
        except OSError as e:
                print(f'Errore di disco : {e}')
        

    def _video_compress(self,directory_path,quality):
        quality_map={
            1 : '23',
            2 : '28',
            3 : '35'
        }
        if quality in quality_map:
            extension=Path(self.path).suffix.lower()
            if directory_path=='': #un file solo
                output_path = save_as(extension)
            else:   #gestione di più file
                file_name=os.path.basename(self.path)
                file_name_without_extension=os.path.splitext(file_name)[0]
                new_name=file_name_without_extension+'_compresso'+extension
                output_path=os.path.join(directory_path,new_name)
            
            if not output_path:
                return
            
            chosen_crf=quality_map[quality]

            try:
                print(f'Avvio compressione di {os.path.basename(self.path)}...')
                command = [
                    self.ffmpeg_exe,
                    '-y',                
                    '-i', self.path, 
                    '-c:v', 'libx264',  
                    '-crf', chosen_crf, 
                    '-preset', 'fast', 
                    '-c:a', 'aac',       
                    '-b:a', '128k',      
                    output_path          
                ]
                subprocess.run(command,check=True,capture_output=True)
                print(f'Il file {os.path.basename(self.path)} prima pesava: {(os.path.getsize(self.path)/1048576):.3f} MB')
                print(f'Il file compresso {os.path.basename(output_path)} adesso pesa: {(os.path.getsize(output_path)/1048576):.3f} MB')
            
            except subprocess.CalledProcessError as e:
                    print(f'Errore ffmpeg : {e}')
            except FileNotFoundError as e:
                    print('Eseguibile di ffmpeg non trovato')
            except OSError as e:
                    print(f'Errore di disco : {e}')
        else:
            print('Scegliere una qualità giusta')
            return
        
#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

#VARIABILI GLOBALI

extension_map={       #mappa per decidere il constructor da chiamare
            '.pdf' : PDFFile,
            '.jpeg' : ImageFile,
            '.png' : ImageFile,
            '.HEIC' : ImageFile,
            '.jpg' : ImageFile,
            '.mp4' : VideoFile,
            '.mov' : VideoFile
        }

#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

def check_homogeneity(files_paths):
    extension=Path(files_paths[0]).suffix.lower()
    if extension in extension_map:
        file_type=extension_map[extension]
    else:
        return False
    homogeneity=True
    for x in files_paths:
        ext=Path(x).suffix.lower()
        if ext in extension_map:
            type_X=extension_map[ext]
        else:
            return False
        if type_X!=file_type:
            homogeneity=False
            break
    return homogeneity