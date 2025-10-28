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
        self.wake_extension = tk.StringVar()
        self.wake_callerid = tk.StringVar()
        self.pbx_context = tk.StringVar()
        
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
        
        # Separatore
        ttk.Separator(fields_frame, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        
        # Sezione CallerID Sveglie
        ttk.Label(fields_frame, text="Configurazione CallerID Sveglie:", 
                 font=("Arial", 10, "bold")).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(5, 10))
        
        # Interno virtuale sveglie
        ttk.Label(fields_frame, text="Interno Virtuale Sveglie:").grid(row=7, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.wake_extension, width=10).grid(row=7, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        ttk.Label(fields_frame, text="(Es: 999 - appare sul display)", 
                 font=("Arial", 8), foreground="gray").grid(row=7, column=2, sticky=tk.W, padx=(5, 0))
        
        # Nome CallerID
        ttk.Label(fields_frame, text="Nome CallerID:").grid(row=8, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.wake_callerid, width=30).grid(row=8, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Label(fields_frame, text="(Es: Servizio Sveglie)", 
                 font=("Arial", 8), foreground="gray").grid(row=8, column=2, sticky=tk.W, padx=(5, 0))
        
        # Context Asterisk
        ttk.Label(fields_frame, text="Context Asterisk:").grid(row=9, column=0, sticky=tk.W, pady=5)
        ttk.Entry(fields_frame, textvariable=self.pbx_context, width=30).grid(row=9, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Label(fields_frame, text="(Di solito: from-internal)", 
                 font=("Arial", 8), foreground="gray").grid(row=9, column=2, sticky=tk.W, padx=(5, 0))
        
        # Pulsanti
        buttons_frame = ttk.Frame(fields_frame)
        buttons_frame.grid(row=10, column=0, columnspan=3, pady=20)
        
        ttk.Button(buttons_frame, text="Test Connessione", 
                  command=self.test_pbx_connection).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="Configura Context DTMF", 
                  command=self.setup_dtmf_context).pack(side=tk.LEFT, padx=5)
        
        fields_frame.columnconfigure(1, weight=1)
    
    def create_rooms_tab(self, notebook):
        """Tab Camere - Redirect a gestione camere completa"""
        rooms_frame = ttk.Frame(notebook)
        notebook.add(rooms_frame, text="Configurazione Camere")
        
        # Contenitore centrale
        center_frame = ttk.Frame(rooms_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Icona e titolo
        ttk.Label(center_frame, text="🏨", font=("Arial", 72)).pack(pady=(0, 20))
        ttk.Label(center_frame, text="Gestione Camere Hotel", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 10))
        
        # Descrizione
        description = (
            "Per gestire le camere dell'hotel usa la finestra dedicata\n"
            "che include tutte le funzionalità avanzate:\n\n"
            "• Import automatico interni da PBX\n"
            "• Stato online/offline in tempo reale\n"
            "• Descrizioni personalizzate\n"
            "• Colori e etichette per organizzazione\n"
            "• Gestione completa interno telefonico"
        )
        ttk.Label(center_frame, text=description, 
                 font=("Arial", 10), justify=tk.CENTER).pack(pady=(0, 30))
        
        # Pulsante grande per aprire gestione camere
        open_btn = ttk.Button(center_frame, text="🚀 Apri Gestione Camere Completa", 
                             command=self.open_room_manager)
        open_btn.pack(pady=(0, 10))
        
        # Info aggiuntiva
        ttk.Label(center_frame, text="(Oppure usa: Menu → Gestione → Gestisci Camere)", 
                 font=("Arial", 9), foreground="gray").pack()
    
    def open_room_manager(self):
        """Apre la finestra di gestione camere completa"""
        from room_manager import RoomManagerWindow
        from database import DatabaseManager
        
        # Chiude la finestra settings
        self.window.destroy()
        
        # Apre room manager
        db = DatabaseManager()
        RoomManagerWindow(self.parent, db)
    
    def create_audio_tab(self, notebook):
        """Tab Audio - Redirect a gestione audio completa"""
        audio_frame = ttk.Frame(notebook)
        notebook.add(audio_frame, text="Messaggi Audio")
        
        # Contenitore centrale
        center_frame = ttk.Frame(audio_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Icona e titolo
        ttk.Label(center_frame, text="🔊", font=("Arial", 72)).pack(pady=(0, 20))
        ttk.Label(center_frame, text="Gestione Messaggi Audio", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 10))
        
        # Descrizione
        description = (
            "Per gestire i messaggi audio usa la finestra dedicata\n"
            "che include tutte le funzionalità avanzate:\n\n"
            "• Upload file MP3, WAV, OGG\n"
            "• Preview e test audio\n"
            "• Selezione lingua per messaggio\n"
            "• Azioni associate (sveglia, conferma, saluto)\n"
            "• Gestione categorie e durata"
        )
        ttk.Label(center_frame, text=description, 
                 font=("Arial", 10), justify=tk.CENTER).pack(pady=(0, 30))
        
        # Pulsante grande
        ttk.Button(center_frame, text="🚀 Apri Gestione Audio Completa", 
                  command=self.open_audio_manager).pack(pady=(0, 10))
        
        # Info aggiuntiva
        ttk.Label(center_frame, text="(Oppure usa: Menu → Gestione → Gestisci Messaggi Audio)", 
                 font=("Arial", 9), foreground="gray").pack()
    
    def open_audio_manager(self):
        """Apre la finestra di gestione audio completa"""
        from audio_manager import AudioManagerWindow
        from database import DatabaseManager
        
        # Chiude la finestra settings
        self.window.destroy()
        
        # Apre audio manager
        db = DatabaseManager()
        AudioManagerWindow(self.parent, db)
    
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
        """Tab Log - Redirect a visualizzatore log completo"""
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="Log e Monitoraggio")
        
        # Contenitore centrale
        center_frame = ttk.Frame(logs_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Icona e titolo
        ttk.Label(center_frame, text="📋", font=("Arial", 72)).pack(pady=(0, 20))
        ttk.Label(center_frame, text="Visualizzatore Log e Monitoraggio", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 10))
        
        # Descrizione
        description = (
            "Per visualizzare i log usa la finestra dedicata\n"
            "che include tutte le funzionalità avanzate:\n\n"
            "• Visualizzazione log in tempo reale\n"
            "• Filtri per livello (DEBUG, INFO, WARNING, ERROR)\n"
            "• Ricerca nel testo dei log\n"
            "• Export log in formato TXT\n"
            "• Pulizia e gestione retention"
        )
        ttk.Label(center_frame, text=description, 
                 font=("Arial", 10), justify=tk.CENTER).pack(pady=(0, 30))
        
        # Pulsanti
        btn_frame = ttk.Frame(center_frame)
        btn_frame.pack(pady=(0, 10))
        
        ttk.Button(btn_frame, text="📋 Visualizza Log", 
                  command=self.open_log_viewer).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="📊 Monitor Sistema", 
                  command=self.open_system_monitor_direct).pack(side=tk.LEFT)
        
        # Info aggiuntiva
        ttk.Label(center_frame, text="(Oppure usa: Menu → Gestione → Visualizza Log / Monitor di Sistema)", 
                 font=("Arial", 9), foreground="gray").pack()
    
    def open_log_viewer(self):
        """Apre il visualizzatore log"""
        from log_viewer import LogViewerWindow
        
        # Chiude la finestra settings
        self.window.destroy()
        
        # Apre log viewer
        LogViewerWindow(self.parent)
    
    def open_system_monitor_direct(self):
        """Apre il monitor di sistema"""
        from system_monitor import SystemMonitorWindow
        from database import DatabaseManager
        
        # Chiude la finestra settings
        self.window.destroy()
        
        # Apre system monitor
        db = DatabaseManager()
        SystemMonitorWindow(self.parent, db)
    
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
        self.wake_extension.set(self.settings["pbx"].get("wake_extension", "999"))
        self.wake_callerid.set(self.settings["pbx"].get("wake_callerid", "Servizio Sveglie"))
        self.pbx_context.set(self.settings["pbx"].get("context", "from-internal"))
        
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
            self.settings["pbx"]["wake_extension"] = self.wake_extension.get()
            self.settings["pbx"]["wake_callerid"] = self.wake_callerid.get()
            self.settings["pbx"]["context"] = self.pbx_context.get()
            
            # Salva su file usando la funzione di config
            from config import save_user_config, PBX_CONFIG
            if save_user_config(self.settings):
                # Aggiorna anche PBX_CONFIG in memoria
                PBX_CONFIG.update(self.settings["pbx"])
            
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
    
    def setup_dtmf_context(self):
        """Configura il context wakeup-service sul PBX per gestire DTMF"""
        import threading
        from pbx_connection import PBXConnection
        
        result = messagebox.askyesno(
            "Configurazione Context DTMF",
            "Questa operazione creerà il context 'wakeup-service'\n"
            "nel dialplan di Asterisk per gestire lo snooze con DTMF.\n\n"
            "Il context verrà salvato in:\n"
            "/etc/asterisk/extensions_custom.conf\n\n"
            "Continuare?",
            icon='question'
        )
        
        if not result:
            return
        
        def setup_thread():
            try:
                self.update_status("Configurazione context DTMF in corso...")
                
                # Crea connessione PBX
                pbx_config = {
                    'host': self.pbx_host.get().strip(),
                    'port': int(self.pbx_port.get().strip()) if self.pbx_port.get().strip() else 22,
                    'username': self.pbx_username.get().strip(),
                    'password': self.pbx_password.get().strip(),
                    'timeout': int(self.pbx_timeout.get().strip()) if self.pbx_timeout.get().strip() else 10
                }
                
                pbx = PBXConnection(config=pbx_config)
                
                # Setup context
                success, message = pbx.setup_wakeup_context()
                
                if success:
                    messagebox.showinfo(
                        "Setup Completato",
                        "✅ Context 'wakeup-service' configurato con successo!\n\n"
                        "Il dialplan è stato aggiornato e caricato.\n\n"
                        "Ora le sveglie potranno rilevare l'input DTMF\n"
                        "per lo snooze (1 = 5min, 2 = 10min)."
                    )
                else:
                    messagebox.showerror(
                        "Errore Setup",
                        f"Errore nella configurazione del context:\n\n{message}\n\n"
                        "Verifica i log per dettagli."
                    )
                
                self.update_status("")
                pbx.disconnect()
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante il setup:\n{e}")
                self.update_status("")
        
        threading.Thread(target=setup_thread, daemon=True).start()
    
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
                
                output, error = pbx.execute_command(test_command)
                
                if error:
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
                
                ast_output, ast_error = pbx.execute_command(asterisk_command)
                
                asterisk_available = False
                if ast_output and 'Asterisk' in ast_output:
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
    
    # Metodi obsoleti rimossi - ora si usano finestre dedicate:
    # - RoomManagerWindow per camere
    # - AudioManagerWindow per audio
    # - LogViewerWindow per log
    # - SystemMonitorWindow per monitoraggio
