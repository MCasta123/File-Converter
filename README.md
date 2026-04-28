# Convertitore Universale Multi-Formato

Applicazione desktop basata su Python progettata per la gestione e la conversione di file PDF, immagini e video. Il software è compatibile con Windows e Linux e adatta automaticamente la propria interfaccia e i motori di elaborazione in base al sistema operativo rilevato.

### Funzionalità

**PDF**
- Conversione in formato PDF/A-1b (standard per l'archiviazione a lungo termine).
- Compressione del PDF con tre livelli di qualità (Alta, Media, Bassa).
- Unione di più file PDF in un unico documento.

**Immagini**
- Conversione di una o più immagini in un unico file PDF.
- Compressione intelligente delle immagini.
- Conversione in formato JPG con supporto nativo per il formato Apple HEIC.

**Video**
- Conversione di file video in formato MP4 (codec H.264).
- Compressione video con tre livelli di intensità per bilanciare qualità e peso del file.

---

### Requisiti Tecnici

#### Dipendenze Python
Per eseguire il codice sorgente è necessario installare le seguenti librerie tramite terminale:

pip install pillow pikepdf pillow-heif

#### Motori esterni

Il programma utilizza Ghostscript per la gestione dei PDF e FFmpeg per l'elaborazione dei video. L'installazione dipende dal sistema operativo in uso.

###### - Sistemi Windows

Il software cerca gli esegubili all'interno della cartella del progetto o nei percorsi di sistema predefiniti:

Ghostscript: Scaricare l'eseguibile da Ghostscript Downloads. Inserire la cartella di installazione nella directory principale del progetto rinominandola in "gs" (il percorso atteso è gs/bin/gswin64c.exe).

FFmpeg: Scaricare l'eseguibile da FFmpeg.org e inserire il file ffmpeg.exe direttamente nella cartella principale del progetto.

###### - Sistemi Linux (Fedora, Ubuntu, Debian e derivate)

 Non è necessario scaricare manualmente gli eseguibili, ma vanno installati tramite il gestore pacchetti:

Per distribuzioni basate su Debian/Ubuntu:

sudo apt update
sudo apt install ffmpeg ghostscript zenity

Per distribuzioni basate su Fedora:

sudo dnf install ffmpeg ghostscript zenity

Nota per utenti Fedora: Per la compressione e conversione video, è necessario installare la versione completa di FFmpeg dai repository RPM Fusion. La versione "ffmpeg-free" preinstallata non include i codec H.264 necessari per il funzionamento dell'applicazione.

Utilizzo
L'applicazione può essere avviata tramite lo script principale:


python main.py



Per quanto riguarda i requisiti video su Fedora, se dovessi avere ancora problemi con i codec dopo il cambio di repository, puoi verificare che i pacchetti necessari siano attivi con il comando `ffmpeg -encoders | grep libx264` nel terminale.