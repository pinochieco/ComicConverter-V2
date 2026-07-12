#!/bin/bash
cd /Users/pinochieco/Documents/Developer/Cbr2Cbz
rm -rf build dist
python3 -m PyInstaller --name "ComicConvert" --icon "ComicConverter.icns" --windowed --onedir --add-data "ComicConverter.icns:." --add-binary "/usr/local/bin/unar:." --hidden-import "PyQt5.sip" --hidden-import "PIL" --hidden-import "PIL._imaging" --hidden-import "fitz" --hidden-import "pymupdf" --clean --noconfirm --osx-bundle-identifier "com.pinochieco.comicconvert" cbr2cbz.py
