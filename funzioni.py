import platform
import os
import tkinter
import shutil
from tkinter import filedialog
import sys
import subprocess
import tomlkit
from tomlkit.exceptions import TOMLKitError
import questionary
from questionary import Choice, Style
import datetime
import json


################################################################################################################################

def choose_file() -> tuple | str:
    """
    Opens a file dialog to select one or more files.

    Returns:
        A tuple of absolute file paths selected by the user.
        Returns an empty tuple if the user cancels.
    """
    if platform.system() == "Linux":
        if shutil.which('zenity'):
            comando = ['zenity', '--file-selection', '--multiple', '--separator=|', '--title=Seleziona i file da convertire']
            risultato = subprocess.run(comando, capture_output=True, text=True)
            if risultato.returncode == 0:
                return tuple(risultato.stdout.strip().split('|'))
            return ()
            
        elif shutil.which('kdialog'):
            comando = ['kdialog', '--getopenfilename', '.', '--multiple', '--title', 'Seleziona i file da convertire']
            risultato = subprocess.run(comando, capture_output=True, text=True)
            if risultato.returncode == 0:
                # kdialog separa i file con un 'a capo' (newline)
                return tuple(risultato.stdout.strip().split('\n'))
            return ()
    root = tkinter.Tk()
    root.withdraw() 
    root.attributes('-topmost', True)
 #Apri l'Esplora Risorse vero e proprio
    file_path = filedialog.askopenfilenames(
        title="Seleziona i file da convertire",
        filetypes=[("TUTTI I FILE","*.*"),("PDF", "*.pdf"),("IMMAGINI","*.jpg *.jpeg *.png *.HEIC"),("VIDEO","*.mp4 *.mov")]
    )
    root.destroy()  #distruggo finestra
    return file_path

#####################################################################################################################################

def save_as(estensione: str) -> str:
    """
    Opens a save dialog to choose where to save the output file.

    Args:
        estensione: Default file extension for the saved file (e.g. '.pdf').

    Returns:
        The absolute path chosen by the user, or an empty string if cancelled.
    """
    if platform.system() == "Linux":
        if shutil.which('zenity'):
            comando = ['zenity', '--file-selection', '--save', '--confirm-overwrite', f'--title=Salva come (*{estensione})']
            risultato = subprocess.run(comando, capture_output=True, text=True)
            if risultato.returncode == 0:
                percorso = risultato.stdout.strip()
                if not percorso.endswith(estensione): percorso += estensione
                return percorso
            return ""
            
        elif shutil.which('kdialog'):
            comando = ['kdialog', '--getsavefilename', '.', f'*{estensione}', '--title', 'Salva file convertito come...']
            risultato = subprocess.run(comando, capture_output=True, text=True)
            if risultato.returncode == 0:
                percorso = risultato.stdout.strip()
                if not percorso.endswith(estensione): percorso += estensione
                return percorso
            return ""
    root = tkinter.Tk()
    root.withdraw() #creato finestra e nascosta
    root.attributes('-topmost', True)
    saving_path = filedialog.asksaveasfilename(title="Salva file convertito come...",defaultextension=estensione)
    root.destroy()
    return saving_path

####################################################################################################################################

def choose_directory() -> str:
    """
    Opens a dialog to choose a destination folder.

    Returns:
        The absolute path of the chosen directory, or an empty string if cancelled.
    """
    if platform.system() == "Linux":
        if shutil.which('zenity'):
            comando = ['zenity', '--file-selection', '--directory', '--title=Scegli cartella in cui salvare..']
            risultato = subprocess.run(comando, capture_output=True, text=True)
            if risultato.returncode == 0:
                return risultato.stdout.strip()
            return ""
            
        elif shutil.which('kdialog'):
            comando = ['kdialog', '--getexistingdirectory', '.', '--title', 'Scegli cartella in cui salvare..']
            risultato = subprocess.run(comando, capture_output=True, text=True)
            if risultato.returncode == 0:
                return risultato.stdout.strip()
            return ""
    root=tkinter.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    saving_directory=filedialog.askdirectory(title='Scegli cartella in cui salvare..')
    root.destroy()
    return saving_directory

#######################################################################################################################################


    
#######################################################################################################################################

def get_base_path() -> str:
    """ 
    Returns the absolute path of the directory where the program is located,
    whether it is running as a .py script or as a compiled .exe.

    Returns:
        The absolute path of the program's base directory.
    """
    if getattr(sys, 'frozen', False):
        # Se stiamo girando come .exe compilato
        return os.path.dirname(sys.executable)
    else:
        # Se stiamo girando come normale script .py
        return os.path.dirname(os.path.abspath(__file__))
    
def load_settings() -> dict :
    """
    Creates the preferences.toml file if it doesn't exist,
    if it exist he loads it
    
    Returns:
        Dictionary with the user preferences
    """
    directory_path=get_base_path()
    preferences_path=os.path.join(directory_path,'preferences.toml')
    
    if not os.path.exists(preferences_path):   #si crea il file
        settings = """\
# impostazioni utente
[pdf]
pdf_compression_quality = ""
[image]

[video]
video_compression_quality= ""
[general]
after_conversion=""

"""
        with open(preferences_path,'w',encoding="utf-8") as f:
            f.write(settings)
            
    try:
        with open(preferences_path, "r", encoding="utf-8") as f:
            preferences=tomlkit.load(f)
    except TOMLKitError as e:
        print(f'Errore: preferences.toml non è valido: {e}')
        sys.exit(1)
    
    return preferences    
            
def modify_settings(category : str, selected_change: dict) -> bool:
    """
    Function to modify the user preferences
    Args:
        category: string that indicate the category of the change
        selected_change: dictionary where key is the option that user want to change and value is the choice made
    Returns:
        A boolean value that indicate if the operation went well or not
    """
    base_dir = get_base_path()
    config_path = os.path.join(base_dir, 'preferences.toml')
    if not os.path.exists(config_path):
        print('Errore il file preferences.toml non esiste')
        return False
    try:
        settings=load_settings()
        if category and selected_change and settings:
            key, value = next(iter(selected_change.items()))    #seleziono chiave e valore dell'unico elemento nel dizionario selected_change
            if category in settings:
                if key in settings[category]:
                    settings[category][key]=value
                    try:
                        with open(config_path, "w", encoding="utf-8") as f:
                            tomlkit.dump(settings, f)
                            return True
                    except OSError as e:
                        print(f'Errore nella scrittura del file: {e}')
                        return False
    except OSError as e:
        print(f'Errore nell\' apertura del file preferences.toml: {e}')
    return False
    
def create_menu(dictio : dict, message : str | None, dictionary_of_alias : dict | None =None, return_the_keys : bool =False) -> str | int:
    """
    Function that uses questionary library to allow the user to choose between different possibilities contained
    in the dictionary keys and returns the value
    Args:
        dictio: key's dictionary is what user see, values's dictionary is what the proram uses
        message : A strings that represent the title of the choice
        dictionary_of_alias: dictionary where keys are dictio's keys and values are alias of the keys
        return_the_keys : boolean parameter, if False (default) the function return the value of dict, if True it returns the key
    Returns:
        value : the value of the user' s input chosen from dictionary
    """
    theme = Style([

        ('qmark', 'fg:#ffcc00 bold'),       

        ('question', 'fg:#ff9933 bold'),    

        ('pointer', 'fg:#ffff66 bold'),     

        ('highlighted', 'fg:#ffff66 bold'), 

        ('text', 'fg:#cccccc'),             

        ('instruction', 'fg:#808080 italic')
    ])
    if dictio:
        list_of_actions=[]
        for action in dictio:
            list_of_actions.append(action)
        available_actions=[]
        alias=False #variabile che mi dice se tutto va bene e posso usare l'alias
        if dictionary_of_alias:
                keys_of_dictio=list(dictio.keys())
                keys_of_dictionary_of_alias=list(dictionary_of_alias.keys())
                alias=True
                for key in keys_of_dictio:
                    if not key in keys_of_dictionary_of_alias:
                        alias=False
                        break
                    
        for el in list_of_actions:
            element=el
            if alias==True:
                element=dictionary_of_alias[el]
            if return_the_keys: 
                available_actions.append(Choice(title=element,value=el))
            else:
                available_actions.append(Choice(title=element,value=dictio[el]))
        value=questionary.select(message,choices=available_actions,instruction=" ",qmark="",style=theme).ask()
        if value is None:
            sys.exit(0)
        return value
    else: 
        return ''
    
def use_settings(category : str, option: str)->bool | str | int | float:
    """
    Function to use settings contained in preferences.toml
    Args:
        category: indicate the category of change, it's the key of dictionary returned by settings=load_settings()
        option: indicate the specific setting, it's the key of sub-dictionary returned by load_settings() (settings[category])
    Returns:
        False if we can find the option or file preferences.toml
        The value of the selected option
    """
    
    
    preferences_path=os.path.join(get_base_path(),'preferences.toml')
    if not os.path.exists(preferences_path):
        return False
    
    settings=load_settings()
    if category in settings:
        if option in settings[category]:
            value = settings[category][option]
            if value == "" or value is None:
                return False 
            return value
        return False    
    return False

def to_do_after_conversion(behaviour: int, files_paths: list | str)-> bool | str:
    """
    Function that execute the selected behaviour after the conversion of files
    Args:
        behaviour: indicate the selected beahviour
        files_path: tuple or string with the paths of converted files
    Returns:
        str: the conversion key if behaviour is 3 and files were saved successfully.
        True: if the operation completed successfully.
        False: if an invalid behaviour was provided or an error occurred.
    """
    if behaviour==1: #elimina tutti i file precedenti
        for el in files_paths:
            if os.path.exists(el):
                os.remove(el)
        return True
    elif behaviour==2:  #mantieni i files precedenti (default)
        return True
    elif behaviour==3:  #salva i files e cancellali in seguito
        return write_cancellation_log(files_paths)
        
    else:
        return False
    
def write_cancellation_log(list_of_path : list | None =None)->bool | str:
    """
    Function to write in file cancellation_log.json
    Args:
        list_of_path: list of files_path to write
    Return:
        str: the key of the conversion entry if files were written successfully.
        True: if the file was created successfully without writing any conversion.
        False: if an error occurred.
    Raises:
        OSError : if cancellation_log.json is not found
    """
    
    adesso = datetime.datetime.now()    #ottengo data e ora attuali
    text = adesso.strftime("Conversione del giorno %d/%m/%Y alle ore %H:%M:%S")   #titolo di una conversione
    cancellation_log_path=os.path.join(get_base_path(),'cancellation_log.json')
    if not os.path.exists(cancellation_log_path):
        try:
            with open(cancellation_log_path, "w") as file:
                json.dump({'Torna alla home' : 'Torna alla home'}, file, indent=4)
                return True
        except OSError as e:
            print(f'Errore nel file cancellation_log.json: {e}')
            return False
    else:
        try:
            with open(cancellation_log_path, "r") as file:
                data=json.load(file)
        except OSError as e:
            print(f'Errore nel file cancellation_log.json: {e}')
            return False
        if list_of_path:
            data[text]=list_of_path
            try:
                with open(cancellation_log_path,'w') as file:
                    json.dump(data,file,indent=4)
            except OSError as e:
                print(f'Errore nel file cancellation_log.json:{e}')
                return False
        return text
    return True
        
        
def load_cancellation_log(key_to_delete: str | None = None, delete_files: bool =True)-> bool:
    """
    Function to delete the files saved in cancellation_log.json.
    Args:
        key_to_delete: if provided, deletes only the entry with this key from the log
                    without prompting the user. If None, shows the full log and
                    lets the user choose which conversion to delete.
        delete_files: if True, physically deletes the files from disk before removing
                    the entry from the log. If False, only removes the entry from
                    the log without touching the files. Default is True.
    Returns:
        True if the operation completed successfully.
        False if an error occurred or no conversions are pending.
    Raises:
        OSError: if cancellation_log.json cannot be read or written.
    """
    
    cancelled=True
    cancellation_log_path=os.path.join(get_base_path(),'cancellation_log.json')
    try:
        with open(cancellation_log_path, "r") as file:
            data=json.load(file)
    except OSError as e:
            print(f'Cancellation_log.json non trovato: {e}')
            return False
    if key_to_delete:
            if key_to_delete in data:
                if delete_files: #elimina i files se richiesto
                    for path in data[key_to_delete]:
                        if os.path.exists(path):
                            os.remove(path)
                del data[key_to_delete]
                try:
                    with open(cancellation_log_path, 'w') as file:
                        json.dump(data, file, indent=4)
                    return True
                except OSError as e:
                    print(f'Errore nel file cancellation_log.json: {e}')
                    return False
        
    print('Questa è la lista delle conversioni fatte dove non sono stati cancellati i files vecchi:')
    conversion_choosed=create_menu(message='Scegli di quale conversione cancellare i files',dictio=data,return_the_keys=True)
    if conversion_choosed and conversion_choosed!='Torna alla home':
        all_paths_exist=True #se diventa false levo dal dizionario la conversione ma stampo che i file devono essere rimossi manualmente
        for path in data[conversion_choosed]:
            if not os.path.exists(path):
                print('Un file è stato spostato o eliminato manualmente, impossibile completare l\'operazione')
                print('è necessario cancellare manualmente i files vecchi')
                cancelled=False
                all_paths_exist=False 
                break
        if all_paths_exist:
            for path in data[conversion_choosed]:
                os.remove(path)

        del data[conversion_choosed]  #cancello la conversione relativa ai file cancellati
        try:    #riscrivo il file json
            with open(cancellation_log_path,'w') as file:
                json.dump(data,file,indent=4)
        except FileNotFoundError as e:
            print(f'Cancellation_log.json non trovato: {e}')
            return False
        if cancelled:
            print('I files vecchi sono stati eliminati correttamente')
        return cancelled
    elif conversion_choosed=='Torna alla home':
        return True
    else:
        print('Non ci sono conversioni in sospeso')
        return False
       


def get_video_codec(file_path : str)-> str |None:
    """
    Function to read a video file and extract codec 
    Args:
        file_path : it's the path of video file
    """
    command = [     #comando che chiama ffprobe
        "ffprobe",
        "-v", "error",                          
        "-select_streams", "v:0",                
        "-show_entries", "stream=codec_name",    
        "-of", "default=noprint_wrappers=1:nokey=1", 
        file_path
    ]
    
    try:

        result = subprocess.run(command, capture_output=True, text=True, check=True)
        codec = result.stdout.strip()
        return codec
    except subprocess.CalledProcessError as e:
        print(f"Errore durante la lettura del codec: {e}")
        return None
    except FileNotFoundError:
        print("ffprobe non trovato — assicurarsi che ffmpeg sia installato correttamente")
        return None
    except OSError as e:
        print(f"Errore di sistema durante la lettura del codec: {e}")
        return None     
    