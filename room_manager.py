"""
Gestione avanzata delle camere dell'hotel con integrazione centralino PBX
"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from database import DatabaseManager
from pbx_connection import PBXConnection
import threading
import logging

class RoomManagerWindow:
    def __init__(self, parent, db_manager, pbx_manager=None, on_save_callback=None):
        self.parent = parent
        self.db = db_manager
        self.pbx_manager = pbx_manager
        self.on_save_callback = on_save_callback
        self.logger = logging.getLogger(__name__)
        
        # Crea la finestra
        self.window = tk.Toplevel(parent)
        self.window.title("Gestione Camere Hotel - Integrazione PBX")
        self.window.geometry("1200x700")
        self.window.resizable(True, True)
        
        # Centra la finestra
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variabili per i controlli
        self.selected_room_id = None
        self.room_number_var = tk.StringVar()
        self.phone_extension_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.room_status_var = tk.StringVar(value="available")
        self.room_color_var = tk.StringVar(value="#FFFFFF")
        self.room_label_var = tk.StringVar()
        
        # Cache interni PBX
        self.pbx_extensions = []
        self.pbx_status_cache = {}
        
        # Crea l'interfaccia
        self.create_widgets()
        self.load_rooms()
        
        # Avvia refresh automatico stato interni
        self.start_auto_refresh()
    
    def create_widgets(self):
        """Crea l'interfaccia della finestra"""
        # Frame principale
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titolo e toolbar
        self.create_header(main_frame)
        
        # Frame per input camere
        self.create_input_section(main_frame)
        
        # Frame per lista camere
        self.create_rooms_list_section(main_frame)
        
        # Pulsanti di controllo
        self.create_control_buttons(main_frame)
    
    def create_header(self, parent):
        """Crea l'header con titolo e toolbar"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Titolo
        title_label = ttk.Label(header_frame, text="Gestione Camere Hotel - Integrazione PBX", 
                               font=("Arial", 14, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Toolbar destra
        toolbar_frame = ttk.Frame(header_frame)
        toolbar_frame.pack(side=tk.RIGHT)
        
        # Pulsante importa da PBX
        ttk.Button(toolbar_frame, text="📥 Importa da PBX", 
                  command=self.import_from_pbx).pack(side=tk.LEFT, padx=(0, 10))
        
        # Pulsante PULISCI e reimporta
        ttk.Button(toolbar_frame, text="🗑️ Pulisci e Reimporta", 
                  command=self.clean_and_reimport_pbx, 
                  style='Danger.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        # Pulsante refresh stato
        ttk.Button(toolbar_frame, text="🔄 Aggiorna Stato", 
                  command=self.refresh_extensions_status).pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(toolbar_frame, text="", font=("Arial", 9), foreground="gray")
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def create_input_section(self, parent):
        """Crea la sezione per l'input delle camere"""
        input_frame = ttk.LabelFrame(parent, text="Dettagli Camera", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 15))
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
        # RIGA 1: Numero camera e Interno telefonico
        ttk.Label(input_frame, text="Numero Camera:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(input_frame, textvariable=self.room_number_var, width=20).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20), pady=5)
        
        ttk.Label(input_frame, text="Interno Telefonico:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10), pady=5)
        extension_entry = ttk.Entry(input_frame, textvariable=self.phone_extension_var, width=15)
        extension_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=5)
        
        # RIGA 2: Descrizione (nome camera/ospite)
        ttk.Label(input_frame, text="Descrizione:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(input_frame, textvariable=self.description_var, width=50).grid(row=1, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # RIGA 3: Status e Colore
        ttk.Label(input_frame, text="Stato:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        status_combo = ttk.Combobox(input_frame, textvariable=self.room_status_var, 
                                   values=["available", "occupied", "maintenance", "cleaning"], 
                                   state="readonly", width=15)
        status_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 20), pady=5)
        
        ttk.Label(input_frame, text="Colore:").grid(row=2, column=2, sticky=tk.W, padx=(0, 10), pady=5)
        color_frame = ttk.Frame(input_frame)
        color_frame.grid(row=2, column=3, sticky=(tk.W, tk.E), pady=5)
        
        self.color_display = tk.Canvas(color_frame, width=30, height=25, bd=2, relief=tk.SUNKEN, 
                                      bg=self.room_color_var.get())
        self.color_display.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(color_frame, text="Scegli Colore", 
                  command=self.choose_color).pack(side=tk.LEFT)
        
        # RIGA 4: Etichetta
        ttk.Label(input_frame, text="Etichetta:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(input_frame, textvariable=self.room_label_var, width=30).grid(row=3, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5)
    
    def create_rooms_list_section(self, parent):
        """Crea la sezione per la lista delle camere"""
        list_frame = ttk.LabelFrame(parent, text="Lista Camere", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview per le camere
        columns = ("Stato PBX", "ID", "Numero", "Interno", "Descrizione", "Stato", "Colore", "Etichetta", "Creata")
        self.rooms_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configurazione colonne
        column_widths = {
            "Stato PBX": 80,
            "ID": 50,
            "Numero": 80,
            "Interno": 80,
            "Descrizione": 200,
            "Stato": 100,
            "Colore": 80,
            "Etichetta": 150,
            "Creata": 100
        }
        
        for col in columns:
            self.rooms_tree.heading(col, text=col)
            self.rooms_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.rooms_tree.yview)
        self.rooms_tree.configure(yscrollcommand=scrollbar.set)
        
        self.rooms_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind per selezione
        self.rooms_tree.bind("<<TreeviewSelect>>", self.on_room_select)
        self.rooms_tree.bind("<Double-1>", self.on_room_double_click)
    
    def create_control_buttons(self, parent):
        """Crea i pulsanti di controllo"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X)
        
        # Pulsanti operazioni
        ttk.Button(buttons_frame, text="➕ Aggiungi Camera", 
                  command=self.add_room).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="✏️ Modifica Camera", 
                  command=self.edit_room).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="🗑️ Elimina Camera", 
                  command=self.delete_room).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="🧹 Pulisci Campi", 
                  command=self.clear_fields).pack(side=tk.LEFT, padx=(0, 10))
        
        # Pulsanti di chiusura
        ttk.Button(buttons_frame, text="Chiudi", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
        ttk.Button(buttons_frame, text="Aggiorna Lista", 
                  command=self.load_rooms).pack(side=tk.RIGHT, padx=(0, 10))
    
    def choose_color(self):
        """Apre il selettore di colori"""
        color_code = colorchooser.askcolor(
            title="Scegli Colore Camera", 
            initialcolor=self.room_color_var.get()
        )
        if color_code[1]:
            self.room_color_var.set(color_code[1])
            self.color_display.config(bg=color_code[1])
    
    def clean_and_reimport_pbx(self):
        """Pulisce tutte le camere e reimporta dal PBX"""
        # Conferma azione
        result = messagebox.askyesno(
            "Conferma Pulizia",
            "⚠️ ATTENZIONE ⚠️\n\n"
            "Questa operazione:\n"
            "• Eliminerà TUTTE le camere esistenti\n"
            "• Reimporterà tutti gli interni dal PBX\n\n"
            "Vuoi continuare?",
            icon='warning'
        )
        
        if not result:
            return
        
        def do_clean_import():
            try:
                self.status_label.config(text="Pulizia in corso...")
                self.logger.info("Pulizia database camere...")
                
                # Elimina tutte le camere
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM rooms")
                conn.commit()
                conn.close()
                
                self.logger.info("Tutte le camere eliminate")
                self.status_label.config(text="Import da PBX in corso...")
                
                # Connessione al PBX
                pbx = PBXConnection()
                
                # Ottiene la lista degli interni
                peers, error = pbx.get_sip_peers()
                
                if error or not peers:
                    messagebox.showerror("Errore Import", 
                                       f"Impossibile importare interni dal PBX:\n{error or 'Nessun interno trovato'}")
                    self.status_label.config(text="")
                    return
                
                self.logger.info(f"Trovati {len(peers)} interni sul PBX")
                
                # Importa tutti gli interni
                imported = 0
                
                for peer in peers:
                    extension = peer['extension']
                    ext_type = peer['type']
                    
                    # Crea nuova camera
                    description = f"Interno {extension} ({ext_type})"
                    self.db.add_room(
                        room_number=extension,
                        phone_extension=extension,
                        description=description,
                        status='available',
                        color='#FFFFFF',
                        label='Importato da PBX'
                    )
                    imported += 1
                    
                    if imported % 20 == 0:
                        self.logger.info(f"Importati {imported}/{len(peers)}...")
                
                self.logger.info(f"Import completato: {imported} interni importati")
                
                # Aggiorna stato e lista
                self.refresh_extensions_status()
                
                # Messaggio risultato
                messagebox.showinfo("Pulizia e Import Completati", 
                                  f"✅ Operazione completata!\n\n"
                                  f"Camere vecchie: Eliminate\n"
                                  f"Interni importati: {imported}\n"
                                  f"Totale interni PBX: {len(peers)}")
                
                self.status_label.config(text=f"✓ {imported} interni importati e aggiornati")
                
            except Exception as e:
                self.logger.error(f"Errore nella pulizia/import: {e}")
                messagebox.showerror("Errore", f"Errore:\n{e}")
                self.status_label.config(text="")
        
        # Esegue in thread separato
        threading.Thread(target=do_clean_import, daemon=True).start()
    
    def import_from_pbx(self):
        """Importa gli interni configurati dal centralino PBX"""
        def do_import():
            try:
                self.status_label.config(text="Importazione in corso...")
                self.logger.info("Avvio importazione interni da PBX...")
                
                # Connessione al PBX
                pbx = PBXConnection()
                
                # Ottiene la lista degli interni
                peers, error = pbx.get_sip_peers()
                
                if error or not peers:
                    messagebox.showerror("Errore Import", 
                                       f"Impossibile importare interni dal PBX:\n{error or 'Nessun interno trovato'}")
                    self.status_label.config(text="")
                    return
                
                self.logger.info(f"Trovati {len(peers)} interni sul PBX")
                
                # Importa gli interni
                imported = 0
                skipped = 0
                
                for peer in peers:
                    extension = peer['extension']
                    status = peer['status']
                    ext_type = peer['type']
                    
                    # Verifica se l'interno esiste già
                    existing = self.db.get_room_by_extension(extension)
                    
                    if not existing:
                        # Crea nuova camera
                        description = f"Interno {extension} ({ext_type})"
                        self.db.add_room(
                            room_number=extension,
                            phone_extension=extension,
                            description=description,
                            status='available',
                            color='#FFFFFF',
                            label=f'Importato da PBX'
                        )
                        imported += 1
                        self.logger.info(f"Importato interno {extension}")
                    else:
                        skipped += 1
                
                # Aggiorna lista
                self.load_rooms()
                
                # Messaggio risultato
                messagebox.showinfo("Import Completato", 
                                  f"Import completato!\n\n"
                                  f"Interni importati: {imported}\n"
                                  f"Interni già esistenti: {skipped}\n"
                                  f"Totale interni PBX: {len(peers)}")
                
                self.status_label.config(text=f"✓ Importati {imported} interni")
                self.logger.info(f"Import completato: {imported} importati, {skipped} saltati")
                
            except Exception as e:
                self.logger.error(f"Errore nell'import da PBX: {e}")
                messagebox.showerror("Errore", f"Errore nell'import:\n{e}")
                self.status_label.config(text="")
        
        # Esegue in thread separato
        threading.Thread(target=do_import, daemon=True).start()
    
    def refresh_extensions_status(self):
        """Aggiorna lo stato di tutti gli interni dal PBX"""
        def do_refresh():
            try:
                self.status_label.config(text="Aggiornamento stato interni...")
                self.logger.info("Refresh stato interni PBX...")
                
                pbx = PBXConnection()
                peers, error = pbx.get_sip_peers()
                
                if error or not peers:
                    self.status_label.config(text="✗ Errore aggiornamento")
                    return
                
                # Aggiorna cache stato
                self.pbx_status_cache = {}
                online_count = 0
                offline_count = 0
                
                for peer in peers:
                    self.pbx_status_cache[peer['extension']] = {
                        'status': peer['status'],
                        'latency': peer['latency'],
                        'type': peer['type']
                    }
                    if peer['status'] == 'online':
                        online_count += 1
                    elif peer['status'] == 'offline':
                        offline_count += 1
                
                self.logger.info(f"Cache popolata con {len(peers)} interni: {online_count} online, {offline_count} offline")
                
                # Log primi 3 interni per debug
                sample_keys = list(self.pbx_status_cache.keys())[:3]
                for ext in sample_keys:
                    self.logger.info(f"  Cache[{ext}] = {self.pbx_status_cache[ext]}")
                
                # Ricarica la lista per aggiornare i colori
                self.load_rooms()
                
                self.status_label.config(text=f"✓ Aggiornati {len(peers)} interni")
                
            except Exception as e:
                self.logger.error(f"Errore nel refresh stato: {e}")
                self.status_label.config(text="✗ Errore aggiornamento")
        
        threading.Thread(target=do_refresh, daemon=True).start()
    
    def start_auto_refresh(self):
        """Avvia il refresh automatico dello stato interni ogni 30 secondi"""
        def auto_refresh_loop():
            # Primo refresh dopo 2 secondi
            self.window.after(2000, self.refresh_extensions_status)
            
            # Poi ogni 30 secondi
            def schedule_next():
                if self.window.winfo_exists():
                    self.refresh_extensions_status()
                    self.window.after(30000, schedule_next)
            
            self.window.after(30000, schedule_next)
        
        auto_refresh_loop()
    
    def load_rooms(self):
        """Carica la lista delle camere con stato PBX"""
        # Pulisce la lista
        for item in self.rooms_tree.get_children():
            self.rooms_tree.delete(item)
        
        # Configura i tag PRIMA del loop (una sola volta)
        self.rooms_tree.tag_configure('pbx_green', foreground='green')
        self.rooms_tree.tag_configure('pbx_red', foreground='red')
        self.rooms_tree.tag_configure('pbx_orange', foreground='orange')
        self.rooms_tree.tag_configure('pbx_gray', foreground='gray')
        
        try:
            # Log cache status
            self.logger.info(f"Caricamento camere... Cache PBX: {len(self.pbx_status_cache)} interni")
            if len(self.pbx_status_cache) > 0:
                # Log primi 3 interni in cache
                sample = list(self.pbx_status_cache.items())[:3]
                self.logger.info(f"  Campione cache: {sample}")
            
            rooms = self.db.get_rooms()
            for room in rooms:
                # Estrae i dati (ordine corretto dal database)
                # 0=id, 1=room_number, 2=phone_extension, 3=description, 
                # 4=status, 5=color, 6=label, 7=created_at
                room_id = room[0]
                room_number = room[1]
                phone_extension = room[2] if len(room) > 2 and room[2] else ""
                description = room[3] if len(room) > 3 and room[3] else ""
                status = room[4] if len(room) > 4 and room[4] else "available"
                color = room[5] if len(room) > 5 and room[5] else "#FFFFFF"
                label = room[6] if len(room) > 6 and room[6] else ""
                created_date = room[7].split(' ')[0] if len(room) > 7 and room[7] else "N/A"
                
                # Determina stato PBX
                pbx_status_display = "?"
                pbx_color = "gray"
                
                if phone_extension and phone_extension in self.pbx_status_cache:
                    ext_status = self.pbx_status_cache[phone_extension]['status']
                    if ext_status == 'online':
                        pbx_status_display = "✓ Online"
                        pbx_color = "green"
                    elif ext_status == 'offline':
                        pbx_status_display = "✗ Offline"
                        pbx_color = "red"
                    elif ext_status == 'unmonitored':
                        pbx_status_display = "○ Non monitorato"
                        pbx_color = "orange"
                    
                    # Log solo primo match per vedere se funziona
                    if room_id == rooms[0][0]:
                        self.logger.info(f"  ✓ Primo interno: {phone_extension} -> {ext_status}")
                elif phone_extension:
                    # Log solo primo mismatch
                    if room_id == rooms[0][0]:
                        self.logger.warning(f"  ✗ Interno {phone_extension} NON trovato in cache!")
                
                # Converte stato in italiano
                status_it = {
                    "available": "Disponibile",
                    "occupied": "Occupata",
                    "maintenance": "Manutenzione",
                    "cleaning": "Pulizia"
                }.get(status, status)
                
                # Inserisci nella lista
                item_id = self.rooms_tree.insert("", "end", values=(
                    pbx_status_display,  # Stato PBX
                    room_id,             # ID
                    room_number,         # Numero
                    phone_extension,     # Interno
                    description,         # Descrizione
                    status_it,           # Stato
                    color,               # Colore
                    label,               # Etichetta
                    created_date         # Data creazione
                ))
                
                # Colora la riga in base allo stato PBX (usa tag già configurato)
                self.rooms_tree.item(item_id, tags=(f'pbx_{pbx_color}',))
        
        except Exception as e:
            self.logger.error(f"Errore nel caricamento camere: {e}")
            messagebox.showerror("Errore", f"Errore nel caricamento delle camere: {e}")
    
    def on_room_select(self, event):
        """Gestisce la selezione di una camera"""
        selected_item = self.rooms_tree.focus()
        if selected_item:
            values = self.rooms_tree.item(selected_item, 'values')
            self.selected_room_id = values[1]  # ID è nella colonna 1
            self.room_number_var.set(values[2])
            self.phone_extension_var.set(values[3])
            self.description_var.set(values[4])
            
            # Converte lo status visualizzato in quello del database
            status_display = values[5]
            status_map = {
                "Disponibile": "available",
                "Occupata": "occupied",
                "Manutenzione": "maintenance",
                "Pulizia": "cleaning"
            }
            self.room_status_var.set(status_map.get(status_display, "available"))
            
            # Color con fallback
            color = values[6] if values[6] else "#FFFFFF"
            self.room_color_var.set(color)
            self.color_display.config(bg=color)
            self.room_label_var.set(values[7])
        else:
            self.clear_fields()
    
    def on_room_double_click(self, event):
        """Gestisce il doppio click su una camera"""
        self.edit_room()
    
    def add_room(self):
        """Aggiunge una nuova camera"""
        room_number = self.room_number_var.get().strip()
        phone_extension = self.phone_extension_var.get().strip()
        description = self.description_var.get().strip()
        status = self.room_status_var.get()
        color = self.room_color_var.get()
        label = self.room_label_var.get().strip()
        
        if not room_number:
            messagebox.showerror("Errore", "Il numero della camera è obbligatorio")
            return
        
        # Se non è specificato un interno, usa il numero camera
        if not phone_extension:
            phone_extension = room_number
        
        try:
            # Verifica se la camera esiste già
            existing_room = self.db.get_room(room_number)
            if existing_room:
                messagebox.showerror("Errore", f"La camera {room_number} esiste già")
                return
            
            # Aggiunge la camera
            room_id = self.db.add_room(room_number, phone_extension, description, status, color, label)
            messagebox.showinfo("Successo", 
                              f"Camera {room_number} aggiunta con successo\n"
                              f"Interno: {phone_extension}\n"
                              f"Descrizione: {description or 'N/A'}")
            self.clear_fields()
            self.load_rooms()
            
            # Notifica l'applicazione principale
            if self.on_save_callback:
                self.on_save_callback()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'aggiunta della camera: {e}")
    
    def edit_room(self):
        """Modifica una camera esistente"""
        if not self.selected_room_id:
            messagebox.showwarning("Attenzione", "Seleziona una camera da modificare")
            return
        
        room_number = self.room_number_var.get().strip()
        phone_extension = self.phone_extension_var.get().strip()
        description = self.description_var.get().strip()
        status = self.room_status_var.get()
        color = self.room_color_var.get()
        label = self.room_label_var.get().strip()
        
        if not room_number:
            messagebox.showerror("Errore", "Il numero della camera è obbligatorio")
            return
        
        if not phone_extension:
            phone_extension = room_number
        
        try:
            self.db.update_room(self.selected_room_id, room_number, phone_extension, description, status, color, label)
            messagebox.showinfo("Successo", f"Camera {room_number} modificata con successo")
            self.clear_fields()
            self.load_rooms()
            
            if self.on_save_callback:
                self.on_save_callback()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella modifica della camera: {e}")
    
    def delete_room(self):
        """Elimina una camera"""
        if not self.selected_room_id:
            messagebox.showwarning("Attenzione", "Seleziona una camera da eliminare")
            return
        
        room_number = self.room_number_var.get()
        
        if messagebox.askyesno("Conferma", f"Eliminare la camera {room_number}?"):
            try:
                self.db.delete_room(self.selected_room_id)
                messagebox.showinfo("Successo", f"Camera {room_number} eliminata")
                self.clear_fields()
                self.load_rooms()
                
                if self.on_save_callback:
                    self.on_save_callback()
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nell'eliminazione della camera: {e}")
    
    def clear_fields(self):
        """Pulisce i campi del form"""
        self.selected_room_id = None
        self.room_number_var.set("")
        self.phone_extension_var.set("")
        self.description_var.set("")
        self.room_status_var.set("available")
        self.room_color_var.set("#FFFFFF")
        self.color_display.config(bg="#FFFFFF")
        self.room_label_var.set("")

