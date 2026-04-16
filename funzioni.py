import tkinter
import shutil
from tkinter import filedialog
import os
import glob
import sys

################################################################################################################################

def scegliFile():
    root = tkinter.Tk()
    root.withdraw() #creato finestra e nascosta
    root.attributes('-topmost', True)
 #Apri l'Esplora Risorse vero e proprio
    percorso_file = filedialog.askopenfilenames(
        title="Seleziona i file da convertire",
        filetypes=[("TUTTI I FILE","*.*"),("PDF", "*.pdf"),("IMMAGINI","*.jpg *.jpeg *.png *.HEIC"),("VIDEO","*.mp4 *.mov")]
    )
    root.destroy()  #distruggo finestra
    return percorso_file

#####################################################################################################################################

def salvaConNome(estensione):
    root = tkinter.Tk()
    root.withdraw() #creato finestra e nascosta
    root.attributes('-topmost', True)
    percorso_salvataggio = filedialog.asksaveasfilename(title="Salva file convertito come...",defaultextension=estensione)
    root.destroy()
    return percorso_salvataggio

####################################################################################################################################à##

def scegliCartella():
    root=tkinter.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    cartellaSalvataggio=filedialog.askdirectory(title='Scegli cartella in cui salvare..')
    root.destroy()
    return cartellaSalvataggio

#######################################################################################################################################

def trova_eseguibile(nome_eseguibile, pattern_windows_fallback=None):
    """
    Cerca un eseguibile nel sistema in questo ordine:
    1. PATH di sistema
    2. Percorsi standard (Windows)
    3. Chiede all'utente
    """
   
    nome_eseguibile_str = str(nome_eseguibile)

    percorso = shutil.which(nome_eseguibile_str)
    if percorso:
        return percorso
        
    if os.name == 'nt' and pattern_windows_fallback:
        for pattern in pattern_windows_fallback:
            risultati = glob.glob(pattern)
            if risultati:
                return risultati[0] # Ritorna il primo trovato
                
    #Chiediamo all'utente
    print(f"\n[!] Non riesco a trovare l'eseguibile: {nome_eseguibile_str}")
    print("Selezionalo manualmente dalla finestra che sta per aprirsi...")
    
    root = tkinter.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    percorso_manuale = filedialog.askopenfilename(
        title=f"Trova {nome_eseguibile_str}",
        filetypes=[("Eseguibili", "*.exe")] if os.name == 'nt' else [("Tutti i file", "*.*")]
    )
    root.destroy()
    
    if percorso_manuale:
        return percorso_manuale
    else:
        raise FileNotFoundError(f"L'eseguibile {nome_eseguibile_str} è strettamente necessario per continuare.")
    
#######################################################################################################################################

def ottieni_percorso_base():
    """ 
    Restituisce il percorso assoluto in cui si trova il programma,
    sia che sia eseguito come script .py, sia come .exe compilato. 
    """
    if getattr(sys, 'frozen', False):
        # Se stiamo girando come .exe compilato
        return os.path.dirname(sys.executable)
    else:
        # Se stiamo girando come normale script .py
        return os.path.dirname(os.path.abspath(__file__))