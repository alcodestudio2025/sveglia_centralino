"""
Sistema di Gestione Sveglie per Hotel
Applicazione principale con interfaccia grafica semplificata
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import threading
import os
import sys
import tempfile
import shutil
from PIL import Image, ImageTk
from config import create_directories, PBX_CONFIG, AUDIO_CONFIG
from database import DatabaseManager
from settings import SettingsWindow
from pbx_connection import PBXConnection, PBXManager
from alarm_manager import AlarmManager
from room_manager import RoomManagerWindow
from audio_manager import AudioManagerWindow
from log_viewer import LogViewerWindow
from system_monitor import SystemMonitorWindow
from backup_manager import BackupManagerWindow
from logger import get_logger

class SvegliaCentralinoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Gestione Sveglie Hotel")
        self.root.geometry("1000x700")
        
        # Imposta icona della finestra (app_icon_2 per taskbar e title bar)
        # IMPORTANTE: Quando PyInstaller crea l'exe, l'icona specificata in build_exe.spec
        # viene integrata nell'exe stesso. Usiamo il percorso dell'exe per l'icona.
        icon_loaded = False
        try:
            if getattr(sys, 'frozen', False):
                # Ambiente exe: prova prima con l'icona integrata nell'exe
                exe_path = sys.executable
                try:
                    # Metodo 1: usa direttamente il percorso dell'exe (l'icona è integrata)
                    self.root.iconbitmap(exe_path)
                    icon_loaded = True
                except Exception as e1:
                    # Metodo 2: prova a caricare dall'assets incluso
                    try:
                        base_path = sys._MEIPASS
                        icon_path = os.path.join(base_path, 'assets', 'app_icon_2.ico')
                        if os.path.exists(icon_path):
                            # Estrai in temp per evitare problemi di percorso
                            temp_dir = tempfile.gettempdir()
                            temp_icon_path = os.path.join(temp_dir, 'wakeup_manager_icon.ico')
                            shutil.copy2(icon_path, temp_icon_path)
                            self.root.iconbitmap(temp_icon_path)
                            icon_loaded = True
                    except Exception as e2:
                        # Metodo 3: usa iconphoto come ultima risorsa
                        try:
                            base_path = sys._MEIPASS
                            icon_path = os.path.join(base_path, 'assets', 'app_icon_2.ico')
                            if os.path.exists(icon_path):
                                icon_img = Image.open(icon_path)
                                # Converti in formato compatibile
                                if icon_img.mode != 'RGBA':
                                    icon_img = icon_img.convert('RGBA')
                                icon_img = icon_img.resize((32, 32), Image.Resampling.LANCZOS)
                                icon_photo = ImageTk.PhotoImage(icon_img)
                                self.root.iconphoto(True, icon_photo)
                                icon_loaded = True
                        except:
                            pass
            else:
                # Ambiente normale (Python): carica da assets
                base_path = os.path.dirname(os.path.abspath(__file__))
                icon_path = os.path.join(base_path, 'assets', 'app_icon_2.ico')
                if os.path.exists(icon_path):
                    try:
                        self.root.iconbitmap(icon_path)
                        icon_loaded = True
                    except:
                        try:
                            icon_img = Image.open(icon_path)
                            if icon_img.mode != 'RGBA':
                                icon_img = icon_img.convert('RGBA')
                            icon_img = icon_img.resize((32, 32), Image.Resampling.LANCZOS)
                            icon_photo = ImageTk.PhotoImage(icon_img)
                            self.root.iconphoto(True, icon_photo)
                            icon_loaded = True
                        except:
                            pass
        except Exception as e:
            # Log errore
            try:
                if hasattr(self, 'logger'):
                    self.logger.warning(f"Impossibile caricare icona finestra: {e}")
                else:
                    print(f"Impossibile caricare icona finestra: {e}")
            except:
                pass
        
        # Inizializza database
        self.db = DatabaseManager()
        
        # Inizializza gestione PBX e sveglie
        self.pbx = PBXManager()
        self.alarm_manager = AlarmManager(self.db, self.pbx)
        
        # Inizializza logger
        self.logger = get_logger('main')
        
        # Crea cartelle necessarie
        create_directories()
        
        # Variabili per l'interfaccia
        self.selected_room = tk.StringVar()
        self.alarm_time = tk.StringVar()
        self.selected_language = tk.StringVar(value="it")  # Lingua invece di messaggio audio
        
        # Crea l'interfaccia
        self.create_widgets()
        
        # Carica dati iniziali
        self.load_rooms()
        self.load_alarms()
        
        # Avvia il gestore sveglie
        self.alarm_manager.start()
        self.logger.info("Gestore sveglie avviato")
        
        # Testa la connessione PBX all'avvio (usa impostazioni salvate)
        self.test_pbx_on_startup()
    
    def create_widgets(self):
        """Crea l'interfaccia grafica principale semplificata"""
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurazione griglia
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Barra del menu
        self.create_menu_bar()
        
        # Frame per header con icona e titolo
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))
        header_frame.columnconfigure(1, weight=1)
        
        # Icona principale (logo_sveglia1) in alto a sinistra
        try:
            if os.path.exists('assets/logo_sveglia1.png'):
                icon1_img = Image.open('assets/logo_sveglia1.png')
                # Ridimensiona l'icona a circa 50x50px
                icon1_img = icon1_img.resize((50, 50), Image.Resampling.LANCZOS)
                icon1_photo = ImageTk.PhotoImage(icon1_img)
                icon1_label = ttk.Label(header_frame, image=icon1_photo)
                icon1_label.image = icon1_photo  # Mantieni riferimento
                icon1_label.grid(row=0, column=0, padx=(0, 15), sticky=tk.W)
        except Exception as e:
            print(f"Impossibile caricare icona principale: {e}")
        
        # Titolo
        title_label = ttk.Label(header_frame, text="Sistema Gestione Sveglie Hotel", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=1, sticky=tk.W)
        
        # Sezione 1: Impostazione sveglia (semplificata)
        self.create_alarm_section(main_frame, row=1)
        
        # Sezione 2: Report sveglie attive con possibilità di modifica
        self.create_alarms_report_section(main_frame, row=2)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Sistema pronto")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        # Aggiungi logo in basso a destra
        self.add_logo(main_frame, row=4, column=1)
    
    def create_menu_bar(self):
        """Crea la barra del menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Impostazioni", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.root.quit)
        
        # Menu Gestione
        manage_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Gestione", menu=manage_menu)
        manage_menu.add_command(label="Test Connessione PBX", command=self.test_pbx_connection)
        manage_menu.add_separator()
        manage_menu.add_command(label="Gestisci Camere", command=self.manage_rooms)
        manage_menu.add_command(label="Gestisci Messaggi Audio", command=self.manage_audio)
        manage_menu.add_separator()
        manage_menu.add_command(label="Visualizza Log", command=self.view_logs)
        manage_menu.add_command(label="Monitor di Sistema", command=self.open_system_monitor)
        manage_menu.add_command(label="Backup e Ripristino", command=self.open_backup_manager)
        
        # Menu Aiuto
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aiuto", menu=help_menu)
        help_menu.add_command(label="Informazioni", command=self.show_about)
    
    def create_alarm_section(self, parent, row):
        """Crea la sezione semplificata per impostare nuove sveglie"""
        # Frame per impostazione sveglia
        alarm_frame = ttk.LabelFrame(parent, text="Imposta Nuova Sveglia", padding="15")
        alarm_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        alarm_frame.columnconfigure(1, weight=1)
        
        # Prima riga: Camera, Data, Ora
        row1_frame = ttk.Frame(alarm_frame)
        row1_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row1_frame.columnconfigure(1, weight=1)
        row1_frame.columnconfigure(3, weight=1)
        
        # Camera
        ttk.Label(row1_frame, text="Camera:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.room_combo = ttk.Combobox(row1_frame, textvariable=self.selected_room, 
                                      state="readonly", width=15)
        self.room_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20))
        
        # Data
        ttk.Label(row1_frame, text="Data:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.date_entry = ttk.Entry(row1_frame, width=12)
        self.date_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 20))
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        
        # Ora (interattiva - si aggiorna all'ora attuale)
        ttk.Label(row1_frame, text="Ora:").grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
        self.time_entry = ttk.Entry(row1_frame, width=8)
        self.time_entry.grid(row=0, column=5, sticky=tk.W)
        # Imposta ora corrente + 1 ora come default
        default_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%H:%M")
        self.time_entry.insert(0, default_time)
        
        # Aggiungi binding per aggiornare l'ora quando si clicca sul campo
        self.time_entry.bind('<FocusIn>', self.update_time_to_current)
        
        # Seconda riga: Messaggio audio e pulsanti
        row2_frame = ttk.Frame(alarm_frame)
        row2_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        row2_frame.columnconfigure(1, weight=1)
        
        # Messaggio audio
        ttk.Label(row2_frame, text="Lingua:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.language_combo = ttk.Combobox(row2_frame, textvariable=self.selected_language, 
                                          values=["it", "en", "fr", "de", "es"],
                                          state="readonly", width=15)
        self.language_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Pulsanti
        ttk.Button(row2_frame, text="Imposta Sveglia", 
                  command=self.set_alarm).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(row2_frame, text="Test Audio", 
                  command=self.test_audio).grid(row=0, column=3)
    
    def create_alarms_report_section(self, parent, row):
        """Crea la sezione report sveglie con possibilità di modifica"""
        # Frame per report sveglie
        report_frame = ttk.LabelFrame(parent, text="Report Sveglie Attive e Posticipate", padding="15")
        report_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        report_frame.columnconfigure(0, weight=1)
        report_frame.rowconfigure(1, weight=1)
        
        # Pulsanti di controllo
        controls_frame = ttk.Frame(report_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Button(controls_frame, text="Aggiorna", 
                  command=self.load_alarms).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="Modifica Selezionata", 
                  command=self.edit_selected_alarm).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="Elimina Selezionata", 
                  command=self.delete_selected_alarm).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="Posticipa Selezionata", 
                  command=self.snooze_selected_alarm).pack(side=tk.LEFT, padx=(0, 10))
        
        # Lista sveglie con colonne estese
        columns = ("ID", "Camera", "Data", "Ora", "Messaggio", "Status", "Tipo")
        self.alarms_tree = ttk.Treeview(report_frame, columns=columns, show="headings", height=12)
        
        # Configurazione colonne
        column_widths = {"ID": 50, "Camera": 80, "Data": 100, "Ora": 80, 
                        "Messaggio": 200, "Status": 100, "Tipo": 80}
        
        for col in columns:
            self.alarms_tree.heading(col, text=col)
            self.alarms_tree.column(col, width=column_widths.get(col, 120))
        
        # Scrollbar per la lista
        scrollbar = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, command=self.alarms_tree.yview)
        self.alarms_tree.configure(yscrollcommand=scrollbar.set)
        
        self.alarms_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Bind per doppio click per modifica rapida
        self.alarms_tree.bind("<Double-1>", self.on_alarm_double_click)
    
    # Metodi per il menu
    def open_settings(self):
        """Apre la finestra delle impostazioni"""
        SettingsWindow(self.root, self.on_settings_saved)
    
    def on_settings_saved(self, settings):
        """Callback quando le impostazioni vengono salvate"""
        self.status_var.set("Impostazioni aggiornate")
        # Ricarica i dati se necessario
        self.load_rooms()
        self.load_alarms()
    
    def manage_rooms(self):
        """Apre la gestione delle camere"""
        RoomManagerWindow(self.root, self.db, self.on_rooms_updated)
    
    def on_rooms_updated(self):
        """Callback quando le camere vengono aggiornate"""
        self.load_rooms()
        self.status_var.set("Lista camere aggiornata")
    
    def manage_audio(self):
        """Apre la gestione dei messaggi audio"""
        AudioManagerWindow(self.root, self.db, self.on_audio_updated)
    
    def on_audio_updated(self):
        """Callback quando i messaggi audio vengono aggiornati"""
        # I messaggi audio vengono caricati automaticamente quando serve
        self.status_var.set("Lista messaggi audio aggiornata")
    
    def view_logs(self):
        """Visualizza i log del sistema"""
        LogViewerWindow(self.root)
    
    def open_system_monitor(self):
        """Apre il monitor di sistema"""
        SystemMonitorWindow(self.root, self.db, self.alarm_manager)
    
    def open_backup_manager(self):
        """Apre il gestore di backup"""
        BackupManagerWindow(self.root, self.db)
    
    def show_about(self):
        """Mostra informazioni sull'applicazione"""
        about_text = """Sistema di Gestione Sveglie per Hotel
Versione 1.0 Beta

Sviluppato per la gestione centralizzata delle sveglie
in hotel con centralino PBX.

Funzionalità:
- Impostazione sveglie per camere
- Gestione messaggi audio personalizzati
- Sistema di rinvio automatico
- Report e monitoraggio sveglie
- Integrazione SSH con centralino PBX

---
Produttore: AL Code Studio 2025
Email: alcodestudio2025@gmail.com"""
        
        messagebox.showinfo("Informazioni", about_text)
    
    # Metodi per la gestione delle sveglie
    def on_alarm_double_click(self, event):
        """Gestisce il doppio click su una sveglia per modifica rapida"""
        self.edit_selected_alarm()
    
    def edit_selected_alarm(self):
        """Modifica la sveglia selezionata"""
        selection = self.alarms_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona una sveglia da modificare")
            return
        
        item = self.alarms_tree.item(selection[0])
        alarm_id = item['values'][0]
        
        # Apri finestra di modifica
        self.open_alarm_edit_dialog(alarm_id)
    
    def open_alarm_edit_dialog(self, alarm_id):
        """Apre la finestra di modifica sveglia"""
        # Ottieni i dati della sveglia
        alarm = self.db.get_alarm(alarm_id)
        if not alarm:
            messagebox.showerror("Errore", "Sveglia non trovata")
            return
        
        # Crea finestra di dialogo
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Modifica Sveglia")
        edit_window.geometry("400x300")
        edit_window.resizable(False, False)
        
        # Centra la finestra
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Frame principale
        main_frame = ttk.Frame(edit_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titolo
        ttk.Label(main_frame, text=f"Modifica Sveglia - Camera {alarm[1]}", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Form di modifica
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Data
        ttk.Label(form_frame, text="Data:").grid(row=0, column=0, sticky=tk.W, pady=5)
        date_entry = ttk.Entry(form_frame, width=15)
        date_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        alarm_time = datetime.datetime.fromisoformat(alarm[2])
        date_entry.insert(0, alarm_time.strftime("%Y-%m-%d"))
        
        # Ora
        ttk.Label(form_frame, text="Ora:").grid(row=1, column=0, sticky=tk.W, pady=5)
        time_entry = ttk.Entry(form_frame, width=15)
        time_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        time_entry.insert(0, alarm_time.strftime("%H:%M"))
        
        # Lingua (se c'è audio message)
        ttk.Label(form_frame, text="Lingua:").grid(row=2, column=0, sticky=tk.W, pady=5)
        language_var = tk.StringVar(value="it")
        
        # Trova lingua dell'audio corrente
        if alarm[3]:  # Se c'è un audio_message_id
            audio_messages = self.db.get_audio_messages()
            for msg in audio_messages:
                if msg[0] == alarm[3]:
                    language_var.set(msg[5] if len(msg) > 5 else "it")
                    break
        
        language_combo = ttk.Combobox(form_frame, textvariable=language_var, 
                                     values=["it", "en", "fr", "de", "es"],
                                     state="readonly", width=12)
        language_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        form_frame.columnconfigure(1, weight=1)
        
        # Pulsanti
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save_changes():
            try:
                date_str = date_entry.get()
                time_str = time_entry.get()
                language = language_var.get()
                
                # Valida e combina data e ora
                new_alarm_time = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                
                # Verifica che la data sia nel futuro
                if new_alarm_time <= datetime.datetime.now():
                    messagebox.showerror("Errore", "La sveglia deve essere programmata nel futuro")
                    return
                
                # Trova audio message per la lingua selezionata
                audio_id = None
                messages = self.db.get_audio_messages()
                for msg in messages:
                    msg_language = msg[5] if len(msg) > 5 else 'it'
                    msg_action = msg[6] if len(msg) > 6 else None
                    
                    if msg_language.lower() == language.lower() and msg_action == 'wake_up':
                        audio_id = msg[0]
                        break
                
                # Aggiorna la sveglia
                success = self.db.update_alarm(alarm_id, new_alarm_time.isoformat(), audio_id)
                
                if success:
                    messagebox.showinfo("Successo", "Sveglia modificata con successo")
                    self.load_alarms()
                    self.status_var.set(f"Sveglia {alarm_id} modificata")
                    edit_window.destroy()
                else:
                    messagebox.showerror("Errore", "Errore nella modifica della sveglia")
                    
            except ValueError as e:
                messagebox.showerror("Errore", f"Formato data/ora non valido: {e}")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore: {e}")
        
        ttk.Button(buttons_frame, text="Salva", command=save_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Annulla", command=edit_window.destroy).pack(side=tk.RIGHT)
    
    def snooze_selected_alarm(self):
        """Posticipa la sveglia selezionata"""
        selection = self.alarms_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona una sveglia da posticipare")
            return
        
        item = self.alarms_tree.item(selection[0])
        alarm_id = item['values'][0]
        room = item['values'][1]
        
        # Apri finestra di selezione rinvio
        self.open_snooze_dialog(alarm_id, room)
    
    def open_snooze_dialog(self, alarm_id, room):
        """Apre la finestra per selezionare il rinvio"""
        # Crea finestra di dialogo per selezione rinvio
        snooze_window = tk.Toplevel(self.root)
        snooze_window.title("Posticipa Sveglia")
        snooze_window.geometry("350x280")
        snooze_window.resizable(False, False)
        
        # Centra la finestra
        snooze_window.transient(self.root)
        snooze_window.grab_set()
        
        # Frame principale
        main_frame = ttk.Frame(snooze_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titolo
        ttk.Label(main_frame, text=f"Posticipa Sveglia Camera {room}", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Opzioni di rinvio
        snooze_var = tk.IntVar(value=5)
        
        ttk.Radiobutton(main_frame, text="5 minuti", variable=snooze_var, value=5).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(main_frame, text="10 minuti", variable=snooze_var, value=10).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(main_frame, text="15 minuti", variable=snooze_var, value=15).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(main_frame, text="30 minuti", variable=snooze_var, value=30).pack(anchor=tk.W, pady=2)
        
        # Pulsanti
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        def apply_snooze():
            minutes = snooze_var.get()
            success, message = self.alarm_manager.snooze_alarm(alarm_id, minutes)
            
            if success:
                messagebox.showinfo("Successo", message)
                self.load_alarms()
                self.status_var.set(f"Sveglia posticipata di {minutes} minuti")
            else:
                messagebox.showerror("Errore", message)
            
            snooze_window.destroy()
        
        ttk.Button(buttons_frame, text="Applica", command=apply_snooze).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Annulla", command=snooze_window.destroy).pack(side=tk.RIGHT)
    
    def test_pbx_on_startup(self):
        """Testa la connessione PBX all'avvio dell'applicazione"""
        def test_connection():
            try:
                # Verifica se il PBX è configurato (non valori di default)
                if PBX_CONFIG.get('host') == '192.168.1.100' and PBX_CONFIG.get('password') == 'password':
                    # Configurazione di default - non testare
                    self.status_var.set("PBX non configurato - Vai in Impostazioni")
                    self.logger.info("PBX non configurato (valori di default)")
                    self.logger.info("Configura il PBX in: Menu → Impostazioni → Connessione PBX")
                    return
                
                # Test reale con configurazione salvata
                self.logger.info("="*60)
                self.logger.info("TEST CONNESSIONE PBX ALL'AVVIO")
                self.logger.info("="*60)
                self.logger.info(f"Host: {PBX_CONFIG.get('host')}:{PBX_CONFIG.get('port')}")
                self.logger.info(f"Username: {PBX_CONFIG.get('username')}")
                
                success, message = self.alarm_manager.test_pbx_connection()
                
                if success:
                    self.status_var.set("✓ Connessione PBX: OK")
                    self.logger.info("✓ Connessione PBX all'avvio: SUCCESSO")
                    self.logger.info("="*60)
                    
                    # Mostra popup di successo con chiusura automatica
                    self.show_success_popup()
                else:
                    self.status_var.set("✗ Connessione PBX: ERRORE")
                    self.logger.error(f"✗ Connessione PBX all'avvio: FALLITA - {message}")
                    self.logger.info("="*60)
                    
                    # Mostra popup solo se configurato ma non raggiungibile
                    messagebox.showwarning("Connessione PBX", 
                                         f"Impossibile connettersi al centralino PBX:\n{message}\n\n"
                                         f"Il sistema funzionerà ma le sveglie non potranno\n"
                                         f"essere eseguite fino alla risoluzione del problema.\n\n"
                                         f"Verifica in: Menu → Impostazioni → Test Connessione")
                    
            except Exception as e:
                self.logger.error(f"Errore nel test PBX all'avvio: {e}")
                self.status_var.set("Errore test PBX - Verifica configurazione")
        
        # Esegue il test in un thread separato per non bloccare l'UI
        threading.Thread(target=test_connection, daemon=True).start()
    
    def show_success_popup(self):
        """Mostra popup di successo connessione PBX con chiusura automatica"""
        def show_popup():
            # Crea finestra popup
            popup = tk.Toplevel(self.root)
            popup.title("Connessione PBX")
            popup.geometry("400x200")
            popup.resizable(False, False)
            
            # Centra la finestra
            popup.transient(self.root)
            popup.grab_set()
            
            # Frame principale
            main_frame = ttk.Frame(popup, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Icona e messaggio successo
            success_frame = ttk.Frame(main_frame)
            success_frame.pack(pady=(10, 20))
            
            # Emoji/simbolo successo
            ttk.Label(success_frame, text="✓", font=("Arial", 48, "bold"), 
                     foreground="green").pack()
            
            # Messaggio principale
            ttk.Label(main_frame, text="Connessione PBX Stabilita", 
                     font=("Arial", 14, "bold")).pack(pady=(0, 10))
            
            # Dettagli connessione
            details_text = f"Host: {PBX_CONFIG.get('host')}:{PBX_CONFIG.get('port')}\n"
            details_text += f"Username: {PBX_CONFIG.get('username')}\n"
            details_text += f"Asterisk: Disponibile"
            
            ttk.Label(main_frame, text=details_text, 
                     font=("Arial", 10)).pack(pady=(0, 15))
            
            # Label countdown
            countdown_var = tk.StringVar(value="Chiusura automatica in 5 secondi...")
            countdown_label = ttk.Label(main_frame, textvariable=countdown_var, 
                                       font=("Arial", 9), foreground="gray")
            countdown_label.pack(pady=(10, 0))
            
            # Countdown e chiusura automatica
            def countdown(seconds):
                if seconds > 0 and popup.winfo_exists():
                    countdown_var.set(f"Chiusura automatica in {seconds} secondi...")
                    popup.after(1000, countdown, seconds - 1)
                elif popup.winfo_exists():
                    popup.destroy()
            
            # Avvia countdown
            countdown(5)
            
            # Pulsante chiusura manuale
            ttk.Button(main_frame, text="Chiudi Ora", 
                      command=popup.destroy).pack(pady=(5, 0))
        
        # Esegue nella main thread
        self.root.after(0, show_popup)
    
    def test_pbx_connection(self):
        """Testa la connessione PBX manualmente"""
        def test_connection():
            success, message = self.alarm_manager.test_pbx_connection()
            if success:
                messagebox.showinfo("Test Connessione", "Connessione PBX riuscita!")
                self.status_var.set("Connessione PBX: OK")
            else:
                messagebox.showerror("Test Connessione", f"Errore connessione PBX:\n{message}")
                self.status_var.set(f"Connessione PBX: ERRORE")
        
        # Esegue il test in un thread separato
        threading.Thread(target=test_connection, daemon=True).start()
    
    
    def load_rooms(self):
        """Carica le camere disponibili"""
        rooms = self.db.get_rooms('available')
        room_numbers = [room[1] for room in rooms]
        self.room_combo['values'] = room_numbers
        if room_numbers:
            self.room_combo.set(room_numbers[0])
    
    def load_alarms(self):
        """Carica le sveglie attive e posticipate"""
        # Carica sveglie programmate e posticipate
        alarms = self.db.get_alarms()
        self.alarms_tree.delete(*self.alarms_tree.get_children())
        
        # Carica TUTTI gli audio UNA SOLA VOLTA prima del loop (performance)
        audio_messages = self.db.get_audio_messages()
        audio_dict = {msg[0]: msg[1] for msg in audio_messages}  # Crea dizionario ID -> Nome
        
        for alarm in alarms:
            alarm_time = datetime.datetime.fromisoformat(alarm[2])
            date_str = alarm_time.strftime("%Y-%m-%d")
            time_str = alarm_time.strftime("%H:%M")
            
            # Ottieni nome messaggio audio dal dizionario (veloce!)
            audio_name = "Nessuno"
            if alarm[3]:  # Se c'è un audio_message_id
                audio_name = audio_dict.get(alarm[3], "Nessuno")
            
            # Determina il colore in base allo status
            status = alarm[4]
            snooze_count = alarm[5] if len(alarm) > 5 else 0
            
            # Determina il tipo: Originale o Rinvio
            tipo = "Originale" if snooze_count == 0 else f"Rinvio ({snooze_count})"
            
            # Inserisci nella lista con ID visibile
            item_id = self.alarms_tree.insert("", "end", values=(
                alarm[0],  # ID
                alarm[1],  # Camera
                date_str,  # Data
                time_str,  # Ora
                audio_name,  # Messaggio
                status,    # Status
                tipo       # Tipo (Originale/Rinvio)
            ))
            
            # Colora le righe in base allo status
            if status == "completed":
                self.alarms_tree.set(item_id, "Status", "Completata")
            elif status == "cancelled":
                self.alarms_tree.set(item_id, "Status", "Cancellata")
            elif status == "snoozed":
                self.alarms_tree.set(item_id, "Status", "Posticipata")
            else:
                self.alarms_tree.set(item_id, "Status", "Programmata")
    
    def update_time_to_current(self, event=None):
        """Aggiorna il campo ora all'ora corrente + 1 ora quando viene cliccato"""
        current_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%H:%M")
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, current_time)
        # Aggiorna anche la data se necessario
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
    
    def set_alarm(self):
        """Imposta una nuova sveglia"""
        try:
            room = self.selected_room.get()
            date_str = self.date_entry.get()
            time_str = self.time_entry.get()
            language = self.selected_language.get()
            
            if not room or not date_str or not time_str:
                messagebox.showerror("Errore", "Compila tutti i campi obbligatori")
                return
            
            # Combina data e ora
            alarm_datetime = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            # Verifica che la data sia nel futuro
            if alarm_datetime <= datetime.datetime.now():
                messagebox.showerror("Errore", "La sveglia deve essere programmata nel futuro")
                return
            
            # Cerca messaggio audio "wake_up" nella lingua selezionata
            audio_id = None
            messages = self.db.get_audio_messages()
            for msg in messages:
                # msg = (id, name, file_path, duration, category, language, action_type, created_at)
                msg_language = msg[5] if len(msg) > 5 else 'it'
                msg_action = msg[6] if len(msg) > 6 else None
                
                if msg_language.lower() == language.lower() and msg_action == 'wake_up':
                    audio_id = msg[0]
                    self.logger.info(f"Audio wake_up trovato: {msg[1]} (ID: {audio_id}, Lingua: {language})")
                    break
            
            if not audio_id:
                messagebox.showwarning("Attenzione", 
                                     f"Nessun messaggio sveglia trovato per la lingua '{language.upper()}'.\n"
                                     f"Sveglia creata senza audio.")
            
            # Aggiungi sveglia al database
            alarm_id = self.db.add_alarm(room, alarm_datetime.isoformat(), audio_id)
            
            lang_info = f" ({language.upper()})" if audio_id else " (senza audio)"
            messagebox.showinfo("Successo", f"Sveglia impostata per camera {room} alle {time_str}{lang_info}")
            self.load_alarms()
            self.status_var.set(f"Sveglia aggiunta: Camera {room} - {alarm_datetime.strftime('%d/%m/%Y %H:%M')}")
            
        except ValueError as e:
            messagebox.showerror("Errore", f"Formato data/ora non valido: {e}")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'impostazione della sveglia: {e}")
    
    def test_audio(self):
        """Testa la riproduzione del messaggio audio nella lingua selezionata"""
        language = self.selected_language.get()
        
        # Cerca messaggio audio "wake_up" nella lingua selezionata
        messages = self.db.get_audio_messages()
        audio = None
        for msg in messages:
            msg_language = msg[5] if len(msg) > 5 else 'it'
            msg_action = msg[6] if len(msg) > 6 else None
            
            if msg_language.lower() == language.lower() and msg_action == 'wake_up':
                audio = msg
                break
        
        if not audio:
            messagebox.showerror("Errore", 
                               f"Nessun messaggio sveglia trovato per la lingua '{language.upper()}'.\n\n"
                               f"Carica un file audio con:\n"
                               f"- Tipo Azione: Messaggio Sveglia\n"
                               f"- Lingua: {language.upper()}")
            return
        
        audio_name = audio[1]
        audio_path = audio[2]  # file_path
        
        if not os.path.exists(audio_path):
            messagebox.showerror("Errore", f"File audio non trovato:\n{audio_path}")
            return
        
        # Riproduce l'audio
        from audio_player import get_audio_player
        player = get_audio_player()
        
        success, msg = player.play(audio_path)
        
        if success:
            messagebox.showinfo("Riproduzione Audio", 
                              f"▶️ Riproduzione in corso:\n{audio_name}\n\n"
                              f"Lingua: {language.upper()}\n"
                              f"File: {os.path.basename(audio_path)}\n"
                              f"Volume: {int(player.get_volume() * 100)}%")
        else:
            messagebox.showerror("Errore Audio", f"Errore nella riproduzione:\n{msg}")
    
    def delete_selected_alarm(self):
        """Elimina la sveglia selezionata"""
        selection = self.alarms_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona una sveglia da eliminare")
            return
        
        item = self.alarms_tree.item(selection[0])
        alarm_id = item['values'][0]
        room = item['values'][1]
        date = item['values'][2]
        time = item['values'][3]
        
        if messagebox.askyesno("Conferma", f"Eliminare la sveglia per camera {room} del {date} alle {time}?"):
            try:
                # Aggiorna status a cancelled nel database
                self.db.update_alarm_status(alarm_id, "cancelled")
                messagebox.showinfo("Successo", "Sveglia eliminata correttamente")
                self.load_alarms()
                self.status_var.set(f"Sveglia eliminata: Camera {room}")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nell'eliminazione: {e}")
    
    def add_logo(self, parent, row, column):
        """Aggiunge il logo AL CODE STUDIO in basso a destra"""
        try:
            # Determina dimensione logo in base alla dimensione della finestra
            window_width = self.root.winfo_width()
            
            # Scegli dimensione logo appropriata
            if window_width < 800:
                logo_file = 'assets/logo_small.png'
            elif window_width < 1200:
                logo_file = 'assets/logo_medium.png'
            else:
                logo_file = 'assets/logo_large.png'
            
            # Carica logo
            if os.path.exists(logo_file):
                logo_img = Image.open(logo_file)
                logo_photo = ImageTk.PhotoImage(logo_img)
                
                # Crea label per logo
                logo_label = ttk.Label(parent, image=logo_photo)
                logo_label.image = logo_photo  # Mantieni riferimento
                logo_label.grid(row=row, column=column, sticky=tk.SE, pady=(10, 0), padx=(0, 10))
            
        except Exception as e:
            self.logger.warning(f"Impossibile caricare logo: {e}")

def main():
    """Funzione principale"""
    root = tk.Tk()
    app = SvegliaCentralinoApp(root)
    
    # Gestisce la chiusura dell'applicazione
    def on_closing():
        """Chiusura pulita dell'applicazione"""
        try:
            # Log chiusura
            app.logger.info("Chiusura applicazione in corso...")
            
            # Chiudi audio player PRIMA (più veloce)
            try:
                from audio_player import get_audio_player
                player = get_audio_player()
                player.cleanup()
            except Exception as e:
                app.logger.warning(f"Errore cleanup audio: {e}")
            
            # Ferma il gestore sveglie
            try:
                app.alarm_manager.stop()
            except Exception as e:
                app.logger.warning(f"Errore stop alarm manager: {e}")
            
            # Chiudi finestra immediatamente
            app.logger.info("Applicazione chiusa")
            root.quit()  # quit() invece di destroy() per uscita più veloce
            
        except Exception as e:
            print(f"Errore durante chiusura: {e}")
            root.quit()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
