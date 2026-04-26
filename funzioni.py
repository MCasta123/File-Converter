import tkinter
import shutil
from tkinter import filedialog
import os
import glob
import sys

################################################################################################################################

def chose_file():
    root = tkinter.Tk()
    root.withdraw() #creato finestra e nascosta
    root.attributes('-topmost', True)
 #Apri l'Esplora Risorse vero e proprio
    file_path = filedialog.askopenfilenames(
        title="Seleziona i file da convertire",
        filetypes=[("TUTTI I FILE","*.*"),("PDF", "*.pdf"),("IMMAGINI","*.jpg *.jpeg *.png *.HEIC"),("VIDEO","*.mp4 *.mov")]
    )
    root.destroy()  #distruggo finestra
    return file_path

#####################################################################################################################################

def save_as(estensione):
    root = tkinter.Tk()
    root.withdraw() #creato finestra e nascosta
    root.attributes('-topmost', True)
    saving_path = filedialog.asksaveasfilename(title="Salva file convertito come...",defaultextension=estensione)
    root.destroy()
    return saving_path

####################################################################################################################################à##

def chose_directory():
    root=tkinter.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    saving_directory=filedialog.askdirectory(title='Scegli cartella in cui salvare..')
    root.destroy()
    return saving_directory

#######################################################################################################################################

def search_executable(executable_name, pattern_windows_fallback=None):
    """
    Cerca un eseguibile nel sistema in questo ordine:
    1. PATH di sistema
    2. Percorsi standard (Windows)
    3. Chiede all'utente
    """
   
    str_executable_name = str(executable_name)

    path = shutil.which(str_executable_name)
    if path:
        return path
        
    if os.name == 'nt' and pattern_windows_fallback:
        for pattern in pattern_windows_fallback:
            results = glob.glob(pattern)
            if results:
                return results[0] # Ritorna il primo trovato
                
    #Chiediamo all'utente
    print(f"\n[!] Non riesco a trovare l'eseguibile: {str_executable_name}")
    print("Selezionalo manualmente dalla finestra che sta per aprirsi...")
    
    root = tkinter.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    manual_path = filedialog.askopenfilename(
        title=f"Trova {str_executable_name}",
        filetypes=[("Eseguibili", "*.exe")] if os.name == 'nt' else [("Tutti i file", "*.*")]
    )
    root.destroy()
    
    if manual_path:
        return manual_path
    else:
        raise FileNotFoundError(f"L'eseguibile {str_executable_name} è strettamente necessario per continuare.")
    
#######################################################################################################################################

def get_base_path():
    """ 
    Restituisce il path assoluto in cui si trova il programma,
    sia che sia eseguito come script .py, sia come .exe compilato. 
    """
    if getattr(sys, 'frozen', False):
        # Se stiamo girando come .exe compilato
        return os.path.dirname(sys.executable)
    else:
        # Se stiamo girando come normale script .py
        return os.path.dirname(os.path.abspath(__file__))