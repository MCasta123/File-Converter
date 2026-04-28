# **Convertitore Universale Multi-Formato**

Un'applicazione desktop basata su Python per la gestione e conversione di file PDF, immagini e video. 

### **Funzionalità**

**PDF:**

-Conversione in PDF/A-1b

-Compressione del pdf con tre livelli di qualità

-Unione di più pdf in uno singolo

**Immagini:**

-Conversione di una o più immagini in pdf

-Compressione dell'immagine

-Conversione in JPG

**Video:**

-Conversione in MP4

-Compressione del video con tre livelli di qualità

### **Requisiti Tecnici**

-Dipendenze Python

-Per eseguire il codice sorgente, è necessario installare le seguenti librerie:

pip install pillow pikepdf pillow_heif

Il progetto si appoggia ai seguenti motori esterni motori esterni per l'elaborazione dei media.

**Ghostscript**: Necessario per l'unione e la compressione dei PDF.

Scarica l'eseguibile da Ghostscript Downloads.

Estrai o installa il contenuto e inserisci la cartella di installazione rinominandola in gs all'interno della directory principale del progetto (il percorso atteso è gs/bin/gswin64c.exe).

**FFmpeg**: Necessario per la gestione dei video.

Scarica l'eseguibile da FFmpeg.org.

Inserisci il file ffmpeg.exe direttamente nella cartella principale del progetto.
