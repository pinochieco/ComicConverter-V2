from setuptools import setup

setup(
    app=['cbr2cbz.py'],
    name='CBR2CBZ',
    options={
        'py2app': {
            'argv_emulation': False,
            'iconfile': 'cbrcbz2pdf.icns',
            'plist': {
                'CFBundleName': 'CBR2CBZ',
                'CFBundleDisplayName': 'CBR2CBZ',
                'CFBundleIdentifier': 'com.pinochieco.cbr2cbz',
                'CFBundleVersion': '2.0.0',
                'CFBundleShortVersionString': '2.0.0',
                'NSHighResolutionCapable': True,
            },
            'packages': ['PyQt5'],
            'excludes': [
                'tkinter', 'customtkinter', 'PyQt5.uic',
                'PyQt5.QtWebEngineWidgets', 'PyQt5.QtWebKit',
                'PyQt5.QtSensors', 'PyQt5.Qt3D',
                'PyQt5.QtBluetooth', 'PyQt5.QtNfc',
                'PyQt5.QtPositioning', 'PyQt5.QtLocation',
                'PyQt5.QtMultimedia', 'PyQt5.QtMultimediaWidgets',
                'PyQt5.QtXml', 'PyQt5.QtXmlPatterns',
                'PyQt5.QtHelp', 'PyQt5.QtTest',
                'PyQt5.QtDBus', 'PyQt5.QtDesigner',
            ],
            'site_packages': True,
        }
    },
    setup_requires=['py2app'],
)
