import platform
import os
import tkinter
import shutil
from tkinter import filedialog
import sys
import subprocess
import tomllib
import tomlkit
import questionary
from questionary import Choice


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
    
    
    if os.path.exists(preferences_path):    #file già creato
        try:
            with open(preferences_path, "r", encoding="utf-8") as f:
                preferences=tomlkit.load(f)
                return preferences
        except tomllib.TOMLDecodeError as e:
            print(f'Errore: preferences.toml non è valido: {e}')
            sys.exit(1)
    
    else:   #si crea il file
        settings="""
        #impostazioni
        [pdf]
        pdf_compression_quality=""
        
        [image]
        
        [video]
        video_compression_quality=""
        
        [general]
        after_conversion=""
        """
        with open(preferences_path,'w') as f:
            f.write(settings)
            
        try:
            with open(preferences_path, "r", encoding="utf-8") as f:
                preferences=tomlkit.load(f)
        except tomllib.TOMLDecodeError as e:
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
            category_list=list(settings.keys())
            if category in category_list:
                change_list=list(settings[category].keys())
                if key in change_list:
                    settings[category][key]=value
                    try:
                        with open("preferences.toml", "w", encoding="utf-8") as f:
                            tomlkit.dump(settings, f)
                            return True
                    except ValueError as e:
                        print(f'Errore nella modifica : {e}') 
        
    except ValueError as e:
        print(f'Errore nell\' apertura del file preferences.toml: {e}')
    return False
    
def choose_from_dictionary(dictio : dict, message : str | None, dictionary_of_alias : dict | None =None, return_the_keys : bool =False) -> str | int:
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
    if dictio:
        list_of_actions=[]
        for action in dictio:
            list_of_actions.append(action)
        available_actions=[]
        alias=False #variabile che mi dice se tutto va bene e posso usare l'alias
        if dictionary_of_alias: #solo se ho passato un alias
            if len(dictio)==len(dictionary_of_alias):
                keys_of_dictio=list(dictio.keys())
                keys_of_dictionary_of_alias=list(dictionary_of_alias.keys())
                if set(keys_of_dictio)==set(keys_of_dictionary_of_alias): #trasformo in set dove non conta l'ordine e posso controllare che siano uguali 
                   alias=True 
                    
        for el in list_of_actions:
            element=el
            if alias==True:
                element=dictionary_of_alias[el]
            if return_the_keys: 
                available_actions.append(Choice(title=element,value=el))
            else:
                available_actions.append(Choice(title=element,value=dictio[el]))
        value=questionary.select(message,choices=available_actions).ask()
        return value
    else: 
        return ''
    
    
    
    