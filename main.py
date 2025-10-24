"""
Sistema di Gestione Sveglie per Hotel
Applicazione principale con interfaccia grafica
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import threading
import os
from config import create_directories, PBX_CONFIG, AUDIO_CONFIG
from database import DatabaseManager

class SvegliaCentralinoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Gestione Sveglie Hotel")
        self.root.geometry("1000x700")
        
        # Inizializza database
        self.db = DatabaseManager()
        
        # Crea cartelle necessarie
        create_directories()
        
        # Variabili per l'interfaccia
        self.selected_room = tk.StringVar()
        self.alarm_time = tk.StringVar()
        self.selected_audio = tk.StringVar()
        
        # Crea l'interfaccia
        self.create_widgets()
        
        # Carica dati iniziali
        self.load_rooms()
        self.load_audio_messages()
        self.load_alarms()
    
    def create_widgets(self):
        """Crea l'interfaccia grafica principale"""
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurazione griglia
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Titolo
        title_label = ttk.Label(main_frame, text="Sistema Gestione Sveglie Hotel", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sezione 1: Impostazione sveglia
        self.create_alarm_section(main_frame, row=1)
        
        # Sezione 2: Lista sveglie attive
        self.create_alarms_list_section(main_frame, row=2)
        
        # Sezione 3: Gestione messaggi audio
        self.create_audio_section(main_frame, row=3)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Sistema pronto")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(20, 0))
    
    def create_alarm_section(self, parent, row):
        """Crea la sezione per impostare nuove sveglie"""
        # Frame per impostazione sveglia
        alarm_frame = ttk.LabelFrame(parent, text="Imposta Nuova Sveglia", padding="10")
        alarm_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        alarm_frame.columnconfigure(1, weight=1)
        
        # Camera
        ttk.Label(alarm_frame, text="Camera:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.room_combo = ttk.Combobox(alarm_frame, textvariable=self.selected_room, 
                                      state="readonly", width=15)
        self.room_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Data e ora
        ttk.Label(alarm_frame, text="Data:").grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.date_entry = ttk.Entry(alarm_frame, width=12)
        self.date_entry.grid(row=0, column=3, padx=(0, 10))
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        
        ttk.Label(alarm_frame, text="Ora:").grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
        self.time_entry = ttk.Entry(alarm_frame, width=8)
        self.time_entry.grid(row=0, column=5, padx=(0, 10))
        self.time_entry.insert(0, "08:00")
        
        # Messaggio audio
        ttk.Label(alarm_frame, text="Messaggio:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.audio_combo = ttk.Combobox(alarm_frame, textvariable=self.selected_audio, 
                                       state="readonly", width=30)
        self.audio_combo.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), 
                             padx=(0, 10), pady=(10, 0))
        
        # Pulsanti
        ttk.Button(alarm_frame, text="Imposta Sveglia", 
                  command=self.set_alarm).grid(row=1, column=3, padx=(10, 0), pady=(10, 0))
        ttk.Button(alarm_frame, text="Test Audio", 
                  command=self.test_audio).grid(row=1, column=4, padx=(10, 0), pady=(10, 0))
    
    def create_alarms_list_section(self, parent, row):
        """Crea la sezione per visualizzare le sveglie attive"""
        # Frame per lista sveglie
        alarms_frame = ttk.LabelFrame(parent, text="Sveglie Attive", padding="10")
        alarms_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        alarms_frame.columnconfigure(0, weight=1)
        alarms_frame.rowconfigure(1, weight=1)
        
        # Pulsanti di controllo
        controls_frame = ttk.Frame(alarms_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(controls_frame, text="Aggiorna", 
                  command=self.load_alarms).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="Elimina Selezionata", 
                  command=self.delete_selected_alarm).pack(side=tk.LEFT, padx=(0, 10))
        
        # Lista sveglie
        columns = ("Camera", "Data", "Ora", "Messaggio", "Status")
        self.alarms_tree = ttk.Treeview(alarms_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.alarms_tree.heading(col, text=col)
            self.alarms_tree.column(col, width=120)
        
        # Scrollbar per la lista
        scrollbar = ttk.Scrollbar(alarms_frame, orient=tk.VERTICAL, command=self.alarms_tree.yview)
        self.alarms_tree.configure(yscrollcommand=scrollbar.set)
        
        self.alarms_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
    
    def create_audio_section(self, parent, row):
        """Crea la sezione per gestire i messaggi audio"""
        # Frame per messaggi audio
        audio_frame = ttk.LabelFrame(parent, text="Gestione Messaggi Audio", padding="10")
        audio_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        audio_frame.columnconfigure(1, weight=1)
        
        # Pulsanti per gestione audio
        ttk.Button(audio_frame, text="Carica File Audio", 
                  command=self.load_audio_file).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(audio_frame, text="Elimina Messaggio", 
                  command=self.delete_audio_message).grid(row=0, column=1, padx=(0, 10))
        
        # Lista messaggi audio
        audio_list_frame = ttk.Frame(audio_frame)
        audio_list_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        audio_list_frame.columnconfigure(0, weight=1)
        
        columns = ("Nome", "File", "Durata", "Categoria")
        self.audio_tree = ttk.Treeview(audio_list_frame, columns=columns, show="headings", height=4)
        
        for col in columns:
            self.audio_tree.heading(col, text=col)
            self.audio_tree.column(col, width=150)
        
        self.audio_tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
    
    def load_rooms(self):
        """Carica le camere disponibili"""
        rooms = self.db.get_rooms('available')
        room_numbers = [room[1] for room in rooms]
        self.room_combo['values'] = room_numbers
        if room_numbers:
            self.room_combo.set(room_numbers[0])
    
    def load_audio_messages(self):
        """Carica i messaggi audio"""
        messages = self.db.get_audio_messages()
        message_names = [msg[1] for msg in messages]
        self.audio_combo['values'] = message_names
        
        # Aggiorna anche la lista
        self.audio_tree.delete(*self.audio_tree.get_children())
        for msg in messages:
            duration = f"{msg[3]:.1f}s" if msg[3] else "N/A"
            self.audio_tree.insert("", "end", values=(msg[1], msg[2], duration, msg[4]))
    
    def load_alarms(self):
        """Carica le sveglie attive"""
        alarms = self.db.get_alarms('scheduled')
        self.alarms_tree.delete(*self.alarms_tree.get_children())
        
        for alarm in alarms:
            alarm_time = datetime.datetime.fromisoformat(alarm[2])
            date_str = alarm_time.strftime("%Y-%m-%d")
            time_str = alarm_time.strftime("%H:%M")
            
            # Ottieni nome messaggio audio
            audio_name = "Nessuno"
            if alarm[3]:  # Se c'è un audio_message_id
                audio_messages = self.db.get_audio_messages()
                for msg in audio_messages:
                    if msg[0] == alarm[3]:
                        audio_name = msg[1]
                        break
            
            self.alarms_tree.insert("", "end", values=(
                alarm[1], date_str, time_str, audio_name, alarm[4]
            ))
    
    def set_alarm(self):
        """Imposta una nuova sveglia"""
        try:
            room = self.selected_room.get()
            date_str = self.date_entry.get()
            time_str = self.time_entry.get()
            audio_name = self.selected_audio.get()
            
            if not room or not date_str or not time_str:
                messagebox.showerror("Errore", "Compila tutti i campi obbligatori")
                return
            
            # Combina data e ora
            alarm_datetime = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            # Verifica che la data sia nel futuro
            if alarm_datetime <= datetime.datetime.now():
                messagebox.showerror("Errore", "La sveglia deve essere programmata nel futuro")
                return
            
            # Ottieni ID del messaggio audio selezionato
            audio_id = None
            if audio_name:
                messages = self.db.get_audio_messages()
                for msg in messages:
                    if msg[1] == audio_name:
                        audio_id = msg[0]
                        break
            
            # Aggiungi sveglia al database
            alarm_id = self.db.add_alarm(room, alarm_datetime.isoformat(), audio_id)
            
            messagebox.showinfo("Successo", f"Sveglia impostata per camera {room} alle {time_str}")
            self.load_alarms()
            self.status_var.set(f"Sveglia aggiunta: Camera {room} - {alarm_datetime.strftime('%d/%m/%Y %H:%M')}")
            
        except ValueError as e:
            messagebox.showerror("Errore", f"Formato data/ora non valido: {e}")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'impostazione della sveglia: {e}")
    
    def test_audio(self):
        """Testa la riproduzione del messaggio audio selezionato"""
        audio_name = self.selected_audio.get()
        if not audio_name:
            messagebox.showwarning("Attenzione", "Seleziona un messaggio audio")
            return
        
        # Per ora mostra solo un messaggio - implementeremo la riproduzione audio dopo
        messagebox.showinfo("Test Audio", f"Riproduzione del messaggio: {audio_name}\n\n(Implementazione audio in corso)")
    
    def load_audio_file(self):
        """Carica un nuovo file audio"""
        file_path = filedialog.askopenfilename(
            title="Seleziona file audio",
            filetypes=[
                ("File Audio", "*.mp3 *.wav *.ogg"),
                ("MP3", "*.mp3"),
                ("WAV", "*.wav"),
                ("OGG", "*.ogg"),
                ("Tutti i file", "*.*")
            ]
        )
        
        if file_path:
            # Ottieni nome file senza estensione
            filename = os.path.basename(file_path)
            name = os.path.splitext(filename)[0]
            
            # Copia file nella cartella audio
            audio_folder = AUDIO_CONFIG['audio_folder']
            dest_path = os.path.join(audio_folder, filename)
            
            try:
                import shutil
                shutil.copy2(file_path, dest_path)
                
                # Aggiungi al database
                self.db.add_audio_message(name, dest_path, category='standard')
                
                messagebox.showinfo("Successo", f"File audio caricato: {name}")
                self.load_audio_messages()
                self.status_var.set(f"File audio caricato: {name}")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel caricamento del file: {e}")
    
    def delete_audio_message(self):
        """Elimina un messaggio audio selezionato"""
        selection = self.audio_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un messaggio da eliminare")
            return
        
        item = self.audio_tree.item(selection[0])
        message_name = item['values'][0]
        
        if messagebox.askyesno("Conferma", f"Eliminare il messaggio '{message_name}'?"):
            # TODO: Implementare eliminazione dal database e file system
            messagebox.showinfo("Info", "Funzione di eliminazione in implementazione")
    
    def delete_selected_alarm(self):
        """Elimina la sveglia selezionata"""
        selection = self.alarms_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona una sveglia da eliminare")
            return
        
        item = self.alarms_tree.item(selection[0])
        room = item['values'][0]
        date = item['values'][1]
        time = item['values'][2]
        
        if messagebox.askyesno("Conferma", f"Eliminare la sveglia per camera {room} del {date} alle {time}?"):
            # TODO: Implementare eliminazione dal database
            messagebox.showinfo("Info", "Funzione di eliminazione in implementazione")

def main():
    """Funzione principale"""
    root = tk.Tk()
    app = SvegliaCentralinoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
