#!/bin/bash
# ============================================================
# Build ComicConverter 1.5 — App + DMG con alias Applicazioni
# ============================================================
cd "$(dirname "$0")"

APP_NAME="ComicConverter"
APP_VERSION="1.5"
ICON_FILE="ComicConverter.icns"
DMG_NAME="${APP_NAME}_${APP_VERSION}"

echo "=== Pulizia build precedenti ==="
rm -rf build dist *.spec

echo "=== Verifica presenza unar ==="
if [ ! -f "/usr/local/bin/unar" ]; then
    echo "ATTENZIONE: unar non trovato in /usr/local/bin/unar"
    echo "Provo a trovarlo con 'which unar'..."
    UNAR_PATH=$(which unar 2>/dev/null)
    if [ -z "$UNAR_PATH" ]; then
        echo "ERRORE: unar non trovato. Installalo con: brew install unar"
        exit 1
    fi
    echo "unar trovato in: $UNAR_PATH"
    UNAR_BINARY="$UNAR_PATH"
else
    UNAR_BINARY="/usr/local/bin/unar"
fi

echo "=== Build App con PyInstaller ==="
python3 -m PyInstaller \
    --name "$APP_NAME" \
    --icon "$ICON_FILE" \
    --windowed \
    --onedir \
    --add-data "$ICON_FILE:." \
    --add-binary "$UNAR_BINARY:." \
    --hidden-import "PyQt5.sip" \
    --hidden-import "PIL" \
    --hidden-import "PIL._imaging" \
    --hidden-import "fitz" \
    --hidden-import "pymupdf" \
    --clean \
    --noconfirm \
    --osx-bundle-identifier "com.pinochieco.comicconvert" \
    cbr2cbz.py

if [ $? -ne 0 ]; then
    echo "ERRORE: PyInstaller build fallito!"
    exit 1
fi

echo "=== Rimozione attributi di quarantena ==="
xattr -cr "dist/$APP_NAME.app"

echo "=== Crea cartella temporanea per il DMG ==="
DMG_TMP="build/dmg_tmp"
rm -rf "$DMG_TMP"
mkdir -p "$DMG_TMP"

echo "=== Copia App nella cartella temporanea ==="
cp -R "dist/$APP_NAME.app" "$DMG_TMP/"

echo "=== Crea alias per la cartella Applicazioni ==="
ln -s /Applications "$DMG_TMP/Applications"

echo "=== Creazione DMG ==="
rm -f "build/$DMG_NAME.dmg"

hdiutil create \
    -volname "$APP_NAME $APP_VERSION" \
    -srcfolder "$DMG_TMP" \
    -ov \
    -format UDZO \
    -fs HFS+ \
    "build/$DMG_NAME.dmg"

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================"
    echo "  ✅ SUCCESSO!"
    echo "  DMG creato: $(pwd)/build/$DMG_NAME.dmg"
    echo "============================================"
    ls -lh "build/$DMG_NAME.dmg"
    
    # Pulizia tmp
    rm -rf "$DMG_TMP"
    
    echo ""
    echo "Per installare: apri il DMG e trascina ComicConverter.app su Applications"
else
    echo "ERRORE: Creazione DMG fallita!"
    exit 1
fi
