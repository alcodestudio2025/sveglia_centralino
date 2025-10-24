"""
Sistema di backup e ripristino per il sistema di gestione sveglie
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
import zipfile
import datetime
import json
from database import DatabaseManager
from config import create_directories

class BackupManagerWindow:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        
        # Crea la finestra
        self.window = tk.Toplevel(parent)
        self.window.title("Backup e Ripristino Sistema")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Centra la finestra
        self.window.transient(parent)
        self.window.grab_set()
        
        # Crea cartelle necessarie
        create_directories()
        
        # Crea l'interfaccia
        self.create_widgets()
        self.load_backup_list()
    
    def create_widgets(self):
        """Crea l'interfaccia della finestra"""
        # Frame principale
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titolo
        title_label = ttk.Label(main_frame, text="Backup e Ripristino Sistema", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Notebook per le sezioni
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Tab Backup
        self.create_backup_tab(notebook)
        
        # Tab Ripristino
        self.create_restore_tab(notebook)
        
        # Tab Gestione
        self.create_management_tab(notebook)
        
        # Pulsanti di controllo
        self.create_control_buttons(main_frame)
    
    def create_backup_tab(self, notebook):
        """Crea il tab per il backup"""
        backup_frame = ttk.Frame(notebook)
        notebook.add(backup_frame, text="Crea Backup")
        
        # Frame per le opzioni di backup
        options_frame = ttk.LabelFrame(backup_frame, text="Opzioni Backup", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Opzioni di backup
        self.include_database = tk.BooleanVar(value=True)
        self.include_audio = tk.BooleanVar(value=True)
        self.include_logs = tk.BooleanVar(value=True)
        self.include_settings = tk.BooleanVar(value=True)
        self.include_config = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Database", 
                       variable=self.include_database).grid(row=0, column=0, sticky=tk.W, padx=(0, 20), pady=5)
        ttk.Checkbutton(options_frame, text="Messaggi Audio", 
                       variable=self.include_audio).grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        ttk.Checkbutton(options_frame, text="File di Log", 
                       variable=self.include_logs).grid(row=0, column=2, sticky=tk.W, padx=(0, 20), pady=5)
        
        ttk.Checkbutton(options_frame, text="Impostazioni", 
                       variable=self.include_settings).grid(row=1, column=0, sticky=tk.W, padx=(0, 20), pady=5)
        ttk.Checkbutton(options_frame, text="File di Configurazione", 
                       variable=self.include_config).grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        
        # Frame per il percorso di backup
        path_frame = ttk.LabelFrame(backup_frame, text="Percorso Backup", padding="15")
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.backup_path = tk.StringVar()
        ttk.Label(path_frame, text="Percorso:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(path_frame, textvariable=self.backup_path, width=50).pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        ttk.Button(path_frame, text="Sfoglia", 
                  command=self.browse_backup_path).pack(side=tk.RIGHT)
        
        # Pulsante crea backup
        ttk.Button(backup_frame, text="Crea Backup", 
                  command=self.create_backup).pack(pady=10)
    
    def create_restore_tab(self, notebook):
        """Crea il tab per il ripristino"""
        restore_frame = ttk.Frame(notebook)
        notebook.add(restore_frame, text="Ripristina Backup")
        
        # Frame per selezione file
        file_frame = ttk.LabelFrame(restore_frame, text="Seleziona File Backup", padding="15")
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.restore_path = tk.StringVar()
        ttk.Label(file_frame, text="File Backup:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(file_frame, textvariable=self.restore_path, width=50).pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Sfoglia", 
                  command=self.browse_restore_file).pack(side=tk.RIGHT)
        
        # Frame per opzioni di ripristino
        options_frame = ttk.LabelFrame(restore_frame, text="Opzioni Ripristino", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.restore_database = tk.BooleanVar(value=True)
        self.restore_audio = tk.BooleanVar(value=True)
        self.restore_logs = tk.BooleanVar(value=False)
        self.restore_settings = tk.BooleanVar(value=True)
        self.restore_config = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Database", 
                       variable=self.restore_database).grid(row=0, column=0, sticky=tk.W, padx=(0, 20), pady=5)
        ttk.Checkbutton(options_frame, text="Messaggi Audio", 
                       variable=self.restore_audio).grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        ttk.Checkbutton(options_frame, text="File di Log", 
                       variable=self.restore_logs).grid(row=0, column=2, sticky=tk.W, padx=(0, 20), pady=5)
        
        ttk.Checkbutton(options_frame, text="Impostazioni", 
                       variable=self.restore_settings).grid(row=1, column=0, sticky=tk.W, padx=(0, 20), pady=5)
        ttk.Checkbutton(options_frame, text="File di Configurazione", 
                       variable=self.restore_config).grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        
        # Pulsante ripristina
        ttk.Button(restore_frame, text="Ripristina Backup", 
                  command=self.restore_backup).pack(pady=10)
    
    def create_management_tab(self, notebook):
        """Crea il tab per la gestione dei backup"""
        management_frame = ttk.Frame(notebook)
        notebook.add(management_frame, text="Gestione Backup")
        
        # Frame per lista backup
        list_frame = ttk.LabelFrame(management_frame, text="Backup Disponibili", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview per i backup
        columns = ("Nome", "Data", "Dimensione", "Tipo", "Percorso")
        self.backup_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.backup_tree.heading(col, text=col)
            self.backup_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.backup_tree.yview)
        self.backup_tree.configure(yscrollcommand=scrollbar.set)
        
        self.backup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Pulsanti di gestione
        buttons_frame = ttk.Frame(management_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Aggiorna Lista", 
                  command=self.load_backup_list).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Elimina Selezionato", 
                  command=self.delete_selected_backup).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Ripristina Selezionato", 
                  command=self.restore_selected_backup).pack(side=tk.LEFT, padx=(0, 10))
    
    def create_control_buttons(self, parent):
        """Crea i pulsanti di controllo"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X)
        
        # Pulsanti di chiusura
        ttk.Button(buttons_frame, text="Chiudi", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
    
    def browse_backup_path(self):
        """Sfoglia per il percorso di backup"""
        path = filedialog.askdirectory(title="Seleziona Cartella per Backup")
        if path:
            self.backup_path.set(path)
    
    def browse_restore_file(self):
        """Sfoglia per il file di backup"""
        file_path = filedialog.askopenfilename(
            title="Seleziona File Backup",
            filetypes=[("File ZIP", "*.zip"), ("Tutti i file", "*.*")]
        )
        if file_path:
            self.restore_path.set(file_path)
    
    def create_backup(self):
        """Crea un backup del sistema"""
        backup_dir = self.backup_path.get()
        if not backup_dir:
            messagebox.showerror("Errore", "Seleziona un percorso per il backup")
            return
        
        try:
            # Crea il nome del file backup
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"sveglia_centralino_backup_{timestamp}.zip"
            backup_file = os.path.join(backup_dir, backup_filename)
            
            # Crea il file ZIP
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Database
                if self.include_database.get():
                    if os.path.exists(self.db.db_path):
                        zipf.write(self.db.db_path, "database/sveglie.db")
                
                # Messaggi audio
                if self.include_audio.get():
                    audio_dir = "audio_messages"
                    if os.path.exists(audio_dir):
                        for root, dirs, files in os.walk(audio_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arc_path = os.path.relpath(file_path, ".")
                                zipf.write(file_path, arc_path)
                
                # Log
                if self.include_logs.get():
                    logs_dir = "logs"
                    if os.path.exists(logs_dir):
                        for root, dirs, files in os.walk(logs_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arc_path = os.path.relpath(file_path, ".")
                                zipf.write(file_path, arc_path)
                
                # Impostazioni
                if self.include_settings.get():
                    settings_file = "settings.json"
                    if os.path.exists(settings_file):
                        zipf.write(settings_file, "settings.json")
                
                # Configurazione
                if self.include_config.get():
                    config_files = ["config.py", "requirements.txt"]
                    for config_file in config_files:
                        if os.path.exists(config_file):
                            zipf.write(config_file, config_file)
                
                # Metadati del backup
                metadata = {
                    "timestamp": timestamp,
                    "version": "1.0",
                    "components": {
                        "database": self.include_database.get(),
                        "audio": self.include_audio.get(),
                        "logs": self.include_logs.get(),
                        "settings": self.include_settings.get(),
                        "config": self.include_config.get()
                    }
                }
                
                zipf.writestr("backup_metadata.json", json.dumps(metadata, indent=2))
            
            messagebox.showinfo("Successo", f"Backup creato con successo:\n{backup_file}")
            self.load_backup_list()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella creazione del backup: {e}")
    
    def restore_backup(self):
        """Ripristina un backup"""
        backup_file = self.restore_path.get()
        if not backup_file or not os.path.exists(backup_file):
            messagebox.showerror("Errore", "Seleziona un file di backup valido")
            return
        
        if messagebox.askyesno("Conferma Ripristino", 
                              "Sei sicuro di voler ripristinare questo backup?\n\n"
                              "Questa operazione sovrascriverà i dati esistenti."):
            try:
                # Crea backup di sicurezza prima del ripristino
                self.create_safety_backup()
                
                # Estrae il backup
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    # Legge i metadati
                    metadata = {}
                    if "backup_metadata.json" in zipf.namelist():
                        metadata = json.loads(zipf.read("backup_metadata.json").decode('utf-8'))
                    
                    # Ripristina i componenti selezionati
                    if self.restore_database.get() and "database/sveglie.db" in zipf.namelist():
                        zipf.extract("database/sveglie.db", ".")
                        # Sposta il file nella posizione corretta
                        if os.path.exists("database/sveglie.db"):
                            shutil.move("database/sveglie.db", self.db.db_path)
                    
                    if self.restore_audio.get():
                        for member in zipf.namelist():
                            if member.startswith("audio_messages/"):
                                zipf.extract(member, ".")
                    
                    if self.restore_logs.get():
                        for member in zipf.namelist():
                            if member.startswith("logs/"):
                                zipf.extract(member, ".")
                    
                    if self.restore_settings.get() and "settings.json" in zipf.namelist():
                        zipf.extract("settings.json", ".")
                    
                    if self.restore_config.get():
                        for config_file in ["config.py", "requirements.txt"]:
                            if config_file in zipf.namelist():
                                zipf.extract(config_file, ".")
                
                messagebox.showinfo("Successo", "Backup ripristinato con successo")
                self.load_backup_list()
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel ripristino del backup: {e}")
    
    def create_safety_backup(self):
        """Crea un backup di sicurezza prima del ripristino"""
        try:
            safety_dir = "backup"
            if not os.path.exists(safety_dir):
                os.makedirs(safety_dir)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safety_file = os.path.join(safety_dir, f"safety_backup_{timestamp}.zip")
            
            with zipfile.ZipFile(safety_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.exists(self.db.db_path):
                    zipf.write(self.db.db_path, "sveglie.db")
            
            print(f"Backup di sicurezza creato: {safety_file}")
            
        except Exception as e:
            print(f"Errore nella creazione backup di sicurezza: {e}")
    
    def load_backup_list(self):
        """Carica la lista dei backup disponibili"""
        # Pulisce la lista
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)
        
        try:
            # Cerca file di backup nella cartella corrente e sottocartelle
            backup_files = []
            for root, dirs, files in os.walk("."):
                for file in files:
                    if file.startswith("sveglia_centralino_backup_") and file.endswith(".zip"):
                        file_path = os.path.join(root, file)
                        stat = os.stat(file_path)
                        
                        # Legge i metadati se disponibili
                        metadata = {}
                        try:
                            with zipfile.ZipFile(file_path, 'r') as zipf:
                                if "backup_metadata.json" in zipf.namelist():
                                    metadata = json.loads(zipf.read("backup_metadata.json").decode('utf-8'))
                        except:
                            pass
                        
                        backup_files.append({
                            'name': file,
                            'path': file_path,
                            'size': stat.st_size,
                            'modified': datetime.datetime.fromtimestamp(stat.st_mtime),
                            'metadata': metadata
                        })
            
            # Ordina per data di modifica (più recenti prima)
            backup_files.sort(key=lambda x: x['modified'], reverse=True)
            
            # Aggiunge alla lista
            for backup in backup_files:
                size_mb = backup['size'] / (1024 * 1024)
                backup_type = "Completo" if backup['metadata'].get('components', {}).get('database') else "Parziale"
                
                self.backup_tree.insert("", "end", values=(
                    backup['name'],
                    backup['modified'].strftime("%Y-%m-%d %H:%M"),
                    f"{size_mb:.1f} MB",
                    backup_type,
                    backup['path']
                ))
        
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel caricamento lista backup: {e}")
    
    def delete_selected_backup(self):
        """Elimina il backup selezionato"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un backup da eliminare")
            return
        
        item = self.backup_tree.item(selection[0])
        backup_name = item['values'][0]
        backup_path = item['values'][4]
        
        if messagebox.askyesno("Conferma Eliminazione", 
                              f"Sei sicuro di voler eliminare il backup '{backup_name}'?"):
            try:
                os.remove(backup_path)
                messagebox.showinfo("Successo", f"Backup '{backup_name}' eliminato")
                self.load_backup_list()
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nell'eliminazione: {e}")
    
    def restore_selected_backup(self):
        """Ripristina il backup selezionato"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un backup da ripristinare")
            return
        
        item = self.backup_tree.item(selection[0])
        backup_path = item['values'][4]
        
        self.restore_path.set(backup_path)
        self.restore_backup()

if __name__ == "__main__":
    # Test del backup manager
    root = tk.Tk()
    root.withdraw()
    db = DatabaseManager()
    BackupManagerWindow(root, db)
    root.mainloop()
