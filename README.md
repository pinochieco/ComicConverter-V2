# CBR2CBZ - Convertitore CBR/CBZ/PDF per macOS

[!["Interfaccia"](screenshot.png)](screenshot.png)

Applicazione macOS standalone per convertire fumetti digitali tra formati **CBR**, **CBZ** e **PDF**.

## ✨ Funzionalità

- **CBR → CBZ** - Converti archivi RAR in ZIP
- **CBR → PDF** - Converti CBR direttamente in PDF
- **CBZ → PDF** - Converti CBZ in PDF
- **Interfaccia nativa macOS** con tema scuro professionale (PyQt5)
- **Selezione formato input**: solo CBR, solo CBZ, o entrambi
- **Cartella output** personalizzabile
- **Scansione ricorsiva** delle sottocartelle
- **Anteprima** del file in elaborazione
- **Barra di progresso** e stato in tempo reale
- **Eliminazione automatica** degli originali (opzionale)

## 📦 Download

Scarica l'ultima versione dalla sezione [Releases](https://github.com/UTENTE/CBR2CBZ/releases).

### Requisiti

- macOS 11 (Big Sur) o superiore
- **unar** (installato automaticamente via Homebrew se necessario)

### Installazione rapida

1. Scarica `CBR2CBZ.dmg` dall'ultima release
2. Trascina l'app nella cartella `Applicazioni`
3. Fai doppio click per avviare

## 🔧 Build da sorgente

```bash
# Clona il repository
git clone https://github.com/UTENTE/CBR2CBZ.git
cd CBR2CBZ

# Installa dipendenze
pip3 install PyQt5 Pillow pyinstaller

# Crea l'app standalone
python3 -m PyInstaller CBR2CBZ.spec

# L'app si trova in:
open dist/CBR2CBZ.app
```

## 📁 Struttura del progetto

```
CBR2CBZ/
├── cbr2cbz.py              # Codice sorgente principale
├── cbrcbz2pdf.icns         # Icona dell'applicazione
├── setup.py                # Build con py2app (alternativa)
├── Avvia_Cbr2CBZ.command   # Script di avvio rapido
├── requirements.txt        # Dipendenze Python
├── README.md               # Questo file
└── dist/
    └── CBR2CBZ.app         # App standalone (dopo build)
```

## 🛠 Tecnologie

- **Python 3.9+**
- **PyQt5** - Interfaccia grafica nativa macOS
- **Pillow (PIL)** - Elaborazione immagini e creazione PDF
- **unar** - Estrazione archivi RAR
- **PyInstaller** - Creazione app standalone

## 📄 Licenza

Distribuito sotto licenza MIT. Vedi il file `LICENSE` per maggiori informazioni.

---

*Creato con ❤️ per gli appassionati di fumetti digitali*
