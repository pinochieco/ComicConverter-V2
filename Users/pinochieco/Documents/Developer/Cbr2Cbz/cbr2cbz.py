    def _avvia(self):
        if not self.files_list or self.in_esecuzione:
            return
        
        # Raccogli solo i file selezionati tramite checkbox
        files_selezionati = []
        for i in range(self.lista_file.count()):
            item = self.lista_file.item(i)
            if item and item.checkState() == Qt.Checked:
                path = item.data(Qt.UserRole)
                if path:
                    files_selezionati.append(Path(path))

        if not files_selezionati:
            QMessageBox.information(self, "Info", "Seleziona almeno un file dalla lista (spunta la checkbox)")
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
                    # Mantieni il nome originale senza lo stato
                    testo_base = item.text().split("  [")[0] if "  [" in item.text() else item.text().split("  (")[0]
                    item.setText(f"{testo_base}  [OK]")
                    item.setForeground(QColor("#a6e3a1"))
                elif stato.startswith("ERRORE"):
                    testo_base = item.text().split("  [")[0] if "  [" in item.text() else item.text().split("  (")[0]
                    item.setText(f"{testo_base}  [ERRORE]")
                    item.setForeground(QColor("#f38ba8"))
                break

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

