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

Scaricare l'eseguibile dalla sezione **Releases** della repository. Nessuna installazione aggiuntiva richiesta — GhostScript e FFmpeg sono già inclusi nel pacchetto. Avviare direttamente il file `.exe`.

---

### Utenti finali — Linux

Su Linux non è disponibile un eseguibile precompilato. È necessario eseguire il programma tramite Python, ma non sono richieste conoscenze tecniche particolari — seguire i passi qui sotto.

**1. Installare Python 3.11 o superiore** (se non già presente):

```bash
# Ubuntu / Debian
sudo apt install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip
```

**2. Installare le dipendenze Python:**

```bash
pip install pillow pikepdf pillow-heif
```

**3. Installare GhostScript, FFmpeg e Zenity:**

Ubuntu / Debian e derivate:
```bash
sudo apt update
sudo apt install ffmpeg ghostscript zenity
```

Fedora e derivate:
```bash
sudo dnf install ghostscript zenity
```

> **Nota per utenti Fedora:** La versione `ffmpeg-free` inclusa nei repository ufficiali non include i codec H.264 necessari. È necessario installare FFmpeg dai repository RPM Fusion:
> ```bash
> sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
> sudo dnf install ffmpeg
> ```
> Per verificare che i codec siano stati installati correttamente:
> ```bash
> ffmpeg -encoders | grep libx264
> ```

**4. Avviare il programma:**

```bash
python main.py
```

---

### Sviluppatori — Windows e Linux

Questa sezione è rivolta a chi vuole modificare o estendere il codice sorgente, o compilare l'eseguibile Windows.

**1. Clonare la repository:**

```bash
git clone <url_repository>
cd <nome_cartella>
```

**2. Installare le dipendenze Python:**

```bash
pip install pillow pikepdf pillow-heif pyinstaller
```

**3. Installare GhostScript e FFmpeg:**

Su **Linux** seguire le stesse istruzioni della sezione utenti finali Linux qui sopra.

Su **Windows** i due eseguibili devono essere posizionati manualmente nella cartella del progetto con la seguente struttura:

```
progetto/
├── main.py
├── classi.py
├── funzioni.py
├── config.toml
├── ffmpeg.exe                  ← file eseguibile FFmpeg
└── gs/
    └── bin/
        └── gswin64c.exe        ← file eseguibile GhostScript
```

- GhostScript per Windows: [Ghostscript Downloads](https://www.ghostscript.com/releases/gsdnld.html)
- FFmpeg per Windows: [FFmpeg.org](https://ffmpeg.org/download.html)

**4. Avviare il programma in modalità sviluppo:**

```bash
python main.py
```
