#!/bin/bash
# Lancia l'app standalone CBR2CBZ
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_PATH="$DIR/dist/CBR2CBZ.app"

if [ -d "$APP_PATH" ]; then
    echo "Avvio CBR2CBZ..."
    open "$APP_PATH"
else
    echo "App non trovata. Eseguo il sorgente Python..."
    cd "$DIR"
    python3 cbr2cbz.py
fi
