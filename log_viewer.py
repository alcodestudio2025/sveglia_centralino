"""
Visualizzatore di log per il sistema di gestione sveglie
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import datetime
from logger import system_logger

class LogViewerWindow:
    def __init__(self, parent):
        self.parent = parent
        
        # Crea la finestra
        self.window = tk.Toplevel(parent)
        self.window.title("Visualizzatore Log Sistema")
        self.window.geometry("1200x800")
        self.window.resizable(True, True)
        
        # Centra la finestra
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variabili per i controlli
        self.selected_log_file = tk.StringVar()
        self.filter_level = tk.StringVar(value="ALL")
        self.filter_text = tk.StringVar()
        self.auto_refresh = tk.BooleanVar(value=False)
        self.refresh_interval = tk.IntVar(value=5)  # secondi
        
        # Timer per auto-refresh
        self.refresh_timer = None
        
        # Crea l'interfaccia
        self.create_widgets()
        self.load_log_files()
        
        # Avvia auto-refresh se abilitato
        self.toggle_auto_refresh()
    
    def create_widgets(self):
        """Crea l'interfaccia della finestra"""
        # Frame principale
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titolo
        title_label = ttk.Label(main_frame, text="Visualizzatore Log Sistema", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Frame per controlli
        self.create_control_section(main_frame)
        
        # Frame per visualizzazione log
        self.create_log_display_section(main_frame)
        
        # Frame per statistiche
        self.create_stats_section(main_frame)
    
    def create_control_section(self, parent):
        """Crea la sezione dei controlli"""
        control_frame = ttk.LabelFrame(parent, text="Controlli", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Prima riga: Selezione file e filtri
        row1_frame = ttk.Frame(control_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Selezione file log
        ttk.Label(row1_frame, text="File Log:").pack(side=tk.LEFT, padx=(0, 10))
        self.log_file_combo = ttk.Combobox(row1_frame, textvariable=self.selected_log_file, 
                                          state="readonly", width=30)
        self.log_file_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.log_file_combo.bind("<<ComboboxSelected>>", self.on_log_file_selected)
        
        # Filtro livello
        ttk.Label(row1_frame, text="Livello:").pack(side=tk.LEFT, padx=(0, 10))
        level_combo = ttk.Combobox(row1_frame, textvariable=self.filter_level,
                                  values=["ALL", "DEBUG", "INFO", "WARNING", "ERROR"], 
                                  state="readonly", width=10)
        level_combo.pack(side=tk.LEFT, padx=(0, 20))
        level_combo.bind("<<ComboboxSelected>>", self.apply_filters)
        
        # Filtro testo
        ttk.Label(row1_frame, text="Cerca:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(row1_frame, textvariable=self.filter_text, width=20).pack(side=tk.LEFT, padx=(0, 20))
        self.filter_text.trace('w', self.apply_filters)
        
        # Seconda riga: Pulsanti e opzioni
        row2_frame = ttk.Frame(control_frame)
        row2_frame.pack(fill=tk.X)
        
        # Pulsanti operazioni
        ttk.Button(row2_frame, text="Aggiorna", 
                  command=self.refresh_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(row2_frame, text="Pulisci", 
                  command=self.clear_log_display).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(row2_frame, text="Esporta", 
                  command=self.export_logs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(row2_frame, text="Elimina File", 
                  command=self.delete_log_file).pack(side=tk.LEFT, padx=(0, 10))
        
        # Auto-refresh
        ttk.Checkbutton(row2_frame, text="Auto-refresh", 
                       variable=self.auto_refresh, 
                       command=self.toggle_auto_refresh).pack(side=tk.LEFT, padx=(20, 10))
        
        ttk.Label(row2_frame, text="Intervallo (sec):").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Spinbox(row2_frame, from_=1, to=60, textvariable=self.refresh_interval, 
                   width=5).pack(side=tk.LEFT, padx=(0, 20))
        
        # Pulsanti di chiusura
        ttk.Button(row2_frame, text="Chiudi", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
    
    def create_log_display_section(self, parent):
        """Crea la sezione di visualizzazione log"""
        display_frame = ttk.LabelFrame(parent, text="Log Entries", padding="5")
        display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # Text widget con scrollbar
        self.log_text = scrolledtext.ScrolledText(
            display_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurazione colori per i livelli
        self.setup_text_colors()
    
    def create_stats_section(self, parent):
        """Crea la sezione delle statistiche"""
        stats_frame = ttk.LabelFrame(parent, text="Statistiche", padding="10")
        stats_frame.pack(fill=tk.X)
        stats_frame.columnconfigure(1, weight=1)
        
        # Statistiche
        self.stats_labels = {}
        stats_info = [
            ("Totale righe:", "total_lines"),
            ("Errori:", "errors"),
            ("Warning:", "warnings"),
            ("Info:", "info"),
            ("Ultimo aggiornamento:", "last_update")
        ]
        
        for i, (label, key) in enumerate(stats_info):
            ttk.Label(stats_frame, text=label).grid(row=0, column=i*2, sticky=tk.W, padx=(0, 5))
            self.stats_labels[key] = ttk.Label(stats_frame, text="0", font=("Arial", 9, "bold"))
            self.stats_labels[key].grid(row=0, column=i*2+1, sticky=tk.W, padx=(0, 20))
    
    def setup_text_colors(self):
        """Configura i colori per i diversi livelli di log"""
        self.log_text.tag_configure("ERROR", foreground="#ff6b6b")
        self.log_text.tag_configure("WARNING", foreground="#ffd93d")
        self.log_text.tag_configure("INFO", foreground="#6bcf7f")
        self.log_text.tag_configure("DEBUG", foreground="#4dabf7")
        self.log_text.tag_configure("ALARM_EVENT", foreground="#ff8cc8")
        self.log_text.tag_configure("PBX_EVENT", foreground="#ffa8a8")
        self.log_text.tag_configure("SYSTEM_EVENT", foreground="#a8e6cf")
    
    def load_log_files(self):
        """Carica la lista dei file di log"""
        log_files = system_logger.get_log_files()
        file_names = [f['name'] for f in log_files]
        
        self.log_file_combo['values'] = file_names
        if file_names:
            self.log_file_combo.set(file_names[0])
            self.refresh_log()
    
    def on_log_file_selected(self, event=None):
        """Gestisce la selezione di un file log"""
        self.refresh_log()
    
    def refresh_log(self):
        """Aggiorna la visualizzazione del log"""
        selected_file = self.selected_log_file.get()
        if not selected_file:
            return
        
        try:
            # Trova il percorso del file
            log_files = system_logger.get_log_files()
            file_path = None
            for log_file in log_files:
                if log_file['name'] == selected_file:
                    file_path = log_file['path']
                    break
            
            if not file_path or not os.path.exists(file_path):
                return
            
            # Legge il file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Applica i filtri
            filtered_lines = self.apply_filters_to_lines(lines)
            
            # Aggiorna la visualizzazione
            self.update_log_display(filtered_lines)
            
            # Aggiorna le statistiche
            self.update_stats(lines, filtered_lines)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel caricamento del log: {e}")
    
    def apply_filters_to_lines(self, lines):
        """Applica i filtri alle righe del log"""
        filtered_lines = []
        
        for line in lines:
            # Filtro per livello
            if self.filter_level.get() != "ALL":
                if self.filter_level.get() not in line:
                    continue
            
            # Filtro per testo
            if self.filter_text.get():
                if self.filter_text.get().lower() not in line.lower():
                    continue
            
            filtered_lines.append(line)
        
        return filtered_lines
    
    def apply_filters(self, *args):
        """Applica i filtri al log corrente"""
        self.refresh_log()
    
    def update_log_display(self, lines):
        """Aggiorna la visualizzazione del log"""
        # Pulisce il text widget
        self.log_text.delete(1.0, tk.END)
        
        # Aggiunge le righe con colori appropriati
        for line in lines:
            # Determina il tag per il colore
            tag = None
            if "ERROR" in line:
                tag = "ERROR"
            elif "WARNING" in line:
                tag = "WARNING"
            elif "INFO" in line:
                tag = "INFO"
            elif "DEBUG" in line:
                tag = "DEBUG"
            elif "ALARM_EVENT" in line:
                tag = "ALARM_EVENT"
            elif "PBX_EVENT" in line:
                tag = "PBX_EVENT"
            elif "SYSTEM_EVENT" in line:
                tag = "SYSTEM_EVENT"
            
            # Inserisce la riga
            self.log_text.insert(tk.END, line)
            if tag:
                # Applica il colore all'ultima riga inserita
                start_line = self.log_text.index(tk.END + "-1l")
                end_line = self.log_text.index(tk.END)
                self.log_text.tag_add(tag, start_line, end_line)
        
        # Scrolla alla fine
        self.log_text.see(tk.END)
    
    def update_stats(self, all_lines, filtered_lines):
        """Aggiorna le statistiche"""
        # Conta i livelli
        errors = sum(1 for line in all_lines if "ERROR" in line)
        warnings = sum(1 for line in all_lines if "WARNING" in line)
        info = sum(1 for line in all_lines if "INFO" in line)
        
        # Aggiorna le etichette
        self.stats_labels["total_lines"].config(text=str(len(filtered_lines)))
        self.stats_labels["errors"].config(text=str(errors))
        self.stats_labels["warnings"].config(text=str(warnings))
        self.stats_labels["info"].config(text=str(info))
        self.stats_labels["last_update"].config(text=datetime.datetime.now().strftime("%H:%M:%S"))
    
    def clear_log_display(self):
        """Pulisce la visualizzazione del log"""
        self.log_text.delete(1.0, tk.END)
        for key in self.stats_labels:
            self.stats_labels[key].config(text="0")
    
    def export_logs(self):
        """Esporta i log in un file"""
        file_path = filedialog.asksaveasfilename(
            title="Esporta Log",
            defaultextension=".txt",
            filetypes=[("File di testo", "*.txt"), ("Tutti i file", "*.*")]
        )
        
        if file_path:
            try:
                # Esporta i log filtrati
                selected_file = self.selected_log_file.get()
                if selected_file:
                    log_files = system_logger.get_log_files()
                    source_path = None
                    for log_file in log_files:
                        if log_file['name'] == selected_file:
                            source_path = log_file['path']
                            break
                    
                    if source_path and os.path.exists(source_path):
                        with open(source_path, 'r', encoding='utf-8') as src:
                            lines = src.readlines()
                        
                        filtered_lines = self.apply_filters_to_lines(lines)
                        
                        with open(file_path, 'w', encoding='utf-8') as dst:
                            dst.writelines(filtered_lines)
                        
                        messagebox.showinfo("Successo", f"Log esportati in: {file_path}")
                    else:
                        messagebox.showerror("Errore", "File di log non trovato")
                else:
                    messagebox.showwarning("Attenzione", "Seleziona un file di log")
                    
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nell'esportazione: {e}")
    
    def delete_log_file(self):
        """Elimina il file di log selezionato"""
        selected_file = self.selected_log_file.get()
        if not selected_file:
            messagebox.showwarning("Attenzione", "Seleziona un file di log da eliminare")
            return
        
        if messagebox.askyesno("Conferma Eliminazione", 
                              f"Sei sicuro di voler eliminare il file '{selected_file}'?"):
            try:
                log_files = system_logger.get_log_files()
                file_path = None
                for log_file in log_files:
                    if log_file['name'] == selected_file:
                        file_path = log_file['path']
                        break
                
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    messagebox.showinfo("Successo", f"File '{selected_file}' eliminato")
                    self.load_log_files()
                else:
                    messagebox.showerror("Errore", "File non trovato")
                    
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nell'eliminazione: {e}")
    
    def toggle_auto_refresh(self):
        """Attiva/disattiva l'auto-refresh"""
        if self.auto_refresh.get():
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        """Avvia l'auto-refresh"""
        self.stop_auto_refresh()  # Ferma eventuali timer esistenti
        self.schedule_refresh()
    
    def stop_auto_refresh(self):
        """Ferma l'auto-refresh"""
        if self.refresh_timer:
            self.window.after_cancel(self.refresh_timer)
            self.refresh_timer = None
    
    def schedule_refresh(self):
        """Programma il prossimo refresh"""
        if self.auto_refresh.get():
            self.refresh_log()
            interval_ms = self.refresh_interval.get() * 1000
            self.refresh_timer = self.window.after(interval_ms, self.schedule_refresh)
    
    def __del__(self):
        """Cleanup quando la finestra viene chiusa"""
        self.stop_auto_refresh()

if __name__ == "__main__":
    # Test del visualizzatore
    root = tk.Tk()
    root.withdraw()
    LogViewerWindow(root)
    root.mainloop()
