import platform
import os
import tkinter
import shutil
from tkinter import filedialog
import sys
import subprocess


################################################################################################################################

def chose_file() -> tuple | str:
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

def chose_directory() -> str:
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