import tkinter
import shutil
from tkinter import filedialog
import os
import glob
import sys

################################################################################################################################

def chose_file() -> tuple:
    """
    Opens a file dialog to select one or more files.

    Returns:
        A tuple of absolute file paths selected by the user.
        Returns an empty tuple if the user cancels.
    """
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

def save_as(estensione: str) -> str:
    """
    Opens a save dialog to choose where to save the output file.

    Args:
        estensione: Default file extension for the saved file (e.g. '.pdf').

    Returns:
        The absolute path chosen by the user, or an empty string if cancelled.
    """
    root = tkinter.Tk()
    root.withdraw() #creato finestra e nascosta
    root.attributes('-topmost', True)
    saving_path = filedialog.asksaveasfilename(title="Salva file convertito come...",defaultextension=estensione)
    root.destroy()
    return saving_path

####################################################################################################################################

def chose_directory() -> str:
    """
    Opens a dialog to choose a destination folder.

    Returns:
        The absolute path of the chosen directory, or an empty string if cancelled.
    """
    root=tkinter.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    saving_directory=filedialog.askdirectory(title='Scegli cartella in cui salvare..')
    root.destroy()
    return saving_directory

#######################################################################################################################################

def search_executable(executable_name: str, pattern_windows_fallback: list | None = None) -> str:
    """
    Searches for an executable in the system in the following order:
    1. System PATH
    2. Common Windows paths (fallback patterns)
    3. Manual selection via file dialog

    Args:
        executable_name: Name of the executable to search for (e.g. 'ffmpeg').
        pattern_windows_fallback: List of glob patterns to try on Windows if PATH search fails.

    Returns:
        The absolute path to the found executable.

    Raises:
        FileNotFoundError: If the executable cannot be found and the user cancels the manual selection.
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