"""
Pagina delle impostazioni del sistema di gestione sveglie
"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
import json
import os
from config import PBX_CONFIG, AUDIO_CONFIG, ALARM_CONFIG, HOTEL_CONFIG

class SettingsWindow:
    def __init__(self, parent, on_save_callback=None):
        self.parent = parent
        self.on_save_callback = on_save_callback
        self.settings_file = "settings.json"
        
        # Carica impostazioni esistenti
        self.settings = self.load_settings()
        
        # Crea la finestra
        self.window = tk.Toplevel(parent)
        self.window.title("Impostazioni Sistema")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Variabili per i controlli
        self.setup_variables()
        
        # Crea l'interfaccia
        self.create_widgets()
        
        # Popola i campi con i valori esistenti
        self.load_current_settings()
    
    def setup_variables(self):
        """Inizializza le variabili per i controlli"""
        # SSH/PBX Settings
        self.pbx_host = tk.StringVar()
        self.pbx_port = tk.StringVar()
        self.pbx_username = tk.StringVar()
        self.pbx_password = tk.StringVar()
        self.pbx_timeout = tk.StringVar()
        
        # Mail Settings
        self.mail_enabled = tk.BooleanVar()
        self.mail_smtp_server = tk.StringVar()
        self.mail_smtp_port = tk.StringVar()
        self.mail_username = tk.StringVar()
        self.mail_password = tk.StringVar()
        self.mail_recipients = tk.StringVar()
        self.mail_ssl = tk.BooleanVar()
        
        # Log Settings
        self.log_level = tk.StringVar()
        self.log_retention_days = tk.StringVar()
        self.log_auto_cleanup = tk.BooleanVar()
        
        # Room Settings
        self.hotel_name = tk.StringVar()
        self.total_rooms = tk.StringVar()
        self.room_prefix = tk.StringVar()
        self.room_start_number = tk.StringVar()
        
        # Audio Settings
        self.audio_volume = tk.StringVar()
        self.audio_formats = tk.StringVar()
        
        # Alarm Settings
        self.snooze_options = tk.StringVar()
        self.max_snooze_attempts = tk.StringVar()
        self.call_timeout = tk.StringVar()
    
    def create_widgets(self):
        """Crea l'interfaccia delle impostazioni"""
        # Frame principale con scrollbar
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook per le sezioni
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Connessione PBX
        self.create_pbx_tab(notebook)
        
        # Tab 2: Configurazione Camere
        self.create_rooms_tab(notebook)
        
        # Tab 3: Messaggi Audio
        self.create_audio_tab(notebook)
        
        # Tab 4: Mail e Report
        self.create_mail_tab(notebook)
        
        # Tab 5: Log e Monitoraggio
        self.create_logs_tab(notebook)
        
        # Tab 6: Sveglie
        self.create_alarms_tab(notebook)
        
        # Pulsanti di controllo
        self.create_control_buttons(main_frame)
    
    def create_pbx_tab(self, notebook):
        """Crea il tab per la configurazione PBX"""
        pbx_frame = ttk.Frame(notebook)
        notebook.add(pbx_frame, text="Connessione PBX")
        
        # Titolo
        ttk.Label(pbx_frame, text="Configurazione Centralino PBX", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Frame per i campi
        fields_frame = ttk.Frame(pbx_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True)
        
        # Host
        ttk.Label(fields_frame, text="Indirizzo IP Centralino:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.pbx_host, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Porta
        ttk.Label(fields_frame, text="Porta SSH:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.pbx_port, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Username
        ttk.Label(fields_frame, text="Username SSH:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.pbx_username, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(fields_frame, text="Password SSH:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.pbx_password, show="*", width=30).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Timeout
        ttk.Label(fields_frame, text="Timeout (secondi):").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.pbx_timeout, width=10).grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Pulsante test connessione
        ttk.Button(fields_frame, text="Test Connessione", 
                  command=self.test_pbx_connection).grid(row=5, column=0, columnspan=2, pady=20)
        
        fields_frame.columnconfigure(1, weight=1)
    
    def create_rooms_tab(self, notebook):
        """Crea il tab per la configurazione camere"""
        rooms_frame = ttk.Frame(notebook)
        notebook.add(rooms_frame, text="Configurazione Camere")
        
        # Titolo
        ttk.Label(rooms_frame, text="Configurazione Camere Hotel", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Frame principale
        main_frame = ttk.Frame(rooms_frame)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame sinistro - Configurazione generale
        left_frame = ttk.LabelFrame(main_frame, text="Configurazione Generale", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Nome hotel
        ttk.Label(left_frame, text="Nome Hotel:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(left_frame, textvariable=self.hotel_name, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Numero totale camere
        ttk.Label(left_frame, text="Numero Totale Camere:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(left_frame, textvariable=self.total_rooms, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Prefisso camere
        ttk.Label(left_frame, text="Prefisso Camere:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(left_frame, textvariable=self.room_prefix, width=10).grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Numero di partenza
        ttk.Label(left_frame, text="Numero di Partenza:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(left_frame, textvariable=self.room_start_number, width=10).grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        left_frame.columnconfigure(1, weight=1)
        
        # Frame destro - Gestione camere individuali
        right_frame = ttk.LabelFrame(main_frame, text="Gestione Camere Individuali", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Lista camere con colori e etichette
        ttk.Label(right_frame, text="Lista Camere (colore = status):").pack(anchor=tk.W, pady=(0, 10))
        
        # Treeview per le camere
        columns = ("Numero", "Status", "Etichetta", "Colore")
        self.rooms_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.rooms_tree.heading(col, text=col)
            self.rooms_tree.column(col, width=100)
        
        # Scrollbar
        rooms_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.rooms_tree.yview)
        self.rooms_tree.configure(yscrollcommand=rooms_scrollbar.set)
        
        self.rooms_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rooms_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Pulsanti per gestione camere
        rooms_buttons = ttk.Frame(right_frame)
        rooms_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(rooms_buttons, text="Aggiungi Camera", 
                  command=self.add_room).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rooms_buttons, text="Modifica Camera", 
                  command=self.edit_room).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rooms_buttons, text="Elimina Camera", 
                  command=self.delete_room).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rooms_buttons, text="Rigenera Camere", 
                  command=self.regenerate_rooms).pack(side=tk.LEFT)
    
    def create_audio_tab(self, notebook):
        """Crea il tab per la configurazione audio"""
        audio_frame = ttk.Frame(notebook)
        notebook.add(audio_frame, text="Messaggi Audio")
        
        # Titolo
        ttk.Label(audio_frame, text="Configurazione Messaggi Audio", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Frame per i campi
        fields_frame = ttk.Frame(audio_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True)
        
        # Volume predefinito
        ttk.Label(fields_frame, text="Volume Predefinito (0.0-1.0):").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.audio_volume, width=10).grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Formati supportati
        ttk.Label(fields_frame, text="Formati Supportati:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.audio_formats, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Cartella messaggi
        ttk.Label(fields_frame, text="Cartella Messaggi:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=tk.StringVar(value="audio_messages"), width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        fields_frame.columnconfigure(1, weight=1)
    
    def create_mail_tab(self, notebook):
        """Crea il tab per la configurazione mail"""
        mail_frame = ttk.Frame(notebook)
        notebook.add(mail_frame, text="Mail e Report")
        
        # Titolo
        ttk.Label(mail_frame, text="Configurazione Invio Report via Mail", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Checkbox per abilitare mail
        ttk.Checkbutton(mail_frame, text="Abilita invio report via mail", 
                       variable=self.mail_enabled).pack(anchor=tk.W, pady=(0, 20))
        
        # Frame per i campi mail
        fields_frame = ttk.Frame(mail_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True)
        
        # Server SMTP
        ttk.Label(fields_frame, text="Server SMTP:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.mail_smtp_server, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Porta SMTP
        ttk.Label(fields_frame, text="Porta SMTP:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.mail_smtp_port, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Username
        ttk.Label(fields_frame, text="Username:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.mail_username, width=40).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(fields_frame, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.mail_password, show="*", width=40).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Destinatari
        ttk.Label(fields_frame, text="Destinatari (separati da ;):").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.mail_recipients, width=40).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # SSL
        ttk.Checkbutton(fields_frame, text="Usa SSL/TLS", 
                       variable=self.mail_ssl).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Pulsante test mail
        ttk.Button(fields_frame, text="Test Invio Mail", 
                  command=self.test_mail).grid(row=6, column=0, columnspan=2, pady=20)
        
        fields_frame.columnconfigure(1, weight=1)
    
    def create_logs_tab(self, notebook):
        """Crea il tab per la configurazione log"""
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="Log e Monitoraggio")
        
        # Titolo
        ttk.Label(logs_frame, text="Configurazione Log e Monitoraggio", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Frame per i campi
        fields_frame = ttk.Frame(logs_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True)
        
        # Livello log
        ttk.Label(fields_frame, text="Livello Log:").grid(row=0, column=0, sticky=tk.W, pady=5)
        log_level_combo = ttk.Combobox(fields_frame, textvariable=self.log_level, 
                                      values=["DEBUG", "INFO", "WARNING", "ERROR"], 
                                      state="readonly", width=15)
        log_level_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Giorni di retention
        ttk.Label(fields_frame, text="Giorni di Retention:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.log_retention_days, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Auto cleanup
        ttk.Checkbutton(fields_frame, text="Pulizia automatica log", 
                       variable=self.log_auto_cleanup).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Pulsanti per gestione log
        log_buttons = ttk.Frame(fields_frame)
        log_buttons.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(log_buttons, text="Visualizza Log", 
                  command=self.view_logs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(log_buttons, text="Pulisci Log", 
                  command=self.clean_logs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(log_buttons, text="Esporta Log", 
                  command=self.export_logs).pack(side=tk.LEFT)
    
    def create_alarms_tab(self, notebook):
        """Crea il tab per la configurazione sveglie"""
        alarms_frame = ttk.Frame(notebook)
        notebook.add(alarms_frame, text="Configurazione Sveglie")
        
        # Titolo
        ttk.Label(alarms_frame, text="Configurazione Sistema Sveglie", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Frame per i campi
        fields_frame = ttk.Frame(alarms_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True)
        
        # Opzioni rinvio
        ttk.Label(fields_frame, text="Opzioni Rinvio (minuti, separate da ;):").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.snooze_options, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Max tentativi rinvio
        ttk.Label(fields_frame, text="Max Tentativi Rinvio:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.max_snooze_attempts, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Timeout chiamata
        ttk.Label(fields_frame, text="Timeout Chiamata (secondi):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.call_timeout, width=10).grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        fields_frame.columnconfigure(1, weight=1)
    
    def create_control_buttons(self, parent):
        """Crea i pulsanti di controllo"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Salva", 
                  command=self.save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Annulla", 
                  command=self.window.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Ripristina Default", 
                  command=self.reset_to_defaults).pack(side=tk.LEFT)
    
    def load_settings(self):
        """Carica le impostazioni dal file"""
        default_settings = {
            "pbx": PBX_CONFIG.copy(),
            "mail": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": "587",
                "username": "",
                "password": "",
                "recipients": "",
                "ssl": True
            },
            "log": {
                "level": "INFO",
                "retention_days": "30",
                "auto_cleanup": True
            },
            "rooms": HOTEL_CONFIG.copy(),
            "audio": AUDIO_CONFIG.copy(),
            "alarms": ALARM_CONFIG.copy()
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge con i default per campi mancanti
                    for key, value in default_settings.items():
                        if key not in loaded_settings:
                            loaded_settings[key] = value
                        elif isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if subkey not in loaded_settings[key]:
                                    loaded_settings[key][subkey] = subvalue
                    return loaded_settings
            except Exception as e:
                print(f"Errore nel caricamento impostazioni: {e}")
                return default_settings
        
        return default_settings
    
    def load_current_settings(self):
        """Popola i campi con le impostazioni correnti"""
        # PBX Settings
        self.pbx_host.set(self.settings["pbx"]["host"])
        self.pbx_port.set(str(self.settings["pbx"]["port"]))
        self.pbx_username.set(self.settings["pbx"]["username"])
        self.pbx_password.set(self.settings["pbx"]["password"])
        self.pbx_timeout.set(str(self.settings["pbx"]["timeout"]))
        
        # Mail Settings
        self.mail_enabled.set(self.settings["mail"]["enabled"])
        self.mail_smtp_server.set(self.settings["mail"]["smtp_server"])
        self.mail_smtp_port.set(self.settings["mail"]["smtp_port"])
        self.mail_username.set(self.settings["mail"]["username"])
        self.mail_password.set(self.settings["mail"]["password"])
        self.mail_recipients.set(self.settings["mail"]["recipients"])
        self.mail_ssl.set(self.settings["mail"]["ssl"])
        
        # Log Settings
        self.log_level.set(self.settings["log"]["level"])
        self.log_retention_days.set(self.settings["log"]["retention_days"])
        self.log_auto_cleanup.set(self.settings["log"]["auto_cleanup"])
        
        # Room Settings
        self.hotel_name.set(self.settings["rooms"]["name"])
        self.total_rooms.set(str(self.settings["rooms"]["total_rooms"]))
        self.room_prefix.set(self.settings["rooms"]["room_prefix"])
        self.room_start_number.set("101")
        
        # Audio Settings
        self.audio_volume.set(str(self.settings["audio"]["default_volume"]))
        self.audio_formats.set(", ".join(self.settings["audio"]["supported_formats"]))
        
        # Alarm Settings
        self.snooze_options.set("; ".join(map(str, self.settings["alarms"]["snooze_options"])))
        self.max_snooze_attempts.set(str(self.settings["alarms"]["max_snooze_attempts"]))
        self.call_timeout.set(str(self.settings["alarms"]["call_timeout"]))
    
    def save_settings(self):
        """Salva le impostazioni"""
        try:
            # Aggiorna le impostazioni
            self.settings["pbx"]["host"] = self.pbx_host.get()
            self.settings["pbx"]["port"] = int(self.pbx_port.get())
            self.settings["pbx"]["username"] = self.pbx_username.get()
            self.settings["pbx"]["password"] = self.pbx_password.get()
            self.settings["pbx"]["timeout"] = int(self.pbx_timeout.get())
            
            self.settings["mail"]["enabled"] = self.mail_enabled.get()
            self.settings["mail"]["smtp_server"] = self.mail_smtp_server.get()
            self.settings["mail"]["smtp_port"] = self.mail_smtp_port.get()
            self.settings["mail"]["username"] = self.mail_username.get()
            self.settings["mail"]["password"] = self.mail_password.get()
            self.settings["mail"]["recipients"] = self.mail_recipients.get()
            self.settings["mail"]["ssl"] = self.mail_ssl.get()
            
            self.settings["log"]["level"] = self.log_level.get()
            self.settings["log"]["retention_days"] = int(self.log_retention_days.get())
            self.settings["log"]["auto_cleanup"] = self.log_auto_cleanup.get()
            
            self.settings["rooms"]["name"] = self.hotel_name.get()
            self.settings["rooms"]["total_rooms"] = int(self.total_rooms.get())
            self.settings["rooms"]["room_prefix"] = self.room_prefix.get()
            
            self.settings["audio"]["default_volume"] = float(self.audio_volume.get())
            self.settings["audio"]["supported_formats"] = [f.strip() for f in self.audio_formats.get().split(",")]
            
            self.settings["alarms"]["snooze_options"] = [int(x.strip()) for x in self.snooze_options.get().split(";")]
            self.settings["alarms"]["max_snooze_attempts"] = int(self.max_snooze_attempts.get())
            self.settings["alarms"]["call_timeout"] = int(self.call_timeout.get())
            
            # Salva su file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            
            messagebox.showinfo("Successo", "Impostazioni salvate correttamente")
            
            # Callback per aggiornare l'applicazione principale
            if self.on_save_callback:
                self.on_save_callback(self.settings)
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel salvataggio: {e}")
    
    def reset_to_defaults(self):
        """Ripristina le impostazioni di default"""
        if messagebox.askyesno("Conferma", "Ripristinare tutte le impostazioni ai valori di default?"):
            self.load_current_settings()
    
    def test_pbx_connection(self):
        """Testa la connessione al centralino PBX con logging dettagliato"""
        import threading
        from pbx_connection import PBXConnection
        import logging
        
        logger = logging.getLogger(__name__)
        
        def test_connection_thread():
            """Thread per il test della connessione"""
            try:
                # Mostra dialog di attesa
                self.update_status("Test connessione PBX in corso...")
                logger.info("=" * 60)
                logger.info("INIZIO TEST CONNESSIONE PBX")
                logger.info("=" * 60)
                
                # Recupera le configurazioni correnti
                host = self.pbx_host.get().strip()
                port_str = self.pbx_port.get().strip()
                username = self.pbx_username.get().strip()
                password = self.pbx_password.get().strip()
                timeout_str = self.pbx_timeout.get().strip()
                
                # Validazione input
                logger.info(f"Host: {host}")
                logger.info(f"Port: {port_str}")
                logger.info(f"Username: {username}")
                logger.info(f"Password: {'*' * len(password) if password else '(vuota)'}")
                logger.info(f"Timeout: {timeout_str}s")
                
                if not host:
                    logger.error("Host non specificato!")
                    self.show_test_result(False, "Errore: Host PBX non specificato")
                    return
                
                if not username:
                    logger.error("Username non specificato!")
                    self.show_test_result(False, "Errore: Username non specificato")
                    return
                
                if not password:
                    logger.warning("Password non specificata!")
                    self.show_test_result(False, "Errore: Password non specificata")
                    return
                
                try:
                    port = int(port_str) if port_str else 22
                    timeout = int(timeout_str) if timeout_str else 10
                except ValueError as e:
                    logger.error(f"Errore conversione porta o timeout: {e}")
                    self.show_test_result(False, f"Errore: Porta o timeout non validi")
                    return
                
                logger.info(f"Parametri validati - Port: {port}, Timeout: {timeout}")
                
                # Crea configurazione temporanea
                temp_config = {
                    'host': host,
                    'port': port,
                    'username': username,
                    'password': password,
                    'timeout': timeout
                }
                
                # Crea connessione PBX temporanea
                logger.info("Creazione oggetto PBXConnection...")
                pbx = PBXConnection()
                
                # Sovrascrivi configurazione
                pbx.config = temp_config
                
                # Test 1: Tentativo connessione SSH
                logger.info("-" * 60)
                logger.info("TEST 1: Connessione SSH al PBX")
                logger.info(f"Tentativo connessione a {username}@{host}:{port}")
                logger.info(f"Timeout: {timeout} secondi")
                
                success = pbx.connect()
                
                if not success:
                    logger.error(f"Connessione SSH fallita")
                    self.show_test_result(False, f"❌ Connessione Fallita\n\nImpossibile connettersi a {host}:{port}\n\nVerifica:\n- IP e porta corretti\n- PBX raggiungibile\n- Credenziali corrette\n- SSH abilitato sul PBX\n\nDettagli nel log.")
                    return
                
                logger.info("✓ Connessione SSH stabilita con successo")
                
                # Test 2: Esecuzione comando di test
                logger.info("-" * 60)
                logger.info("TEST 2: Esecuzione comando di test")
                
                test_command = "echo 'PBX_TEST_CONNECTION'"
                logger.info(f"Comando: {test_command}")
                
                cmd_success, output, error = pbx.execute_command(test_command)
                
                if not cmd_success:
                    logger.error(f"Comando fallito: {error}")
                    pbx.disconnect()
                    self.show_test_result(False, f"❌ Test Comando Fallito\n\n{error}\n\nConnessione SSH OK ma comando non eseguito.")
                    return
                
                logger.info(f"✓ Comando eseguito con successo")
                logger.info(f"Output: {output}")
                
                # Test 3: Verifica comandi Asterisk (se disponibile)
                logger.info("-" * 60)
                logger.info("TEST 3: Verifica disponibilità Asterisk")
                
                asterisk_command = "asterisk -rx 'core show version'"
                logger.info(f"Comando: {asterisk_command}")
                
                ast_success, ast_output, ast_error = pbx.execute_command(asterisk_command)
                
                asterisk_available = False
                if ast_success and 'Asterisk' in ast_output:
                    logger.info(f"✓ Asterisk disponibile")
                    logger.info(f"Versione: {ast_output[:100]}")
                    asterisk_available = True
                else:
                    logger.warning("⚠ Asterisk non rilevato o comando non disponibile")
                    logger.warning(f"Output: {ast_output}")
                    logger.warning(f"Error: {ast_error}")
                
                # Chiudi connessione
                logger.info("-" * 60)
                logger.info("Chiusura connessione...")
                pbx.disconnect()
                logger.info("✓ Connessione chiusa")
                
                # Risultato finale
                logger.info("=" * 60)
                logger.info("TEST COMPLETATO CON SUCCESSO")
                logger.info("=" * 60)
                
                # Prepara messaggio risultato
                result_message = f"✅ Connessione PBX Riuscita!\n\n"
                result_message += f"Host: {host}:{port}\n"
                result_message += f"Username: {username}\n\n"
                result_message += f"✓ Connessione SSH: OK\n"
                result_message += f"✓ Esecuzione comandi: OK\n"
                
                if asterisk_available:
                    result_message += f"✓ Asterisk: Disponibile\n\n"
                    result_message += f"Versione:\n{ast_output[:150]}"
                else:
                    result_message += f"⚠ Asterisk: Non rilevato\n\n"
                    result_message += f"Nota: Verifica che Asterisk sia installato\n"
                    result_message += f"o che l'utente abbia i permessi necessari."
                
                self.show_test_result(True, result_message)
                
            except Exception as e:
                logger.error("=" * 60)
                logger.error(f"ERRORE IMPREVISTO NEL TEST: {e}")
                logger.error("=" * 60)
                import traceback
                logger.error(traceback.format_exc())
                
                self.show_test_result(
                    False, 
                    f"❌ Errore Imprevisto\n\n{str(e)}\n\nControlla il log per dettagli."
                )
        
        # Avvia test in thread separato
        threading.Thread(target=test_connection_thread, daemon=True).start()
    
    def show_test_result(self, success, message):
        """Mostra il risultato del test in una messagebox thread-safe"""
        def show_in_main_thread():
            if success:
                messagebox.showinfo("Test Connessione PBX", message)
            else:
                messagebox.showerror("Test Connessione PBX", message)
            self.update_status("Pronto")
        
        # Schedula nella main thread
        self.window.after(0, show_in_main_thread)
    
    def update_status(self, message):
        """Aggiorna la status bar (se disponibile)"""
        # Placeholder per futura status bar
        pass
    
    def test_mail(self):
        """Testa l'invio di una mail"""
        messagebox.showinfo("Test Mail", "Funzione di test mail in implementazione")
    
    def add_room(self):
        """Aggiunge una nuova camera"""
        messagebox.showinfo("Aggiungi Camera", "Funzione di aggiunta camera in implementazione")
    
    def edit_room(self):
        """Modifica una camera esistente"""
        messagebox.showinfo("Modifica Camera", "Funzione di modifica camera in implementazione")
    
    def delete_room(self):
        """Elimina una camera"""
        messagebox.showinfo("Elimina Camera", "Funzione di eliminazione camera in implementazione")
    
    def regenerate_rooms(self):
        """Rigenera tutte le camere"""
        messagebox.showinfo("Rigenera Camere", "Funzione di rigenerazione camere in implementazione")
    
    def view_logs(self):
        """Visualizza i log"""
        messagebox.showinfo("Visualizza Log", "Funzione di visualizzazione log in implementazione")
    
    def clean_logs(self):
        """Pulisce i log"""
        messagebox.showinfo("Pulisci Log", "Funzione di pulizia log in implementazione")
    
    def export_logs(self):
        """Esporta i log"""
        messagebox.showinfo("Esporta Log", "Funzione di esportazione log in implementazione")
