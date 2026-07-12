#!/bin/bash
cd "$(dirname "$0")"

echo "=== Pulizia build precedenti ==="
rm -rf build dist *.spec

echo "=== Build App con PyInstaller ==="
python3 -m PyInstaller \
    --name "ComicConvert" \
    --icon "ComicConverter.icns" \
    --windowed \
    --onedir \
    --add-data "ComicConverter.icns:." \
    --add-binary "/usr/local/bin/unar:." \
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
xattr -cr dist/ComicConvert.app

echo "=== Creazione DMG ==="
rm -f build/ComicConverter_1.2.dmg
mkdir -p build
hdiutil create \
    -volname "ComicConvert 1.2" \
    -srcfolder dist/ComicConvert.app \
    -ov \
    -format UDZO \
    build/ComicConverter_1.2.dmg

if [ $? -eq 0 ]; then
    echo ""
    echo "=== SUCCESSO! ==="
    echo "DMG creato: $(pwd)/build/ComicConverter_1.2.dmg"
    ls -lh build/ComicConverter_1.2.dmg
else
    echo "ERRORE: Creazione DMG fallita!"
fi
