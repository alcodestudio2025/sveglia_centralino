"""
Gestione delle camere dell'hotel
"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from database import DatabaseManager

class RoomManagerWindow:
    def __init__(self, parent, db_manager, on_save_callback=None):
        self.parent = parent
        self.db = db_manager
        self.on_save_callback = on_save_callback
        
        # Crea la finestra
        self.window = tk.Toplevel(parent)
        self.window.title("Gestione Camere Hotel")
        self.window.geometry("900x600")
        self.window.resizable(True, True)
        
        # Centra la finestra
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variabili per i controlli
        self.selected_room_id = None
        self.room_number_var = tk.StringVar()
        self.phone_extension_var = tk.StringVar()
        self.room_status_var = tk.StringVar(value="available")
        self.room_color_var = tk.StringVar(value="#FFFFFF")
        self.room_label_var = tk.StringVar()
        
        # Crea l'interfaccia
        self.create_widgets()
        self.load_rooms()
    
    def create_widgets(self):
        """Crea l'interfaccia della finestra"""
        # Frame principale
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titolo
        title_label = ttk.Label(main_frame, text="Gestione Camere Hotel", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame per input camere
        self.create_input_section(main_frame)
        
        # Frame per lista camere
        self.create_rooms_list_section(main_frame)
        
        # Pulsanti di controllo
        self.create_control_buttons(main_frame)
    
    def create_input_section(self, parent):
        """Crea la sezione per l'input delle camere"""
        input_frame = ttk.LabelFrame(parent, text="Dettagli Camera", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 15))
        input_frame.columnconfigure(1, weight=1)
        
        # Numero camera
        ttk.Label(input_frame, text="Numero Camera:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(input_frame, textvariable=self.room_number_var, width=20).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20), pady=5)
        
        # Interno telefonico
        ttk.Label(input_frame, text="Interno Telefonico:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(input_frame, textvariable=self.phone_extension_var, width=15).grid(row=0, column=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status
        ttk.Label(input_frame, text="Stato:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        status_combo = ttk.Combobox(input_frame, textvariable=self.room_status_var, 
                                   values=["available", "occupied", "maintenance", "cleaning"], 
                                   state="readonly", width=15)
        status_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 20), pady=5)
        
        # Colore
        ttk.Label(input_frame, text="Colore:").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=5)
        color_frame = ttk.Frame(input_frame)
        color_frame.grid(row=1, column=3, sticky=(tk.W, tk.E), pady=5)
        
        self.color_display = tk.Canvas(color_frame, width=30, height=25, bd=2, relief=tk.SUNKEN, 
                                      bg=self.room_color_var.get())
        self.color_display.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(color_frame, text="Scegli Colore", 
                  command=self.choose_color).pack(side=tk.LEFT)
        
        # Etichetta
        ttk.Label(input_frame, text="Etichetta:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(input_frame, textvariable=self.room_label_var, width=30).grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5)
    
    def create_rooms_list_section(self, parent):
        """Crea la sezione per la lista delle camere"""
        list_frame = ttk.LabelFrame(parent, text="Lista Camere", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview per le camere
        columns = ("ID", "Numero", "Interno", "Stato", "Colore", "Etichetta", "Creata")
        self.rooms_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # Configurazione colonne
        column_widths = {"ID": 50, "Numero": 100, "Interno": 80, "Stato": 100, "Colore": 80, "Etichetta": 200, "Creata": 120}
        
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
        ttk.Button(buttons_frame, text="Aggiungi Camera", 
                  command=self.add_room).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Modifica Camera", 
                  command=self.edit_room).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Elimina Camera", 
                  command=self.delete_room).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Pulisci Campi", 
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
        if color_code[1]:  # color_code[1] è la stringa hex
            self.room_color_var.set(color_code[1])
            self.color_display.config(bg=color_code[1])
    
    def load_rooms(self):
        """Carica la lista delle camere"""
        # Pulisce la lista
        for item in self.rooms_tree.get_children():
            self.rooms_tree.delete(item)
        
        try:
            rooms = self.db.get_rooms()
            for room in rooms:
                # Formatta la data di creazione
                created_date = room[5].split(' ')[0] if len(room) > 5 and room[5] else "N/A"
                
                # Inserisci nella lista
                item_id = self.rooms_tree.insert("", "end", values=(
                    room[0],  # ID
                    room[1],  # Numero
                    room[2] if len(room) > 2 else "",  # Interno telefonico
                    room[3] if len(room) > 3 else "available",  # Stato
                    room[4] if len(room) > 4 else "#FFFFFF",  # Colore
                    room[5] if len(room) > 5 else "",  # Etichetta
                    created_date  # Data creazione
                ))
                
                # Colora la riga in base allo status
                status = room[3] if len(room) > 3 else "available"
                if status == "occupied":
                    self.rooms_tree.set(item_id, "Stato", "Occupata")
                elif status == "maintenance":
                    self.rooms_tree.set(item_id, "Stato", "Manutenzione")
                elif status == "cleaning":
                    self.rooms_tree.set(item_id, "Stato", "Pulizia")
                else:
                    self.rooms_tree.set(item_id, "Stato", "Disponibile")
        
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel caricamento delle camere: {e}")
    
    def on_room_select(self, event):
        """Gestisce la selezione di una camera"""
        selected_item = self.rooms_tree.focus()
        if selected_item:
            values = self.rooms_tree.item(selected_item, 'values')
            self.selected_room_id = values[0]
            self.room_number_var.set(values[1])
            self.phone_extension_var.set(values[2])
            
            # Converte lo status visualizzato in quello del database
            status_display = values[3]
            if status_display == "Occupata":
                self.room_status_var.set("occupied")
            elif status_display == "Manutenzione":
                self.room_status_var.set("maintenance")
            elif status_display == "Pulizia":
                self.room_status_var.set("cleaning")
            else:
                self.room_status_var.set("available")
            
            self.room_color_var.set(values[4])
            self.color_display.config(bg=values[4])
            self.room_label_var.set(values[5])
        else:
            self.clear_fields()
    
    def on_room_double_click(self, event):
        """Gestisce il doppio click su una camera"""
        self.edit_room()
    
    def add_room(self):
        """Aggiunge una nuova camera"""
        room_number = self.room_number_var.get().strip()
        phone_extension = self.phone_extension_var.get().strip()
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
            room_id = self.db.add_room(room_number, phone_extension, status, color, label)
            messagebox.showinfo("Successo", f"Camera {room_number} aggiunta con successo\nInterno: {phone_extension}")
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
            # Verifica se il nuovo numero esiste già (se diverso)
            existing_room = self.db.get_room(room_number)
            if existing_room and str(existing_room[0]) != str(self.selected_room_id):
                messagebox.showerror("Errore", f"La camera {room_number} esiste già")
                return
            
            # Aggiorna la camera
            self.db.update_room(self.selected_room_id, room_number, phone_extension, status, color, label)
            messagebox.showinfo("Successo", f"Camera {room_number} modificata con successo\nInterno: {phone_extension}")
            self.clear_fields()
            self.load_rooms()
            
            # Notifica l'applicazione principale
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
        
        if messagebox.askyesno("Conferma Eliminazione", 
                              f"Sei sicuro di voler eliminare la camera {room_number}?\n\n"
                              f"Questa operazione non può essere annullata."):
            try:
                self.db.delete_room(self.selected_room_id)
                messagebox.showinfo("Successo", f"Camera {room_number} eliminata con successo")
                self.clear_fields()
                self.load_rooms()
                
                # Notifica l'applicazione principale
                if self.on_save_callback:
                    self.on_save_callback()
                    
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nell'eliminazione della camera: {e}")
    
    def clear_fields(self):
        """Pulisce i campi di input"""
        self.selected_room_id = None
        self.room_number_var.set("")
        self.phone_extension_var.set("")
        self.room_status_var.set("available")
        self.room_color_var.set("#FFFFFF")
        self.color_display.config(bg="#FFFFFF")
        self.room_label_var.set("")

if __name__ == "__main__":
    # Test del modulo
    root = tk.Tk()
    root.withdraw()
    db = DatabaseManager()
    RoomManagerWindow(root, db)
    root.mainloop()
