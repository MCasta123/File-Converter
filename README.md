Convertitore Universale Multi-Formato
Un'applicazione desktop basata su Python per la gestione e conversione di file PDF, immagini e video. Il software offre un'interfaccia grafica (GUI) intuitiva per eseguire operazioni comuni come la compressione, l'unione di file e il cambio di formato.

Funzionalità
PDF:
-Conversione PDF/A-1b: Ottimizzazione per l'archiviazione a lungo termine.

-Compressione: Riduzione del peso del file con tre livelli di qualità.

-Unione (Merge): Unione di più file PDF in un unico documento.

Immagini:
-Conversione in PDF: Trasforma immagini singole o multiple (unite) in documenti PDF.

-Compressione: Ottimizzazione del peso (JPG/PNG).

-Conversione in JPG: Conversione rapida da altri formati (PNG, HEIC, ecc.).

Video:
-Conversione in MP4: Standardizzazione dei video.

-Compressione: Riduzione delle dimensioni tramite codec H.264 (CRF variabile).

Requisiti Tecnici
Dipendenze Python
Per eseguire il codice sorgente, è necessario installare le seguenti librerie:


pip install pillow pikepdf
Strumenti Esterni:
Il progetto si appoggia a motori esterni per l'elaborazione dei media. Questi file non sono inclusi nel repository per motivi di licenza e dimensioni.

Ghostscript: Necessario per l'unione e la compressione dei PDF.

Scarica l'eseguibile da Ghostscript Downloads.

Estrai o installa il contenuto e inserisci la cartella di installazione rinominandola in gs all'interno della directory principale del progetto (il percorso atteso è gs/bin/gswin64c.exe).

FFmpeg: Necessario per la gestione dei video.

Scarica l'eseguibile da FFmpeg.org.

Inserisci il file ffmpeg.exe direttamente nella cartella principale del progetto.

Licenza:
Questo progetto è distribuito sotto licenza MIT. Consulta il file LICENSE per ulteriori dettagli.