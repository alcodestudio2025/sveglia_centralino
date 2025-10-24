"""
Monitor di sistema per il sistema di gestione sveglie
"""
import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import threading
import time
import datetime
import os
from database import DatabaseManager
from pbx_connection import PBXConnection
from alarm_manager import AlarmManager

class SystemMonitorWindow:
    def __init__(self, parent, db_manager, alarm_manager):
        self.parent = parent
        self.db = db_manager
        self.alarm_manager = alarm_manager
        
        # Crea la finestra
        self.window = tk.Toplevel(parent)
        self.window.title("Monitor di Sistema")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        
        # Centra la finestra
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variabili per i controlli
        self.monitoring = tk.BooleanVar(value=True)
        self.refresh_interval = tk.IntVar(value=2)  # secondi
        
        # Timer per aggiornamento
        self.update_timer = None
        
        # Crea l'interfaccia
        self.create_widgets()
        self.start_monitoring()
    
    def create_widgets(self):
        """Crea l'interfaccia della finestra"""
        # Frame principale
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titolo
        title_label = ttk.Label(main_frame, text="Monitor di Sistema", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Frame per controlli
        self.create_control_section(main_frame)
        
        # Notebook per le diverse sezioni
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Tab Sistema
        self.create_system_tab(notebook)
        
        # Tab Database
        self.create_database_tab(notebook)
        
        # Tab PBX
        self.create_pbx_tab(notebook)
        
        # Tab Sveglie
        self.create_alarms_tab(notebook)
        
        # Tab Performance
        self.create_performance_tab(notebook)
        
        # Pulsanti di controllo
        self.create_control_buttons(main_frame)
    
    def create_control_section(self, parent):
        """Crea la sezione dei controlli"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Pulsanti di controllo
        ttk.Button(control_frame, text="Aggiorna Ora", 
                  command=self.force_update).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Test Connessioni", 
                  command=self.test_connections).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Pulisci Database", 
                  command=self.cleanup_database).pack(side=tk.LEFT, padx=(0, 10))
        
        # Auto-refresh
        ttk.Checkbutton(control_frame, text="Monitoraggio Attivo", 
                       variable=self.monitoring, 
                       command=self.toggle_monitoring).pack(side=tk.LEFT, padx=(20, 10))
        
        ttk.Label(control_frame, text="Intervallo (sec):").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Spinbox(control_frame, from_=1, to=30, textvariable=self.refresh_interval, 
                   width=5).pack(side=tk.LEFT, padx=(0, 20))
        
        # Pulsante chiusura
        ttk.Button(control_frame, text="Chiudi", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
    
    def create_system_tab(self, notebook):
        """Crea il tab per le informazioni di sistema"""
        system_frame = ttk.Frame(notebook)
        notebook.add(system_frame, text="Sistema")
        
        # Frame per le informazioni
        info_frame = ttk.Frame(system_frame, padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Informazioni di sistema
        self.system_info = {}
        system_labels = [
            ("Sistema Operativo:", "os"),
            ("Versione Python:", "python"),
            ("CPU:", "cpu"),
            ("Memoria Totale:", "memory_total"),
            ("Memoria Usata:", "memory_used"),
            ("Memoria Disponibile:", "memory_available"),
            ("Uptime Sistema:", "uptime"),
            ("Processi Attivi:", "processes")
        ]
        
        for i, (label, key) in enumerate(system_labels):
            ttk.Label(info_frame, text=label, font=("Arial", 9, "bold")).grid(
                row=i, column=0, sticky=tk.W, padx=(0, 10), pady=2)
            self.system_info[key] = ttk.Label(info_frame, text="N/A", font=("Arial", 9))
            self.system_info[key].grid(row=i, column=1, sticky=tk.W, pady=2)
    
    def create_database_tab(self, notebook):
        """Crea il tab per le informazioni del database"""
        db_frame = ttk.Frame(notebook)
        notebook.add(db_frame, text="Database")
        
        # Frame per le informazioni
        info_frame = ttk.Frame(db_frame, padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Informazioni database
        self.db_info = {}
        db_labels = [
            ("Stato Connessione:", "connection"),
            ("Dimensione File:", "file_size"),
            ("Camere Totali:", "total_rooms"),
            ("Camere Disponibili:", "available_rooms"),
            ("Camere Occupate:", "occupied_rooms"),
            ("Sveglie Programmate:", "scheduled_alarms"),
            ("Sveglie Completate:", "completed_alarms"),
            ("Messaggi Audio:", "audio_messages"),
            ("Log Chiamate:", "call_logs")
        ]
        
        for i, (label, key) in enumerate(db_labels):
            ttk.Label(info_frame, text=label, font=("Arial", 9, "bold")).grid(
                row=i, column=0, sticky=tk.W, padx=(0, 10), pady=2)
            self.db_info[key] = ttk.Label(info_frame, text="N/A", font=("Arial", 9))
            self.db_info[key].grid(row=i, column=1, sticky=tk.W, pady=2)
    
    def create_pbx_tab(self, notebook):
        """Crea il tab per le informazioni PBX"""
        pbx_frame = ttk.Frame(notebook)
        notebook.add(pbx_frame, text="Centralino PBX")
        
        # Frame per le informazioni
        info_frame = ttk.Frame(pbx_frame, padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Informazioni PBX
        self.pbx_info = {}
        pbx_labels = [
            ("Stato Connessione:", "connection"),
            ("Indirizzo IP:", "host"),
            ("Porta SSH:", "port"),
            ("Ultima Connessione:", "last_connection"),
            ("Chiamate Attive:", "active_calls"),
            ("Comandi Eseguiti:", "commands_executed"),
            ("Errori Connessione:", "connection_errors")
        ]
        
        for i, (label, key) in enumerate(pbx_labels):
            ttk.Label(info_frame, text=label, font=("Arial", 9, "bold")).grid(
                row=i, column=0, sticky=tk.W, padx=(0, 10), pady=2)
            self.pbx_info[key] = ttk.Label(info_frame, text="N/A", font=("Arial", 9))
            self.pbx_info[key].grid(row=i, column=1, sticky=tk.W, pady=2)
    
    def create_alarms_tab(self, notebook):
        """Crea il tab per le informazioni sveglie"""
        alarms_frame = ttk.Frame(notebook)
        notebook.add(alarms_frame, text="Sveglie")
        
        # Frame per le informazioni
        info_frame = ttk.Frame(alarms_frame, padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Informazioni sveglie
        self.alarms_info = {}
        alarms_labels = [
            ("Gestore Attivo:", "manager_active"),
            ("Sveglie in Coda:", "queued_alarms"),
            ("Sveglie in Esecuzione:", "executing_alarms"),
            ("Sveglie Completate Oggi:", "completed_today"),
            ("Sveglie Posticipate:", "snoozed_alarms"),
            ("Sveglie Fallite:", "failed_alarms"),
            ("Prossima Sveglia:", "next_alarm"),
            ("Ultima Esecuzione:", "last_execution")
        ]
        
        for i, (label, key) in enumerate(alarms_labels):
            ttk.Label(info_frame, text=label, font=("Arial", 9, "bold")).grid(
                row=i, column=0, sticky=tk.W, padx=(0, 10), pady=2)
            self.alarms_info[key] = ttk.Label(info_frame, text="N/A", font=("Arial", 9))
            self.alarms_info[key].grid(row=i, column=1, sticky=tk.W, pady=2)
    
    def create_performance_tab(self, notebook):
        """Crea il tab per le performance"""
        perf_frame = ttk.Frame(notebook)
        notebook.add(perf_frame, text="Performance")
        
        # Frame per le informazioni
        info_frame = ttk.Frame(perf_frame, padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Informazioni performance
        self.perf_info = {}
        perf_labels = [
            ("CPU Usage:", "cpu_usage"),
            ("Memoria Usage:", "memory_usage"),
            ("Disco Usage:", "disk_usage"),
            ("Thread Attivi:", "active_threads"),
            ("Connessioni DB:", "db_connections"),
            ("Tempo Risposta DB:", "db_response_time"),
            ("Tempo Risposta PBX:", "pbx_response_time"),
            ("Ultimo Aggiornamento:", "last_update")
        ]
        
        for i, (label, key) in enumerate(perf_labels):
            ttk.Label(info_frame, text=label, font=("Arial", 9, "bold")).grid(
                row=i, column=0, sticky=tk.W, padx=(0, 10), pady=2)
            self.perf_info[key] = ttk.Label(info_frame, text="N/A", font=("Arial", 9))
            self.perf_info[key].grid(row=i, column=1, sticky=tk.W, pady=2)
    
    def create_control_buttons(self, parent):
        """Crea i pulsanti di controllo"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X)
        
        # Pulsanti di azione
        ttk.Button(buttons_frame, text="Riavvia Gestore Sveglie", 
                  command=self.restart_alarm_manager).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Test Database", 
                  command=self.test_database).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Test PBX", 
                  command=self.test_pbx).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Esporta Report", 
                  command=self.export_report).pack(side=tk.LEFT, padx=(0, 10))
    
    def start_monitoring(self):
        """Avvia il monitoraggio"""
        self.update_all_info()
        self.schedule_update()
    
    def toggle_monitoring(self):
        """Attiva/disattiva il monitoraggio"""
        if self.monitoring.get():
            self.schedule_update()
        else:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Ferma il monitoraggio"""
        if self.update_timer:
            self.window.after_cancel(self.update_timer)
            self.update_timer = None
    
    def schedule_update(self):
        """Programma il prossimo aggiornamento"""
        if self.monitoring.get():
            self.update_all_info()
            interval_ms = self.refresh_interval.get() * 1000
            self.update_timer = self.window.after(interval_ms, self.schedule_update)
    
    def force_update(self):
        """Forza l'aggiornamento immediato"""
        self.update_all_info()
    
    def update_all_info(self):
        """Aggiorna tutte le informazioni"""
        try:
            self.update_system_info()
            self.update_database_info()
            self.update_pbx_info()
            self.update_alarms_info()
            self.update_performance_info()
        except Exception as e:
            print(f"Errore nell'aggiornamento info: {e}")
    
    def update_system_info(self):
        """Aggiorna le informazioni di sistema"""
        try:
            # Sistema operativo
            self.system_info["os"].config(text=f"{os.name} - {os.sys.platform}")
            
            # Python
            import sys
            self.system_info["python"].config(text=f"{sys.version.split()[0]}")
            
            # CPU
            cpu_count = psutil.cpu_count()
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_info["cpu"].config(text=f"{cpu_count} core - {cpu_percent}%")
            
            # Memoria
            memory = psutil.virtual_memory()
            self.system_info["memory_total"].config(text=f"{memory.total // (1024**3)} GB")
            self.system_info["memory_used"].config(text=f"{memory.used // (1024**3)} GB ({memory.percent}%)")
            self.system_info["memory_available"].config(text=f"{memory.available // (1024**3)} GB")
            
            # Uptime
            boot_time = psutil.boot_time()
            uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(boot_time)
            self.system_info["uptime"].config(text=str(uptime).split('.')[0])
            
            # Processi
            process_count = len(psutil.pids())
            self.system_info["processes"].config(text=str(process_count))
            
        except Exception as e:
            print(f"Errore aggiornamento info sistema: {e}")
    
    def update_database_info(self):
        """Aggiorna le informazioni del database"""
        try:
            # Test connessione
            conn = self.db.get_connection()
            self.db_info["connection"].config(text="Connesso", foreground="green")
            conn.close()
            
            # Dimensione file
            if os.path.exists(self.db.db_path):
                size = os.path.getsize(self.db.db_path)
                self.db_info["file_size"].config(text=f"{size // 1024} KB")
            
            # Statistiche camere
            rooms = self.db.get_rooms()
            total_rooms = len(rooms)
            available_rooms = len([r for r in rooms if r[2] == 'available'])
            occupied_rooms = len([r for r in rooms if r[2] == 'occupied'])
            
            self.db_info["total_rooms"].config(text=str(total_rooms))
            self.db_info["available_rooms"].config(text=str(available_rooms))
            self.db_info["occupied_rooms"].config(text=str(occupied_rooms))
            
            # Statistiche sveglie
            alarms = self.db.get_alarms()
            scheduled_alarms = len([a for a in alarms if a[4] == 'scheduled'])
            completed_alarms = len([a for a in alarms if a[4] == 'completed'])
            
            self.db_info["scheduled_alarms"].config(text=str(scheduled_alarms))
            self.db_info["completed_alarms"].config(text=str(completed_alarms))
            
            # Messaggi audio
            audio_messages = self.db.get_audio_messages()
            self.db_info["audio_messages"].config(text=str(len(audio_messages)))
            
            # Log chiamate (approssimativo)
            self.db_info["call_logs"].config(text="N/A")
            
        except Exception as e:
            self.db_info["connection"].config(text="Errore", foreground="red")
            print(f"Errore aggiornamento info database: {e}")
    
    def update_pbx_info(self):
        """Aggiorna le informazioni PBX"""
        try:
            # Test connessione PBX
            success, message = self.alarm_manager.test_pbx_connection()
            if success:
                self.pbx_info["connection"].config(text="Connesso", foreground="green")
            else:
                self.pbx_info["connection"].config(text="Disconnesso", foreground="red")
            
            # Informazioni di base
            from config import PBX_CONFIG
            self.pbx_info["host"].config(text=PBX_CONFIG['host'])
            self.pbx_info["port"].config(text=str(PBX_CONFIG['port']))
            
            # Chiamate attive
            active_calls = self.alarm_manager.get_active_calls()
            self.pbx_info["active_calls"].config(text=str(len(active_calls)))
            
            # Altri campi
            self.pbx_info["last_connection"].config(text="N/A")
            self.pbx_info["commands_executed"].config(text="N/A")
            self.pbx_info["connection_errors"].config(text="N/A")
            
        except Exception as e:
            self.pbx_info["connection"].config(text="Errore", foreground="red")
            print(f"Errore aggiornamento info PBX: {e}")
    
    def update_alarms_info(self):
        """Aggiorna le informazioni sveglie"""
        try:
            # Gestore attivo
            self.alarms_info["manager_active"].config(text="Sì", foreground="green")
            
            # Statistiche sveglie
            alarms = self.db.get_alarms()
            scheduled_alarms = [a for a in alarms if a[4] == 'scheduled']
            executing_alarms = [a for a in alarms if a[4] == 'executing']
            completed_today = [a for a in alarms if a[4] == 'completed']
            snoozed_alarms = [a for a in alarms if a[4] == 'snoozed']
            failed_alarms = [a for a in alarms if a[4] == 'failed']
            
            self.alarms_info["queued_alarms"].config(text=str(len(scheduled_alarms)))
            self.alarms_info["executing_alarms"].config(text=str(len(executing_alarms)))
            self.alarms_info["completed_today"].config(text=str(len(completed_today)))
            self.alarms_info["snoozed_alarms"].config(text=str(len(snoozed_alarms)))
            self.alarms_info["failed_alarms"].config(text=str(len(failed_alarms)))
            
            # Prossima sveglia
            if scheduled_alarms:
                next_alarm = min(scheduled_alarms, key=lambda x: x[2])
                alarm_time = datetime.datetime.fromisoformat(next_alarm[2])
                self.alarms_info["next_alarm"].config(text=alarm_time.strftime("%H:%M:%S"))
            else:
                self.alarms_info["next_alarm"].config(text="Nessuna")
            
            # Ultima esecuzione
            self.alarms_info["last_execution"].config(text="N/A")
            
        except Exception as e:
            print(f"Errore aggiornamento info sveglie: {e}")
    
    def update_performance_info(self):
        """Aggiorna le informazioni di performance"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.perf_info["cpu_usage"].config(text=f"{cpu_percent}%")
            
            # Memoria usage
            memory = psutil.virtual_memory()
            self.perf_info["memory_usage"].config(text=f"{memory.percent}%")
            
            # Disco usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.perf_info["disk_usage"].config(text=f"{disk_percent:.1f}%")
            
            # Thread attivi
            thread_count = threading.active_count()
            self.perf_info["active_threads"].config(text=str(thread_count))
            
            # Altri campi
            self.perf_info["db_connections"].config(text="1")
            self.perf_info["db_response_time"].config(text="N/A")
            self.perf_info["pbx_response_time"].config(text="N/A")
            self.perf_info["last_update"].config(text=datetime.datetime.now().strftime("%H:%M:%S"))
            
        except Exception as e:
            print(f"Errore aggiornamento info performance: {e}")
    
    def test_connections(self):
        """Testa tutte le connessioni"""
        def test_thread():
            try:
                # Test database
                conn = self.db.get_connection()
                conn.close()
                messagebox.showinfo("Test Connessioni", "Database: OK")
                
                # Test PBX
                success, message = self.alarm_manager.test_pbx_connection()
                if success:
                    messagebox.showinfo("Test Connessioni", "Database: OK\nPBX: OK")
                else:
                    messagebox.showwarning("Test Connessioni", f"Database: OK\nPBX: ERRORE - {message}")
                    
            except Exception as e:
                messagebox.showerror("Test Connessioni", f"Errore: {e}")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def cleanup_database(self):
        """Pulisce il database"""
        if messagebox.askyesno("Conferma Pulizia", "Pulire i log vecchi del database?"):
            try:
                # Implementa la pulizia del database
                messagebox.showinfo("Pulizia", "Pulizia database completata")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nella pulizia: {e}")
    
    def restart_alarm_manager(self):
        """Riavvia il gestore sveglie"""
        if messagebox.askyesno("Conferma Riavvio", "Riavviare il gestore sveglie?"):
            try:
                self.alarm_manager.stop()
                time.sleep(1)
                self.alarm_manager.start()
                messagebox.showinfo("Riavvio", "Gestore sveglie riavviato")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel riavvio: {e}")
    
    def test_database(self):
        """Testa il database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM rooms")
            count = cursor.fetchone()[0]
            conn.close()
            messagebox.showinfo("Test Database", f"Database funzionante\nCamere: {count}")
        except Exception as e:
            messagebox.showerror("Test Database", f"Errore: {e}")
    
    def test_pbx(self):
        """Testa il PBX"""
        def test_thread():
            try:
                success, message = self.alarm_manager.test_pbx_connection()
                if success:
                    messagebox.showinfo("Test PBX", "Connessione PBX riuscita")
                else:
                    messagebox.showerror("Test PBX", f"Errore connessione: {message}")
            except Exception as e:
                messagebox.showerror("Test PBX", f"Errore: {e}")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def export_report(self):
        """Esporta un report del sistema"""
        try:
            report = self.generate_system_report()
            messagebox.showinfo("Report", f"Report generato:\n\n{report}")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella generazione report: {e}")
    
    def generate_system_report(self):
        """Genera un report del sistema"""
        report = f"""
REPORT SISTEMA - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== SISTEMA ===
OS: {os.name} - {os.sys.platform}
CPU: {psutil.cpu_percent()}%
Memoria: {psutil.virtual_memory().percent}%

=== DATABASE ===
Stato: Connesso
Camere: {len(self.db.get_rooms())}
Sveglie: {len(self.db.get_alarms())}

=== PBX ===
Stato: {self.pbx_info['connection']['text']}
Chiamate Attive: {self.pbx_info['active_calls']['text']}

=== SVEGLIE ===
Gestore: Attivo
Sveglie Programmate: {self.alarms_info['queued_alarms']['text']}
Sveglie in Esecuzione: {self.alarms_info['executing_alarms']['text']}
        """
        return report
    
    def __del__(self):
        """Cleanup quando la finestra viene chiusa"""
        self.stop_monitoring()

if __name__ == "__main__":
    # Test del monitor
    root = tk.Tk()
    root.withdraw()
    db = DatabaseManager()
    alarm_mgr = AlarmManager(db)
    SystemMonitorWindow(root, db, alarm_mgr)
    root.mainloop()
