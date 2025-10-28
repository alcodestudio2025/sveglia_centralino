"""
Gestione dei messaggi audio
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from database import DatabaseManager
from config import AUDIO_CONFIG

class AudioManagerWindow:
    def __init__(self, parent, db_manager, on_save_callback=None):
        self.parent = parent
        self.db = db_manager
        self.on_save_callback = on_save_callback
        
        # Inizializza logger
        from logger import get_logger
        self.logger = get_logger('audio_manager')
        self.logger.info("Apertura finestra Gestione Messaggi Audio")
        
        # Crea la finestra
        self.window = tk.Toplevel(parent)
        self.window.title("Gestione Messaggi Audio")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Centra la finestra
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variabili per i controlli
        self.selected_audio_id = None
        self.audio_name_var = tk.StringVar()
        self.audio_category_var = tk.StringVar(value="standard")
        self.audio_language_var = tk.StringVar(value="it")
        self.audio_action_var = tk.StringVar(value="Messaggio Sveglia")
        
        # Mappatura azioni
        self.action_map = {
            "Messaggio Sveglia": "wake_up",
            "Conferma Riprogrammazione": "snooze_confirm",
            "Saluto": "goodbye"
        }
        self.action_map_reverse = {v: k for k, v in self.action_map.items()}
        
        # Crea l'interfaccia
        self.create_widgets()
        self.load_audio_messages()
    
    def create_widgets(self):
        """Crea l'interfaccia della finestra"""
        # Frame principale
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titolo
        title_label = ttk.Label(main_frame, text="Gestione Messaggi Audio", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame per caricamento file
        self.create_upload_section(main_frame)
        
        # Frame per lista messaggi
        self.create_audio_list_section(main_frame)
        
        # Pulsanti di controllo
        self.create_control_buttons(main_frame)
    
    def create_upload_section(self, parent):
        """Crea la sezione per il caricamento dei file audio"""
        upload_frame = ttk.LabelFrame(parent, text="Carica Nuovo Messaggio Audio", padding="15")
        upload_frame.pack(fill=tk.X, pady=(0, 15))
        upload_frame.columnconfigure(1, weight=1)
        
        # Nome messaggio
        ttk.Label(upload_frame, text="Nome Messaggio:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(upload_frame, textvariable=self.audio_name_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20), pady=5)
        
        # Categoria
        ttk.Label(upload_frame, text="Categoria:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10), pady=5)
        category_combo = ttk.Combobox(upload_frame, textvariable=self.audio_category_var, 
                                     values=["standard", "emergency", "promotional", "custom"], 
                                     state="readonly", width=15)
        category_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=5)
        
        # Lingua
        ttk.Label(upload_frame, text="Lingua:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        language_combo = ttk.Combobox(upload_frame, textvariable=self.audio_language_var, 
                                     values=["it", "en", "fr", "de", "es", "pt", "ru", "zh", "ja", "ar"], 
                                     state="readonly", width=15)
        language_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 20), pady=5)
        
        # Tipo di azione
        ttk.Label(upload_frame, text="Tipo Azione:").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=5)
        action_combo = ttk.Combobox(upload_frame, textvariable=self.audio_action_var, 
                                   values=list(self.action_map.keys()), 
                                   state="readonly", width=20)
        action_combo.grid(row=1, column=3, sticky=(tk.W, tk.E), pady=5)
        
        # Pulsante caricamento
        ttk.Button(upload_frame, text="Seleziona File Audio", 
                  command=self.load_audio_file).grid(row=2, column=0, columnspan=4, pady=10)
        
        # Info formati supportati
        info_text = f"Formati supportati: {', '.join(AUDIO_CONFIG['supported_formats'])}"
        ttk.Label(upload_frame, text=info_text, font=("Arial", 9), foreground="gray").grid(row=3, column=0, columnspan=4, pady=5)
    
    def create_audio_list_section(self, parent):
        """Crea la sezione per la lista dei messaggi audio"""
        list_frame = ttk.LabelFrame(parent, text="Messaggi Audio Disponibili", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview per i messaggi audio
        columns = ("ID", "Nome", "File", "Durata", "Categoria", "Lingua", "Azione", "Creata")
        self.audio_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # Configurazione colonne
        column_widths = {"ID": 40, "Nome": 130, "File": 150, "Durata": 60, "Categoria": 80, "Lingua": 50, "Azione": 150, "Creata": 100}
        
        for col in columns:
            self.audio_tree.heading(col, text=col)
            self.audio_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.audio_tree.yview)
        self.audio_tree.configure(yscrollcommand=scrollbar.set)
        
        self.audio_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind per selezione
        self.audio_tree.bind("<<TreeviewSelect>>", self.on_audio_select)
        self.audio_tree.bind("<Double-1>", self.on_audio_double_click)
    
    def create_control_buttons(self, parent):
        """Crea i pulsanti di controllo"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X)
        
        # Pulsanti operazioni
        ttk.Button(buttons_frame, text="Riproduci Selezionato", 
                  command=self.play_selected_audio).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Elimina Selezionato", 
                  command=self.delete_selected_audio).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Pulisci Campi", 
                  command=self.clear_fields).pack(side=tk.LEFT, padx=(0, 10))
        
        # Pulsanti di chiusura
        ttk.Button(buttons_frame, text="Chiudi", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
        ttk.Button(buttons_frame, text="Aggiorna Lista", 
                  command=self.load_audio_messages).pack(side=tk.RIGHT, padx=(0, 10))
    
    def load_audio_file(self):
        """Carica un nuovo file audio"""
        # Verifica che il nome sia stato inserito
        audio_name = self.audio_name_var.get().strip()
        if not audio_name:
            messagebox.showerror("Errore", "Inserisci un nome per il messaggio audio")
            return
        
        # Apre il dialog per selezionare il file
        file_path = filedialog.askopenfilename(
            title="Seleziona File Audio",
            filetypes=[
                ("File Audio", "*.mp3 *.wav *.ogg"),
                ("MP3", "*.mp3"),
                ("WAV", "*.wav"),
                ("OGG", "*.ogg"),
                ("Tutti i file", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Verifica l'estensione del file
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in AUDIO_CONFIG['supported_formats']:
                    messagebox.showerror("Errore", f"Formato file non supportato: {file_ext}")
                    return
                
                # Crea la cartella audio se non esiste
                audio_folder = AUDIO_CONFIG['audio_folder']
                if not os.path.exists(audio_folder):
                    os.makedirs(audio_folder)
                
                # Copia il file nella cartella audio
                filename = os.path.basename(file_path)
                dest_path = os.path.join(audio_folder, filename)
                
                # Se il file esiste già, aggiunge un numero
                counter = 1
                original_dest = dest_path
                while os.path.exists(dest_path):
                    name, ext = os.path.splitext(original_dest)
                    dest_path = f"{name}_{counter}{ext}"
                    counter += 1
                
                shutil.copy2(file_path, dest_path)
                
                # Calcola la durata del file (semplificato)
                duration = self.get_audio_duration(dest_path)
                
                # Aggiunge al database
                action_type = self.action_map.get(self.audio_action_var.get(), "wake_up")
                audio_id = self.db.add_audio_message(
                    name=audio_name,
                    file_path=dest_path,
                    duration=duration,
                    category=self.audio_category_var.get(),
                    language=self.audio_language_var.get(),
                    action_type=action_type
                )
                
                messagebox.showinfo("Successo", f"Messaggio audio '{audio_name}' caricato con successo")
                self.clear_fields()
                self.load_audio_messages()
                
                # Notifica l'applicazione principale
                if self.on_save_callback:
                    self.on_save_callback()
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel caricamento del file: {e}")
    
    def get_audio_duration(self, file_path):
        """Calcola la durata del file audio usando pygame"""
        try:
            import pygame.mixer
            
            # Inizializza mixer se necessario
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            # Carica il file audio
            sound = pygame.mixer.Sound(file_path)
            
            # Ottieni la durata in secondi
            duration_seconds = sound.get_length()
            
            # Formatta in mm:ss
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            
            return f"{minutes:02d}:{seconds:02d}"
            
        except Exception as e:
            self.logger.warning(f"Impossibile calcolare durata per {file_path}: {e}")
            return "N/A"
    
    def load_audio_messages(self):
        """Carica la lista dei messaggi audio"""
        # Pulisce la lista
        for item in self.audio_tree.get_children():
            self.audio_tree.delete(item)
        
        try:
            messages = self.db.get_audio_messages()
            for msg in messages:
                # Formatta la durata
                duration = f"{msg[3]:.1f}s" if msg[3] else "N/A"
                
                # Ottiene la lingua e l'azione
                language = msg[5] if len(msg) > 5 else "it"
                action_type = msg[6] if len(msg) > 6 else "wake_up"
                action_display = self.action_map_reverse.get(action_type, "Messaggio Sveglia")
                
                # Formatta la data di creazione
                created_date = msg[7].split(' ')[0] if len(msg) > 7 and msg[7] else "N/A"
                
                # Inserisci nella lista
                item_id = self.audio_tree.insert("", "end", values=(
                    msg[0],  # ID
                    msg[1],  # Nome
                    os.path.basename(msg[2]),  # File (solo nome)
                    duration,  # Durata
                    msg[4] if len(msg) > 4 else "standard",  # Categoria
                    language.upper(),  # Lingua
                    action_display,  # Tipo Azione
                    created_date  # Data creazione
                ))
        
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel caricamento dei messaggi audio: {e}")
    
    def on_audio_select(self, event):
        """Gestisce la selezione di un messaggio audio"""
        selected_item = self.audio_tree.focus()
        if selected_item:
            values = self.audio_tree.item(selected_item, 'values')
            self.selected_audio_id = values[0]
            self.audio_name_var.set(values[1])
            self.audio_category_var.set(values[4])
        else:
            self.clear_fields()
    
    def on_audio_double_click(self, event):
        """Gestisce il doppio click su un messaggio audio"""
        self.play_selected_audio()
    
    def play_selected_audio(self):
        """Riproduce il messaggio audio selezionato"""
        if not self.selected_audio_id:
            messagebox.showwarning("Attenzione", "Seleziona un messaggio audio da riprodurre")
            return
        
        selected_item = self.audio_tree.focus()
        if not selected_item:
            return
        
        values = self.audio_tree.item(selected_item, 'values')
        audio_name = values[1]
        audio_file = values[2]
        
        # Costruisce il percorso completo
        audio_path = os.path.join(AUDIO_CONFIG['audio_folder'], audio_file)
        
        if not os.path.exists(audio_path):
            messagebox.showerror("Errore", f"File audio non trovato:\n{audio_path}")
            return
        
        # Riproduce l'audio
        from audio_player import get_audio_player
        player = get_audio_player()
        
        success, message = player.play(audio_path)
        
        if success:
            # Mostra informazioni durante la riproduzione
            duration = values[3]
            category = values[4]
            language = values[5]
            action = values[6]
            
            messagebox.showinfo("Riproduzione Audio", 
                              f"▶️ Riproduzione in corso:\n\n"
                              f"Nome: {audio_name}\n"
                              f"Durata: {duration}\n"
                              f"Categoria: {category}\n"
                              f"Lingua: {language}\n"
                              f"Azione: {action}\n\n"
                              f"Volume: {int(player.get_volume() * 100)}%")
            
            self.logger.info(f"Riproduzione audio: {audio_name}")
        else:
            messagebox.showerror("Errore Audio", f"Errore nella riproduzione:\n{message}")
            self.logger.error(f"Errore riproduzione audio: {message}")
    
    def delete_selected_audio(self):
        """Elimina il messaggio audio selezionato"""
        if not self.selected_audio_id:
            messagebox.showwarning("Attenzione", "Seleziona un messaggio audio da eliminare")
            return
        
        selected_item = self.audio_tree.focus()
        if selected_item:
            values = self.audio_tree.item(selected_item, 'values')
            audio_name = values[1]
            
            if messagebox.askyesno("Conferma Eliminazione", 
                                  f"Sei sicuro di voler eliminare il messaggio '{audio_name}'?\n\n"
                                  f"Questa operazione non può essere annullata."):
                try:
                    # Ottieni il percorso del file
                    messages = self.db.get_audio_messages()
                    file_path = None
                    for msg in messages:
                        if msg[0] == int(self.selected_audio_id):
                            file_path = msg[2]
                            break
                    
                    # Elimina dal database
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM audio_messages WHERE id = ?", (self.selected_audio_id,))
                    conn.commit()
                    conn.close()
                    
                    # Elimina il file fisico
                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)
                    
                    messagebox.showinfo("Successo", f"Messaggio '{audio_name}' eliminato con successo")
                    self.clear_fields()
                    self.load_audio_messages()
                    
                    # Notifica l'applicazione principale
                    if self.on_save_callback:
                        self.on_save_callback()
                    
                except Exception as e:
                    messagebox.showerror("Errore", f"Errore nell'eliminazione del messaggio: {e}")
    
    def clear_fields(self):
        """Pulisce i campi di input"""
        self.selected_audio_id = None
        self.audio_name_var.set("")
        self.audio_category_var.set("standard")

if __name__ == "__main__":
    # Test del modulo
    root = tk.Tk()
    root.withdraw()
    db = DatabaseManager()
    AudioManagerWindow(root, db)
    root.mainloop()
