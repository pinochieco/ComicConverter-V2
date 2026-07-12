    def converti(self, files, formato_output, elimina, cartella_output=""):
        totale = len(files)
        ok = 0
        errs = 0
        
        for i, f in enumerate(files):
            # Determina il nome del file di output in base al formato scelto
            if cartella_output:
                if formato_output == "CBZ":
                    nome_output_path = Path(cartella_output) / (f.stem + ".cbz")
                else:  # PDF
                    nome_output_path = Path(cartella_output) / (f.stem + ".pdf")
            else:
                if formato_output == "CBZ":
                    nome_output_path = f.with_suffix(".cbz")
                else:  # PDF
                    nome_output_path = f.with_suffix(".pdf")
            
            nome_output = nome_output_path.name
            
            self.segnali.aggiorna_file.emit(f.name, nome_output, "Elaborazione...")
            self.segnali.aggiorna_stato.emit(f"Convertendo: {f.name}")
            
            try:
                if f.suffix.lower() == ".cbr":
                    if formato_output == "CBZ":
                        risultato = self._cbr_in_cbz(f, cartella_output)
                    else:  # PDF
                        risultato = self._cbr_in_pdf(f, cartella_output)
                elif f.suffix.lower() == ".cbz":
                    if formato_output == "PDF":
                        risultato = self._cbz_in_pdf(f, cartella_output)
                    else:
                        risultato = self._cbz_in_pdf(f, cartella_output)
                elif f.suffix.lower() == ".pdf":
                    if formato_output == "CBZ":
                        risultato = self._pdf_in_cbz(f, cartella_output)
                    elif formato_output == "CBR":
                        risultato = (False, "CBR non supportato, usa CBZ")
                    else:
                        risultato = (False, "Formato non supportato")
                else:
                    risultato = (False, "Formato non supportato")
                
                if risultato[0]:
                    ok += 1
                    if elimina:
                        try:
                            os.remove(str(f))
                            self.segnali.aggiorna_file.emit(f.name, nome_output, "OK (eliminato)")
                        except:
                            self.segnali.aggiorna_file.emit(f.name, nome_output, "OK")
                    else:
                        self.segnali.aggiorna_file.emit(f.name, nome_output, "OK")
                else:
                    errs += 1
                    self.segnali.aggiorna_file.emit(f.name, nome_output, f"ERRORE: {risultato[1][:40]}")
            except Exception as e:
                errs += 1
                self.segnali.aggiorna_file.emit(f.name, nome_output, f"ERRORE")
            
            self.segnali.aggiorna_progresso.emit(i + 1, totale)
        
        self.segnali.fine_conversione.emit(ok, errs)

    def _on_file_stato(self, nome, nome_output, stato):
        # Aggiorna il label del file in elaborazione
        if stato == "Elaborazione...":
            self.label_file_corrente.setText(f"▶ {nome}")
        elif stato.startswith("OK"):
            # Verifica se questo nome_output è già presente nella lista elaborati
            gia_presente = False
            for i in range(self.lista_elaborati.count()):
                if nome_output in self.lista_elaborati.item(i).text():
                    gia_presente = True
                    # Se è già presente, aggiorna il testo se necessario
                    if stato == "OK (eliminato)" and "(originale eliminato)" not in self.lista_elaborati.item(i).text():
                        self.lista_elaborati.item(i).setText(f"✅ {nome_output} (originale eliminato)")
                    break

            if not gia_presente:
                if stato == "OK (eliminato)":
                    self.lista_elaborati.addItem(f"✅ {nome_output} (originale eliminato)")
                else:
                    self.lista_elaborati.addItem(f"✅ {nome_output}")
            self.lista_elaborati.scrollToBottom()

            self.label_file_corrente.setText("")
        elif stato.startswith("ERRORE"):
            self.lista_elaborati.addItem(f"❌ {nome}")
            self.lista_elaborati.scrollToBottom()
            self.label_file_corrente.setText("")

        # Cerca il file nella lista e aggiorna
        for i in range(self.lista_file.count()):
            item = self.lista_file.item(i)
            if item and nome in item.text() and not item.text().startswith("Nessun"):
        if stato == "Elaborazione...":
                    item.setBackground(QColor("#313244"))
                    self.lista_file.setCurrentRow(i)
                elif stato.startswith("OK"):
                    if "[OK]" not in item.text():
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

