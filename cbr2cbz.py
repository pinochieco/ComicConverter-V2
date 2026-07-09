#!/usr/bin/env python3
"""
CBR2CBZ v2.0 - Convertitore CBR/CBZ con interfaccia PyQt5
Supporta: CBR->CBZ, CBR->PDF, CBZ->PDF
"""

import os, sys, shutil, tempfile, zipfile, subprocess, threading
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QCheckBox, QProgressBar,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
    QFrame, QSplitter, QScrollArea, QTextEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap


class Segnali(QObject):
    """Segnali per comunicazione thread-safe con la GUI"""
    aggiorna_stato = pyqtSignal(str)
    aggiorna_file = pyqtSignal(str, str)  # nome file, stato
    aggiorna_progresso = pyqtSignal(int, int)  # corrente, totale
    fine_conversione = pyqtSignal(int, int)


class Convertitore:
    """Gestisce le conversioni in un thread separato"""
    
    def __init__(self, segnali):
        self.segnali = segnali
    
    def converti(self, files, formato_output, elimina, cartella_output=""):
        totale = len(files)
        ok = 0
        errs = 0
        
        for i, f in enumerate(files):
            self.segnali.aggiorna_file.emit(f.name, "Elaborazione...")
            self.segnali.aggiorna_stato.emit(f"Convertendo: {f.name}")
            
            try:
                if f.suffix.lower() == ".cbr":
                    if formato_output == "CBZ":
                        risultato = self._cbr_in_cbz(f, cartella_output)
                    else:  # PDF
                        risultato = self._cbr_in_pdf(f, cartella_output)
                elif f.suffix.lower() == ".cbz":
                    risultato = self._cbz_in_pdf(f, cartella_output)
                else:
                    risultato = (False, "Formato non supportato")
                
                if risultato[0]:
                    ok += 1
                    self.segnali.aggiorna_file.emit(f.name, "OK")
                    if elimina:
                        try:
                            os.remove(str(f))
                            self.segnali.aggiorna_file.emit(f.name, "OK (eliminato)")
                        except:
                            pass
                else:
                    errs += 1
                    self.segnali.aggiorna_file.emit(f.name, f"ERRORE: {risultato[1][:40]}")
            except Exception as e:
                errs += 1
                self.segnali.aggiorna_file.emit(f.name, f"ERRORE")
            
            self.segnali.aggiorna_progresso.emit(i + 1, totale)
        
        self.segnali.fine_conversione.emit(ok, errs)
    
    def _cbr_in_cbz(self, file_in, cartella_out=""):
        tmp = tempfile.mkdtemp(prefix="cbr2cbz_")
        try:
            r = subprocess.run(["unar", "-o", tmp, "-q", str(file_in)],
                               capture_output=True, timeout=120)
            if r.returncode != 0:
                return False, "unar fallito"
            
            immagini = []
            for root, _, files in os.walk(tmp):
                for img in sorted(files):
                    immagini.append(os.path.join(root, img))
            
            if not immagini:
                return False, "Nessuna immagine estratta"
            
            if cartella_out:
                dest = Path(cartella_out) / (file_in.stem + ".cbz")
            else:
                dest = file_in.with_suffix(".cbz")
            
            with zipfile.ZipFile(str(dest), "w", zipfile.ZIP_DEFLATED) as zf:
                for img in immagini:
                    zf.write(img, os.path.basename(img))
            
            return True, "OK"
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    
    def _cbr_in_pdf(self, file_in, cartella_out=""):
        tmp = tempfile.mkdtemp(prefix="cbr2pdf_")
        try:
            r = subprocess.run(["unar", "-o", tmp, "-q", str(file_in)],
                               capture_output=True, timeout=120)
            if r.returncode != 0:
                return False, "unar fallito"
            
            immagini = []
            for root, _, files in os.walk(tmp):
                for img in sorted(files):
                    img_path = os.path.join(root, img)
                    if os.path.isfile(img_path):
                        immagini.append(img_path)
            
            if not immagini:
                return False, "Nessuna immagine estratta"
            
            if cartella_out:
                dest = Path(cartella_out) / (file_in.stem + ".pdf")
            else:
                dest = file_in.with_suffix(".pdf")
            
            # Crea PDF con Pillow
            from PIL import Image
            immagini_pil = []
            for img in immagini:
                try:
                    im = Image.open(img).convert("RGB")
                    immagini_pil.append(im)
                except:
                    continue
            
            if immagini_pil:
                immagini_pil[0].save(str(dest), save_all=True,
                                      append_images=immagini_pil[1:])
                return True, "OK"
            else:
                return False, "Nessuna immagine valida"
        except Exception as e:
            return False, str(e)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    
    def _cbz_in_pdf(self, file_in, cartella_out=""):
        tmp = tempfile.mkdtemp(prefix="cbz2pdf_")
        try:
            with zipfile.ZipFile(str(file_in), "r") as zf:
                zf.extractall(tmp)
            
            immagini = []
            for root, _, files in os.walk(tmp):
                for img in sorted(files):
                    img_path = os.path.join(root, img)
                    if os.path.isfile(img_path):
                        immagini.append(img_path)
            
            if not immagini:
                return False, "Nessuna immagine nell'archivio"
            
            if cartella_out:
                dest = Path(cartella_out) / (file_in.stem + ".pdf")
            else:
                dest = file_in.with_suffix(".pdf")
            
            from PIL import Image
            immagini_pil = []
            for img in immagini:
                try:
                    im = Image.open(img).convert("RGB")
                    immagini_pil.append(im)
                except:
                    continue
            
            if immagini_pil:
                immagini_pil[0].save(str(dest), save_all=True,
                                      append_images=immagini_pil[1:])
                return True, "OK"
            else:
                return False, "Nessuna immagine valida"
        except Exception as e:
            return False, str(e)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Convertitore CBR/CBZ")
        self.setMinimumSize(900, 650)
        self.resize(950, 700)
        
        # Variabili
        self.files_list = []
        self.cartella_output = ""
        self.in_esecuzione = False
        
        # Segnali
        self.segnali = Segnali()
        self.segnali.aggiorna_stato.connect(self._on_stato)
        self.segnali.aggiorna_file.connect(self._on_file_stato)
        self.segnali.aggiorna_progresso.connect(self._on_progresso)
        self.segnali.fine_conversione.connect(self._on_fine)
        
        # Setup UI
        self._setup_ui()
        self._applica_stile()
    
    def _setup_ui(self):
        widget_centrale = QWidget()
        self.setCentralWidget(widget_centrale)
        layout_main = QVBoxLayout(widget_centrale)
        layout_main.setContentsMargins(0, 0, 0, 0)
        layout_main.setSpacing(0)
        
        # === HEADER ===
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(80)
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(20, 12, 20, 10)
        
        titolo = QLabel("Convertitore CBR / CBZ / PDF")
        titolo.setFont(QFont("SF Pro Display", 18, QFont.Bold))
        titolo.setStyleSheet("color: #cba6f7;")
        h_layout.addWidget(titolo)
        
        sottotitolo = QLabel("Converti fumetti tra formati CBR, CBZ e PDF")
        sottotitolo.setFont(QFont("SF Pro Text", 10))
        sottotitolo.setStyleSheet("color: #6c7086;")
        h_layout.addWidget(sottotitolo)
        
        layout_main.addWidget(header)
        
        # === BODY ===
        body = QWidget()
        body.setObjectName("body")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 15, 20, 10)
        body_layout.setSpacing(10)
        
        # -- Riga 1: Input cartella e opzioni --
        riga1 = QHBoxLayout()
        riga1.setSpacing(8)
        
        lbl_cartella = QLabel("Cartella sorgente:")
        lbl_cartella.setFont(QFont("SF Pro Text", 11, QFont.Bold))
        lbl_cartella.setStyleSheet("color: #cdd6f4;")
        riga1.addWidget(lbl_cartella)
        
        self.txt_cartella = QLabel("Nessuna cartella selezionata")
        self.txt_cartella.setFont(QFont("SF Pro Text", 10))
        self.txt_cartella.setStyleSheet("color: #6c7086; background: #313244; padding: 6px 10px; border-radius: 6px;")
        self.txt_cartella.setWordWrap(True)
        riga1.addWidget(self.txt_cartella, 1)
        
        btn_sfoglia = QPushButton("Sfoglia")
        btn_sfoglia.setFont(QFont("SF Pro Text", 11))
        btn_sfoglia.setObjectName("btnSecondario")
        btn_sfoglia.setFixedWidth(100)
        btn_sfoglia.clicked.connect(self._sfoglia)
        riga1.addWidget(btn_sfoglia)
        
        body_layout.addLayout(riga1)
        
        # -- Riga 2: Opzioni conversione --
        riga_opts = QHBoxLayout()
        riga_opts.setSpacing(15)
        
        # Formato input
        lbl_in = QLabel("Formato input:")
        lbl_in.setFont(QFont("SF Pro Text", 10, QFont.Bold))
        lbl_in.setStyleSheet("color: #cdd6f4;")
        riga_opts.addWidget(lbl_in)
        
        self.cmb_input = QComboBox()
        self.cmb_input.addItems(["CBR", "CBZ", "CBR e CBZ"])
        self.cmb_input.setFont(QFont("SF Pro Text", 10))
        self.cmb_input.setObjectName("combo")
        riga_opts.addWidget(self.cmb_input)
        
        # Freccia
        freccia = QLabel("\u2192")
        freccia.setFont(QFont("SF Pro Display", 16, QFont.Bold))
        freccia.setStyleSheet("color: #cba6f7; padding: 0 5px;")
        riga_opts.addWidget(freccia)
        
        # Formato output
        lbl_out = QLabel("Formato output:")
        lbl_out.setFont(QFont("SF Pro Text", 10, QFont.Bold))
        lbl_out.setStyleSheet("color: #cdd6f4;")
        riga_opts.addWidget(lbl_out)
        
        self.cmb_output = QComboBox()
        self.cmb_output.addItems(["CBZ", "PDF"])
        self.cmb_output.setFont(QFont("SF Pro Text", 10))
        self.cmb_output.setObjectName("combo")
        riga_opts.addWidget(self.cmb_output)
        
        riga_opts.addStretch()
        
        self.chk_ricorsivo = QCheckBox("Includi sottocartelle")
        self.chk_ricorsivo.setFont(QFont("SF Pro Text", 10))
        self.chk_ricorsivo.setStyleSheet("color: #cdd6f4;")
        self.chk_ricorsivo.setChecked(True)
        riga_opts.addWidget(self.chk_ricorsivo)
        
        self.chk_elimina = QCheckBox("Elimina originali")
        self.chk_elimina.setFont(QFont("SF Pro Text", 10))
        self.chk_elimina.setStyleSheet("color: #cdd6f4;")
        riga_opts.addWidget(self.chk_elimina)
        
        btn_scan = QPushButton("Scansiona")
        btn_scan.setFont(QFont("SF Pro Text", 11, QFont.Bold))
        btn_scan.setObjectName("btnSecondario")
        btn_scan.setFixedWidth(110)
        btn_scan.clicked.connect(self._scansiona)
        riga_opts.addWidget(btn_scan)
        
        body_layout.addLayout(riga_opts)
        
        # -- Riga 3: Cartella output --
        riga_out = QHBoxLayout()
        riga_out.setSpacing(8)
        
        lbl_out_dir = QLabel("Cartella output (opzionale):")
        lbl_out_dir.setFont(QFont("SF Pro Text", 10, QFont.Bold))
        lbl_out_dir.setStyleSheet("color: #cdd6f4;")
        riga_out.addWidget(lbl_out_dir)
        
        self.txt_cartella_out = QLabel("Stessa cartella dei file originali")
        self.txt_cartella_out.setFont(QFont("SF Pro Text", 10))
        self.txt_cartella_out.setStyleSheet("color: #6c7086; background: #313244; padding: 6px 10px; border-radius: 6px;")
        self.txt_cartella_out.setWordWrap(True)
        riga_out.addWidget(self.txt_cartella_out, 1)
        
        btn_out = QPushButton("Scegli...")
        btn_out.setFont(QFont("SF Pro Text", 10))
        btn_out.setObjectName("btnTerziario")
        btn_out.setFixedWidth(90)
        btn_out.clicked.connect(self._sfoglia_output)
        riga_out.addWidget(btn_out)
        
        btn_reset = QPushButton("Reset")
        btn_reset.setFont(QFont("SF Pro Text", 10))
        btn_reset.setObjectName("btnTerziario")
        btn_reset.setFixedWidth(70)
        btn_reset.clicked.connect(self._reset_output)
        riga_out.addWidget(btn_reset)
        
        body_layout.addLayout(riga_out)
        
        # -- Separatore --
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #45475a;")
        body_layout.addWidget(sep)
        
        # -- Lista file e anteprima (splitter) --
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #45475a; width: 2px; }")
        
        # Pannello sinistro: lista file
        pannello_sx = QWidget()
        sx_layout = QVBoxLayout(pannello_sx)
        sx_layout.setContentsMargins(0, 0, 5, 0)
        
        # Intestazione con pulsanti selezione
        header_lista = QHBoxLayout()
        lbl_lista = QLabel("File trovati:")
        lbl_lista.setFont(QFont("SF Pro Text", 11, QFont.Bold))
        lbl_lista.setStyleSheet("color: #cdd6f4;")
        header_lista.addWidget(lbl_lista)
        
        header_lista.addStretch()
        
        btn_sel_tutti = QPushButton("Seleziona tutti")
        btn_sel_tutti.setFont(QFont("SF Pro Text", 9))
        btn_sel_tutti.setObjectName("btnTerziario")
        btn_sel_tutti.setFixedWidth(110)
        btn_sel_tutti.clicked.connect(self._seleziona_tutti)
        header_lista.addWidget(btn_sel_tutti)
        
        btn_desel_tutti = QPushButton("Deseleziona tutti")
        btn_desel_tutti.setFont(QFont("SF Pro Text", 9))
        btn_desel_tutti.setObjectName("btnTerziario")
        btn_desel_tutti.setFixedWidth(120)
        btn_desel_tutti.clicked.connect(self._deseleziona_tutti)
        header_lista.addWidget(btn_desel_tutti)
        
        sx_layout.addLayout(header_lista)
        
        self.lista_file = QListWidget()
        self.lista_file.setFont(QFont("SF Pro Text", 10))
        self.lista_file.setStyleSheet("""
            QListWidget {
                background: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background: #45475a;
            }
        """)
        sx_layout.addWidget(self.lista_file, 1)
        
        # Info files
        self.lbl_info = QLabel("Nessun file caricato")
        self.lbl_info.setFont(QFont("SF Pro Text", 9))
        self.lbl_info.setStyleSheet("color: #6c7086;")
        sx_layout.addWidget(self.lbl_info)
        
        splitter.addWidget(pannello_sx)
        
        # Pannello destro: anteprima
        pannello_dx = QWidget()
        dx_layout = QVBoxLayout(pannello_dx)
        dx_layout.setContentsMargins(5, 0, 0, 0)
        
        lbl_anteprima = QLabel("File in elaborazione:")
        lbl_anteprima.setFont(QFont("SF Pro Text", 11, QFont.Bold))
        lbl_anteprima.setStyleSheet("color: #cdd6f4;")
        dx_layout.addWidget(lbl_anteprima)
        
        # Area anteprima
        self.area_anteprima = QScrollArea()
        self.area_anteprima.setWidgetResizable(True)
        self.area_anteprima.setStyleSheet("""
            QScrollArea {
                background: #1e1e2e;
                border: 1px solid #45475a;
                border-radius: 6px;
            }
        """)
        
        self.widget_anteprima = QWidget()
        self.layout_anteprima = QVBoxLayout(self.widget_anteprima)
        self.layout_anteprima.setAlignment(Qt.AlignCenter)
        
        self.label_nome_file = QLabel("Seleziona o avvia una conversione")
        self.label_nome_file.setFont(QFont("SF Pro Text", 10))
        self.label_nome_file.setStyleSheet("color: #6c7086;")
        self.label_nome_file.setAlignment(Qt.AlignCenter)
        self.layout_anteprima.addWidget(self.label_nome_file)
        
        self.label_immagine = QLabel()
        self.label_immagine.setAlignment(Qt.AlignCenter)
        self.label_immagine.setFixedSize(350, 400)
        self.label_immagine.setStyleSheet("background: #181825; border-radius: 8px;")
        self.layout_anteprima.addWidget(self.label_immagine)
        
        self.area_anteprima.setWidget(self.widget_anteprima)
        dx_layout.addWidget(self.area_anteprima, 1)
        
        splitter.addWidget(pannello_dx)
        splitter.setSizes([450, 350])
        
        body_layout.addWidget(splitter, 1)
        
        layout_main.addWidget(body, 1)
        
        # === FOOTER ===
        footer = QFrame()
        footer.setObjectName("footer")
        footer.setFixedHeight(100)
        f_layout = QVBoxLayout(footer)
        f_layout.setContentsMargins(20, 8, 20, 10)
        f_layout.setSpacing(6)
        
        # Barra di progresso
        self.progresso = QProgressBar()
        self.progresso.setObjectName("progresso")
        self.progresso.setRange(0, 100)
        self.progresso.setValue(0)
        self.progresso.setTextVisible(True)
        self.progresso.setFixedHeight(10)
        f_layout.addWidget(self.progresso)
        
        # Riga stato
        riga_stato = QHBoxLayout()
        
        self.label_stato = QLabel("Pronto")
        self.label_stato.setFont(QFont("SF Pro Text", 9))
        self.label_stato.setStyleSheet("color: #6c7086;")
        riga_stato.addWidget(self.label_stato)
        
        riga_stato.addStretch()
        
        self.label_conteggio = QLabel("")
        self.label_conteggio.setFont(QFont("SF Pro Text", 9))
        self.label_conteggio.setStyleSheet("color: #6c7086;")
        riga_stato.addWidget(self.label_conteggio)
        
        f_layout.addLayout(riga_stato)
        
        # Pulsante converti
        self.btn_converti = QPushButton("Avvia Conversione")
        self.btn_converti.setFont(QFont("SF Pro Display", 13, QFont.Bold))
        self.btn_converti.setObjectName("btnPrincipale")
        self.btn_converti.setFixedHeight(42)
        self.btn_converti.setEnabled(False)
        self.btn_converti.clicked.connect(self._avvia)
        f_layout.addWidget(self.btn_converti)
        
        layout_main.addWidget(footer)
    
    def _applica_stile(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: "SF Pro Text", "Segoe UI", "Helvetica Neue", sans-serif;
            }
            QFrame#header {
                background-color: #11111b;
                border-bottom: 1px solid #313244;
            }
            QFrame#footer {
                background-color: #11111b;
                border-top: 1px solid #313244;
            }
            QFrame#body {
                background-color: #1e1e2e;
            }
            QPushButton#btnPrincipale {
                background-color: #a6e3a1;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
            }
            QPushButton#btnPrincipale:hover {
                background-color: #94e2d5;
            }
            QPushButton#btnPrincipale:disabled {
                background-color: #45475a;
                color: #6c7086;
            }
            QPushButton#btnSecondario {
                background-color: #45475a;
                color: #cdd6f4;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
            }
            QPushButton#btnSecondario:hover {
                background-color: #585b70;
            }
            QPushButton#btnTerziario {
                background-color: transparent;
                color: #89b4fa;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton#btnTerziario:hover {
                background-color: #313244;
            }
            QComboBox#combo {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 4px 10px;
                min-width: 80px;
            }
            QComboBox#combo::drop-down {
                border: none;
                padding-right: 8px;
            }
            QComboBox#combo QAbstractItemView {
                background-color: #313244;
                color: #cdd6f4;
                selection-background-color: #45475a;
                border: 1px solid #45475a;
            }
            QProgressBar#progresso {
                background-color: #313244;
                border: none;
                border-radius: 5px;
                text-align: center;
                color: transparent;
            }
            QProgressBar#progresso::chunk {
                background-color: #a6e3a1;
                border-radius: 5px;
            }
            QScrollBar:vertical {
                background: #1e1e2e;
                width: 10px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #45475a;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QSplitter::handle {
                background: #45475a;
            }
        """)
    
    def _sfoglia(self):
        d = QFileDialog.getExistingDirectory(
            self, "Seleziona cartella con file CBR/CBZ",
            self.txt_cartella.text() if "Nessuna" not in self.txt_cartella.text() else os.path.expanduser("~"))
        if d:
            self.txt_cartella.setText(d)
            self._scansiona()
    
    def _sfoglia_output(self):
        d = QFileDialog.getExistingDirectory(
            self, "Seleziona cartella di destinazione",
            self.cartella_output or os.path.expanduser("~"))
        if d:
            self.cartella_output = d
            self.txt_cartella_out.setText(d)
    
    def _reset_output(self):
        self.cartella_output = ""
        self.txt_cartella_out.setText("Stessa cartella dei file originali")
    
    def _scansiona(self):
        path = self.txt_cartella.text()
        if "Nessuna" in path or not os.path.isdir(path):
            QMessageBox.warning(self, "Attenzione", "Seleziona una cartella valida")
            return
        
        self.lista_file.clear()
        self.files_list = []
        self.label_stato.setText("Scansione in corso...")
        
        # Determina pattern in base al formato input
        formati = []
        if self.cmb_input.currentText() in ("CBR", "CBR e CBZ"):
            formati.append("*.cbr")
        if self.cmb_input.currentText() in ("CBZ", "CBR e CBZ"):
            formati.append("*.cbz")
        
        files_trovati = []
        p = Path(path)
        if self.chk_ricorsivo.isChecked():
            pattern = "**/*"
            for f in p.glob(pattern):
                if f.is_file() and f.suffix.lower() in [".cbr", ".cbz"]:
                    if f.suffix.lower() == ".cbr" and "CBR" in self.cmb_input.currentText():
                        files_trovati.append(f)
                    elif f.suffix.lower() == ".cbz" and "CBZ" in self.cmb_input.currentText():
                        files_trovati.append(f)
        else:
            for ext in formati:
                files_trovati.extend(sorted(p.glob(ext)))
        
        files_trovati = sorted(set(files_trovati))
        
        if not files_trovati:
            self.lista_file.addItem("Nessun file trovato")
            self.btn_converti.setEnabled(False)
            self.label_stato.setText("Nessun file trovato")
            self.lbl_info.setText("0 file")
            return
        
        self.files_list = files_trovati
        for f in files_trovati:
            kb = f.stat().st_size // 1024
            if kb > 1024:
                testo = f"{f.name}  ({kb//1024}.{kb%1024//100} MB)"
            else:
                testo = f"{f.name}  ({kb} KB)"
            
            item = QListWidgetItem(testo)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            item.setData(Qt.UserRole, str(f))
            self.lista_file.addItem(item)
        
        totale_kb = sum(f.stat().st_size for f in files_trovati) // 1024
        if totale_kb > 1024:
            info = f"{len(files_trovati)} file - {totale_kb//1024}.{totale_kb%1024//100} MB"
        else:
            info = f"{len(files_trovati)} file - {totale_kb} KB"
        
        self.lbl_info.setText(info)
        self.btn_converti.setEnabled(True)
        self.label_stato.setText(f"Pronto - {info}")
    
    def _avvia(self):
        if not self.files_list or self.in_esecuzione:
            return
        
        # Raccogli solo i file con checkbox selezionata
        files_selezionati = []
        for i in range(self.lista_file.count()):
            item = self.lista_file.item(i)
            if item and item.checkState() == Qt.Checked:
                path = item.data(Qt.UserRole)
                if path:
                    files_selezionati.append(Path(path))
        
        if not files_selezionati:
            QMessageBox.information(self, "Info", "Seleziona almeno un file dalla lista")
            return
        
        self.in_esecuzione = True
        self.btn_converti.setEnabled(False)
        self.btn_converti.setText("Convertendo...")
        self.progresso.setValue(0)
        self.lista_file.clearSelection()
        
        formato = self.cmb_output.currentText()
        elimina = self.chk_elimina.isChecked()
        
        # Prepara convertitore con solo i file selezionati
        conv = Convertitore(self.segnali)
        t = threading.Thread(target=conv.converti,
                             args=(files_selezionati, formato, elimina, self.cartella_output),
                             daemon=True)
        t.start()
    
    def _on_stato(self, testo):
        self.label_stato.setText(testo)
    
    def _seleziona_tutti(self):
        for i in range(self.lista_file.count()):
            item = self.lista_file.item(i)
            if item and item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(Qt.Checked)
    
    def _deseleziona_tutti(self):
        for i in range(self.lista_file.count()):
            item = self.lista_file.item(i)
            if item and item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(Qt.Unchecked)
    
    def _on_file_stato(self, nome, stato):
        # Cerca il file nella lista e aggiorna
        for i in range(self.lista_file.count()):
            item = self.lista_file.item(i)
            if item and nome in item.text() and not item.text().startswith("Nessun"):
                if stato == "Elaborazione...":
                    item.setBackground(QColor("#313244"))
                    self.lista_file.setCurrentRow(i)
                    self.label_nome_file.setText(f"Elaborazione: {nome}")
                elif stato == "OK" or stato.startswith("OK"):
                    testo_base = item.text().split("  (")[0]
                    item.setText(f"{testo_base}  [OK]")
                    item.setCheckState(Qt.Checked)
                    item.setForeground(QColor("#a6e3a1"))
                    item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
                elif stato.startswith("ERRORE"):
                    testo_base = item.text().split("  (")[0]
                    item.setText(f"{testo_base}  [ERRORE]")
                    item.setCheckState(Qt.Unchecked)
                    item.setForeground(QColor("#f38ba8"))
                    item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
                break
    
    def _on_progresso(self, corrente, totale):
        self.progresso.setMaximum(totale)
        self.progresso.setValue(corrente)
        self.label_conteggio.setText(f"{corrente} / {totale}")
    
    def _on_fine(self, ok, errs):
        self.in_esecuzione = False
        self.btn_converti.setEnabled(True)
        self.btn_converti.setText("Avvia Conversione")
        self.lista_file.clearSelection()
        self.label_nome_file.setText("Conversione completata")
        
        if errs == 0 and ok > 0:
            self.label_stato.setText(f"Completato: {ok} convertiti con successo!")
            QMessageBox.information(self, "Completato", f"{ok} file convertiti con successo!")
        elif ok > 0 and errs > 0:
            self.label_stato.setText(f"Completato: {ok} OK, {errs} errori")
            QMessageBox.warning(self, "Attenzione", f"{ok} convertiti, {errs} errori.")
        elif ok == 0 and errs > 0:
            self.label_stato.setText(f"Tutti i {errs} file hanno fallito")
            QMessageBox.critical(self, "Errore", f"Tutti i {errs} file hanno fallito.")
        else:
            self.label_stato.setText("Nessun file convertito")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
    finestra = MainWindow()
    finestra.show()
    sys.exit(app.exec_())
