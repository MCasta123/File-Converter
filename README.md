# Convertitore Universale Multi-Formato

Applicazione desktop basata su Python progettata per la gestione e la conversione di file PDF, immagini e video. Il software è compatibile con Windows e Linux e adatta automaticamente la propria interfaccia e i motori di elaborazione in base al sistema operativo rilevato.

---

## Funzionalità

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

## Utilizzo

### Utenti finali — Windows
Scaricare l'eseguibile dalla sezione **Releases** della repository. Nessuna installazione aggiuntiva richiesta — GhostScript e FFmpeg sono già inclusi nel pacchetto.

### Utenti finali — Linux
Su Linux non è disponibile un eseguibile precompilato. Seguire le istruzioni nella sezione [Installazione per sviluppatori](#installazione-per-sviluppatori) qui sotto.

---

## Installazione per sviluppatori

Questa sezione è rivolta a chi vuole eseguire o modificare il codice sorgente direttamente.

### 1. Dipendenze Python

Installare le librerie necessarie tramite pip:

```bash
pip install pillow pikepdf pillow-heif
```

### 2. Motori esterni

Il programma si affida a **GhostScript** per la gestione dei PDF e **FFmpeg** per l'elaborazione dei video. Su Linux vanno installati tramite il gestore pacchetti di sistema.

#### Ubuntu / Debian e derivate

```bash
sudo apt update
sudo apt install ffmpeg ghostscript zenity
```

#### Fedora e derivate

```bash
sudo dnf install ghostscript zenity
```

Per FFmpeg su Fedora è necessario abilitare i repository **RPM Fusion**, in quanto la versione `ffmpeg-free` inclusa nei repo ufficiali non include i codec H.264 necessari:

```bash
sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install ffmpeg
```

Per verificare che i codec siano stati installati correttamente:

```bash
ffmpeg -encoders | grep libx264
```

### 3. Avvio

```bash
python main.py
```

---

## Compilazione dell'eseguibile (Windows)

Per generare il file `.exe` distribuibile è necessario avere installato **PyInstaller**:

```bash
pip install pyinstaller
```

Prima di compilare, assicurarsi che nella cartella del progetto siano presenti:
- La cartella `gs/` contenente GhostScript (percorso atteso: `gs/bin/gswin64c.exe`)
- Il file `ffmpeg.exe` nella cartella principale del progetto

GhostScript per Windows può essere scaricato da [Ghostscript Downloads](https://www.ghostscript.com/releases/gsdnld.html).
FFmpeg per Windows può essere scaricato da [FFmpeg.org](https://ffmpeg.org/download.html).

Per compilare:

```bash
pyinstaller --onedir main.py
```