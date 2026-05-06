import os
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener
from pathlib import Path  #libreria importata per estrarre facilmente l' extension del file
from abc import ABC, abstractmethod
import subprocess
import pikepdf
from funzioni import save_as, get_base_path, create_menu , use_settings , get_video_codec
import platform



# Inizializza il plugin per leggere i file HEIC (Apple)
register_heif_opener()

#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

class GenericFile(ABC):    #classe astratta che gestisce la factory, di questa nel main bisogna chimare solo il metodo statico
    def __init__(self, file_path: str, config: dict) -> None:
        """
        Initializes the generic file object with basic file metadata.

        Args:
            file_path: Absolute path to the file.
            config: Configuration dictionary.
        """
        self.path=file_path
        self.name=os.path.basename(file_path)
        self.file_dimension=os.path.getsize(file_path)
        self.config=config

    @staticmethod
    def _get_extension_map()-> dict:
        extension_map={       #mappa per decidere il constructor da chiamare
            '.pdf' : PDFFile,
            '.jpeg' : ImageFile,
            '.png' : ImageFile,
            '.heic' : ImageFile,
            '.heif' : ImageFile,
            '.jpg' : ImageFile,
            '.mp4' : VideoFile,
            '.mov' : VideoFile,
            '.avi' : VideoFile,
            '.mkv' : VideoFile,
            '.hevc' : VideoFile,
            '.h265' : VideoFile
        }
        return extension_map

    @staticmethod
    def create_from_path(file_path: str, config: dict) -> 'GenericFile':
        """
        Factory method that creates the appropriate file object based on the file extension.

        Args:
            file_path: Absolute path to the file.
            config: Configuration dictionary.

        Returns:
            An instance of the appropriate GenericFile subclass.
        """
        extension_map=GenericFile._get_extension_map()
        extension=Path(file_path).suffix.lower()   #prendo l'extension
        if extension in extension_map:   #controllo se c' è l' extension, con la mappa ricavo il constructor e lo chiamo
            constructor=extension_map[extension]
            return constructor(file_path, config)
        else:
            raise ValueError(f'Unsupported file extension: {extension}')

    def add_extra_parameters(self, choice: int, file_list: list | None = None) -> dict:
        """
        Collects additional parameters needed before executing the chosen action.
        Base implementation returns an empty dict. Subclasses should override this.

        Args:
            choice: The action number selected by the user.
            file_list: List of file paths involved in the operation.

        Returns:
            A dictionary of extra parameters, or {'stop': True} to abort the main loop but with the operation done, {'stop' : False} to abortthe main loop if there is a problem.
        """
        return {}

    @abstractmethod
    def choose_action(self, choice: int, directory_path: str, extra_parameters: dict | None = None) -> None:
        """
        Executes the action corresponding to the user's choice.

        Args:
            choice: The action number selected by the user.
            directory_path: Output folder path. Empty string if saving a single file via dialog.
            extra_parameters: Additional parameters required by specific actions.
        """
        pass

    @abstractmethod
    def get_available_actions(self) -> dict:
        """Return a dictionary where keys are all the available actions for this type of file, values indicate that action in this program"""
        pass

#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

class PDFFile(GenericFile):        #classe che gestisce i file pdf
    def __init__(self, file_path: str, config: dict) -> None:
        """
        Initializes the PDFFile object and locates the GhostScript executable.

        Args:
            file_path: Absolute path to the PDF file.
            config: Configuration dictionary.
        """
        super().__init__(file_path, config)
        if platform.system() == 'Windows':
            self.gs_exe = os.path.join(get_base_path(), "gs", "bin", "gswin64c.exe")
        else:
            self.gs_exe = "gs"  # trovato nel PATH di sistema)

    def get_available_actions(self) -> dict:
        available_actions={
            'Converti il pdf in pdf/A' : 1,
            'Comprimi pdf' : 2,
            'Unisci più pdf' : 3
        }
        return available_actions

    def choose_action(self, choice: int, directory_path: str = '', extra_parameters: dict | None = None) -> None:
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

    def add_extra_parameters(self, choice: int, file_list: list | None = None) -> dict:
        if choice==2:
            available_quality={
                    'Qualità alta, compressione bassa' : 1,
                    'Qualità media, compressione media' : 2,
                    'Qualità bassa, compressione alta' : 3
                }
            quality=use_settings(category='pdf',option='pdf_compression_quality')
            if quality:
                inverted_available_quality= {v: k for k, v in available_quality.items()}
                print(f'Dalle impostazioni è selezionata: {inverted_available_quality[quality]}')
            else:
                quality=create_menu(message='Scegli la qualità di compressione', dictio=available_quality)
            return {'quality' : quality}
        elif choice==3: #qui non si aggiunge parametri extra ma si usa la funzione per chiamarne un altra senza fare il ciclo for del main
            if file_list and len(file_list)>1:   #serve per quando si passa più file ma se ne vuole solo uno in output, quindi la funzione unisce i file in uno
                self._merge_PDF(file_list)
                return {'stop' : True}
            else:
                print('Seleziona più pdf da unire')
                return {'stop' : False}  #quindi stampo errore e fermo l'esecuzione
        else:
            return {}

    def _convert_to_PDFA(self, directory_path: str) -> None:
        """
        Converts the PDF file to PDF/A-1b format by adding XMP metadata.

        Args:
            directory_path: Output folder path. Empty string if saving via dialog.

        Raises:
            pikepdf.PdfError: If the PDF is corrupted or cannot be read.
            OSError: If the output file cannot be written.
        """
        if directory_path=='': #un file solo
            output_path = save_as(".pdf")
        else:   #gestione di più file
            suffix=self.config['output_suffixes']['pdfa']
            file_name=os.path.basename(self.path)
            file_name_without_extension=os.path.splitext(file_name)[0]
            new_name=file_name_without_extension+suffix+'.pdf'
            output_path=os.path.join(directory_path,new_name)
        
        if not output_path:
            return
        
        print("Conversione a PDF/A-1b")
        
        try:
            with pikepdf.open(self.path) as pdf:
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

   
    def _compress_PDF(self, directory_path: str, quality: int) -> None:
        """
        Compresses the PDF file using GhostScript.

        Args:
            directory_path: Output folder path. Empty string if saving via dialog.
            quality: Compression level — 1 (low compression), 2 (medium), 3 (high compression).

        Raises:
            subprocess.CalledProcessError: If GhostScript returns an error.
            FileNotFoundError: If the GhostScript executable is not found.
            OSError: If the output file cannot be written or read.
        """
        quality_map={
            1 : '/prepress',
            2 : '/ebook',
            3 : '/screen'
        }

        if quality in quality_map:
            if directory_path=='': #un file solo
                output_path = save_as(".pdf")
            else:   #gestione di più file
                suffix=self.config['output_suffixes']['compressed']
                file_name=os.path.basename(self.path)
                file_name_without_extension=os.path.splitext(file_name)[0]
                new_name=file_name_without_extension+suffix+'.pdf'
                output_path=os.path.join(directory_path,new_name)
        
            if not output_path:
                return
            try:
                compatibility_level= self.config['pdf']['compatibility_level']
                command=[
                    self.gs_exe,
                    '-sDEVICE=pdfwrite',
                    f'-dCompatibilityLevel={compatibility_level}',
                    f'-dPDFSETTINGS={quality_map[quality]}',
                    '-dNOPAUSE',
                    '-dQUIET',
                    '-dBATCH',
                    f'-sOutputFile={output_path}',
                    self.path]
                kwargs = {}
                if os.name == 'nt':
                    kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                subprocess.run(command, check=True, capture_output=True, text=True, **kwargs)
                bytes_per_mb=self.config['constants']['bytes_per_mb']
                print(f'Il file {os.path.basename(self.path)} prima pesava: {(os.path.getsize(self.path)/bytes_per_mb):.3f} MB')
                print(f'Il file convertito {os.path.basename(output_path)} adesso pesa: {(os.path.getsize(output_path)/bytes_per_mb):.3f} MB')
            except subprocess.CalledProcessError as e:
                print(f'Errore ghostscript : {e}')
            except FileNotFoundError as e:
                print('Eseguibile di ghostscript non trovato')
            except OSError as e:
                print(f'Errore di disco : {e}') 
            

        else:
            print('ERRORE RIPROVARE')
            return

    def _merge_PDF(self, files_paths: list | None = None) -> None:
        """
        Merges multiple PDF files into a single output file using GhostScript.

        Args:
            files_paths: List of absolute paths to the PDF files to merge.

        Raises:
            subprocess.CalledProcessError: If GhostScript returns an error.
            FileNotFoundError: If the GhostScript executable is not found.
            OSError: If the output file cannot be written.
        """
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
                kwargs = {}
                if os.name == 'nt':
                    kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                subprocess.run(command, check=True, capture_output=True, text=True, **kwargs)
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
    def __init__(self, file_path: str, config: dict) -> None:
        """
        Initializes the ImageFile object.

        Args:
            file_path: Absolute path to the image file.
            config: Configuration dictionary.
        """
        super().__init__(file_path, config)

    def get_available_actions(self) -> dict:
        available_actions={
            'Converti una o più immagini in pdf' : 1,
            'Comprimi immagine' : 2,
            'Converti immagine in jpg' : 3
        }
        return available_actions

    def choose_action(self, choice: int, directory_path: str = '', extra_parameters: dict | None = None) -> None:
        if extra_parameters is None:
            extra_parameters={}
        choice_map={
            1 : self._convert_to_PDF,
            2 : self._image_compress,
            3 : self._convert_to_JPG
        }   
        if choice in choice_map:
            if extra_parameters:  #per ora niente parametri extra, qui non si dovrebbe entrare
               return
            else:
                return choice_map[choice](directory_path=directory_path)
        else:
            print('SCELTA NON GIUSTA')
            return

    def add_extra_parameters(self, choice: int, file_list: list | None = None) -> dict:
        if choice==1:       #qui non si aggiunge parametri extra ma si usa la funzione per chiamarne un altra senza fare il ciclo for del main
            if file_list:   #serve per quando si passa più file ma se ne vuole solo uno in output, quindi la funzione unisce i file in uno
               
                self._convert_to_PDF(file_list)
                return {'stop' : True}
            print('Nessun file selezionato')
            return {'stop' : False}
        else:
            return {}

    def _convert_to_PDF(self, file_list: list | None = None) -> None:
        """
        Converts one or more images into a single PDF file.

        Args:
            file_list: List of absolute paths to the image files to convert.

        Raises:
            UnidentifiedImageError: If an image file is corrupted or unrecognized.
            OSError: If the output file cannot be written.
        """
        if file_list is None:
            file_list=[]
        if file_list:
            output_path = save_as('.pdf')
            other_image=[]
            if not output_path:
                return
            try:
                img1=Image.open(file_list[0])
                if img1.mode!='RGB':
                    img1=img1.convert('RGB')
                for image in file_list[1:]:
                    img_temp=Image.open(image)
                    if img_temp.mode!='RGB':
                        img_temp=img_temp.convert('RGB')
                    other_image.append(img_temp)
                img1.save(output_path,'PDF',save_all=True,append_images=other_image)
                print(f'Il file {os.path.basename(output_path)} è stato creato correttamente')
            except UnidentifiedImageError as e:
                print(f'Errore nell\' apertura dell\'immagine : {e}')
            except OSError as e:
                print(f'Errore nel salvataggio del file {e}')
            finally:    #blocco che si assicura che a prescindere tutte le immagini aperte vengano chiuse
                for img in other_image:
                    img.close()
                if 'img1' in locals():  #controlla che img1 sia tra le variabili locali, altrimenti se l'apertura era fallita e provo a chiudere img1 avrei errore
                    img1.close()

        else:
            print('ERRORE,riprovare')


    def _image_compress(self, directory_path: str) -> None:
        """
        Compresses the image file, preserving its original format.

        Args:
            directory_path: Output folder path. Empty string if saving via dialog.

        Raises:
            UnidentifiedImageError: If the image file is corrupted or unrecognized.
            OSError: If the output file cannot be written.
        """
        extension=Path(self.path).suffix.lower()
        if directory_path=='': #un file solo
            output_path = save_as(extension)
        else:   #gestione di più file
            suffix=self.config['output_suffixes']['compressed']
            file_name=os.path.basename(self.path)
            file_name_without_extension=os.path.splitext(file_name)[0]
            new_name=file_name_without_extension+suffix+extension
            output_path=os.path.join(directory_path,new_name)
        if not output_path:
            return
        try:
            if extension in ['.jpg','.jpeg']:
                with Image.open(self.path) as img:
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    quality=self.config['image']['compress_quality']
                    img.save(output_path, "JPEG", optimize=True, quality=quality)
            else:
                with Image.open(self.path) as img:
                    img.save(output_path, optimize=True)
            bytes_per_mb=self.config['constants']['bytes_per_mb']
            print(f'Il file {os.path.basename(self.path)} prima pesava: {(os.path.getsize(self.path)/bytes_per_mb):.3f} MB')
            print(f'Il file convertito {os.path.basename(output_path)} adesso pesa: {(os.path.getsize(output_path)/bytes_per_mb):.3f} MB')
        except UnidentifiedImageError as e:
            print(f'Errore nell\' apertura dell\'immagine : {e}')
        except OSError as e:
            print(f'Errore nel salvataggio del file {e}')


    def _convert_to_JPG(self, directory_path: str) -> None | str:
        """
        Converts the image to JPEG format.

        Args:
            directory_path: Output folder path. Empty string if saving via dialog.
        Returns:
            None in general
            str : path of file already jpg
        Raises:
            UnidentifiedImageError: If the image file is corrupted or unrecognized.
            OSError: If the output file cannot be written.
        """
        extension=Path(self.path).suffix.lower()
        if extension in ['.jpg', '.jpeg']:
            print(f'L\'immagine {os.path.basename(self.path)} è già un jpg')
            return self.path
        if directory_path=='': #un file solo
            output_path = save_as(".jpg")
        else:   #gestione di più file
            suffix=self.config['output_suffixes']['converted_jpg']
            file_name=os.path.basename(self.path)
            file_name_without_extension=os.path.splitext(file_name)[0]
            new_name=file_name_without_extension+suffix+'.jpg'
            output_path=os.path.join(directory_path,new_name)
        
        if not output_path:
            return

        try:
            with Image.open(self.path) as im:
                if im.mode in ("RGBA", "P"):
                    im = im.convert("RGB")
                quality=self.config['image']['jpeg_quality']
                subsampling=self.config['image']['jpeg_subsampling']
                im.save(output_path, "JPEG", quality=quality, subsampling=subsampling)
            print(f'Il file {os.path.basename(self.path)} è stato convertito correttamente in jpg')
        except UnidentifiedImageError as e:
            print(f'Errore nell\' apertura dell\'immagine : {e}')
        except OSError as e:
            print(f'Errore nel salvataggio del file {e}')

#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

class VideoFile(GenericFile):
    def __init__(self, file_path: str, config: dict) -> None:
        """
        Initializes the VideoFile object and locates the ffmpeg executable.

        Args:
            file_path: Absolute path to the video file.
            config: Configuration dictionary.
        """
        super().__init__(file_path, config)
        if platform.system() == 'Windows':
            self.ffmpeg_exe = os.path.join(get_base_path(), "ffmpeg.exe")
        else:
            self.ffmpeg_exe = "ffmpeg"  # trovato nel PATH di sistema
        
    def choose_action(self, choice: int, directory_path: str, extra_parameters: dict | None = None) -> None:
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
        
    def get_available_actions(self) -> dict:
        available_actions={
            'Converti video in mp4' : 1,
            'Comprimi video' : 2
        }
        return available_actions

    
    def add_extra_parameters(self, choice: int, file_list: list | None = None) -> dict:
        if choice==2:
            available_quality={
                'Compressione bassa' : 1,
                'Compressione media' : 2,
                'Compressione alta' : 3
            }
            quality=use_settings(category='video',option='video_compression_quality')
            if quality:
                inverted_available_quality= {v: k for k, v in available_quality.items()}
                print(f'Dalle impostazioni è selezionata: {inverted_available_quality[quality]}')
            else:
                quality=create_menu(message='Scegli la qualità di ccompressione', dictio=available_quality)
            return {'quality' : quality}
        else:
            return {}

    def _convert_to_mp4(self, directory_path: str) -> None | str:
        """
        Converts the video file to MP4 format using ffmpeg.

        Args:
            directory_path: Output folder path. Empty string if saving via dialog.
         Returns:
            None in general
            str : path of file already jpg
        Raises:
            subprocess.CalledProcessError: If ffmpeg returns an error.
            FileNotFoundError: If the ffmpeg executable is not found.
            OSError: If the output file cannot be written.
        """
        extension=Path(self.path).suffix.lower()
        if extension=='.mp4' and get_video_codec(self.path)=="h264":
            print(f'Il file {os.path.basename(self.path)} è già mp4')
            return self.path
        if directory_path=='': #un file solo
            output_path = save_as(".mp4")
        else:   #gestione di più file
            suffix=self.config['output_suffixes']['converted_mp4']
            file_name=os.path.basename(self.path)
            file_name_without_extension=os.path.splitext(file_name)[0]
            new_name=file_name_without_extension+suffix+'.mp4'
            output_path=os.path.join(directory_path,new_name)
        
        if not output_path:
            return


        try:
            print(f'Avvio conversione di {os.path.basename(self.path)}...')
            codec_video=self.config['video']['codec_video']
            codec_audio=self.config['video']['codec_audio']
            command = [
                self.ffmpeg_exe,
                '-y',             
                '-i', self.path,
                '-c:v', codec_video, 
                '-c:a', codec_audio,     
                '-strict', 'experimental', 
                output_path]
            
            kwargs = {}
            if os.name == 'nt':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            subprocess.run(command, check=True, capture_output=True, text=True, **kwargs)
            print(f'Il file {os.path.basename(self.path)} è stato convertito correttamente in {os.path.basename(output_path)}')
        except subprocess.CalledProcessError as e:
                print(f'Errore ffmpeg : {e}')
        except FileNotFoundError as e:
                print('Eseguibile di ffmpeg non trovato')
        except OSError as e:
                print(f'Errore di disco : {e}')
        

    def _video_compress(self, directory_path: str, quality: int) -> None:
        """
        Compresses the video file using ffmpeg with the H.264 codec.

        Args:
            directory_path: Output folder path. Empty string if saving via dialog.
            quality: Compression level — 1 (light), 2 (medium), 3 (heavy).

        Raises:
            subprocess.CalledProcessError: If ffmpeg returns an error.
            FileNotFoundError: If the ffmpeg executable is not found.
            OSError: If the output file cannot be written or read.
        """
        crf_low=self.config['video']['crf_low']
        crf_medium=self.config['video']['crf_medium']
        crf_high=self.config['video']['crf_high']
        quality_map={
            1 : crf_low,
            2 : crf_medium,
            3 : crf_high
        }
        if quality in quality_map:
            extension=Path(self.path).suffix.lower()
            if directory_path=='': #un file solo
                output_path = save_as(extension)
            else:   #gestione di più file
                suffix=self.config['output_suffixes']['compressed']
                file_name=os.path.basename(self.path)
                file_name_without_extension=os.path.splitext(file_name)[0]
                new_name=file_name_without_extension+suffix+extension
                output_path=os.path.join(directory_path,new_name)
            
            if not output_path:
                return
            
            chosen_crf=quality_map[quality]

            try:
                print(f'Avvio compressione di {os.path.basename(self.path)}...')
                codec_video=self.config['video']['codec_video']
                codec_audio=self.config['video']['codec_audio']
                preset=self.config['video']['preset']
                audio_bitrate=self.config['video']['audio_bitrate']
                command = [
                    self.ffmpeg_exe,
                    '-y',                
                    '-i', self.path, 
                    '-c:v', codec_video,  
                    '-crf', chosen_crf, 
                    '-preset', preset, 
                    '-c:a', codec_audio,       
                    '-b:a', audio_bitrate,      
                    output_path          
                ]
                kwargs = {}
                if os.name == 'nt':
                    kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                subprocess.run(command, check=True, capture_output=True, text=True, **kwargs)
                bytes_per_mb=self.config['constants']['bytes_per_mb']
                print(f'Il file {os.path.basename(self.path)} prima pesava: {(os.path.getsize(self.path)/bytes_per_mb):.3f} MB')
                print(f'Il file compresso {os.path.basename(output_path)} adesso pesa: {(os.path.getsize(output_path)/bytes_per_mb):.3f} MB')
            
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


def check_homogeneity(files_paths: tuple[str, ...]) -> bool:
    """
    Checks that all selected files belong to the same supported file type.

    Args:
        files_paths: List of absolute paths to the files to check.

    Returns:
        True if all files map to the same class, False otherwise.
    """
    extension_map=GenericFile._get_extension_map()
    extension=Path(files_paths[0]).suffix.lower()
    if extension in extension_map:
        file_type=extension_map[extension]
    else:
        return False
    homogeneity=True
    for x in files_paths[1:]: #salto il primo file, controllarlo con se stesso non avrebbe senso
        ext=Path(x).suffix.lower()
        if ext in extension_map:
            type_X=extension_map[ext]
        else:
            return False
        if type_X!=file_type:
            homogeneity=False
            break
    return homogeneity