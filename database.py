"""
Gestione database SQLite per il sistema di sveglie
"""
import sqlite3
import datetime
from config import DATABASE_PATH

class DatabaseManager:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Inizializza il database con le tabelle necessarie"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabella camere
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabella messaggi audio
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audio_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                duration REAL,
                category TEXT DEFAULT 'standard',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabella sveglie
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alarms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number TEXT NOT NULL,
                alarm_time TIMESTAMP NOT NULL,
                audio_message_id INTEGER,
                status TEXT DEFAULT 'scheduled',
                snooze_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (audio_message_id) REFERENCES audio_messages (id)
            )
        ''')
        
        # Tabella log chiamate
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS call_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alarm_id INTEGER,
                room_number TEXT NOT NULL,
                call_time TIMESTAMP NOT NULL,
                response TEXT,
                snooze_minutes INTEGER,
                status TEXT NOT NULL,
                FOREIGN KEY (alarm_id) REFERENCES alarms (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Inserisci camere di default
        self.create_default_rooms()
    
    def create_default_rooms(self):
        """Crea le camere di default per l'hotel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verifica se le camere esistono già
        cursor.execute("SELECT COUNT(*) FROM rooms")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Crea camere da 101 a 150 (50 camere)
            rooms = []
            for i in range(101, 151):
                rooms.append((f"1{i:02d}", 'available'))
            
            cursor.executemany(
                "INSERT INTO rooms (room_number, status) VALUES (?, ?)",
                rooms
            )
            conn.commit()
            print(f"Create {len(rooms)} camere di default")
        
        conn.close()
    
    def get_connection(self):
        """Restituisce una connessione al database"""
        return sqlite3.connect(self.db_path)
    
    def get_rooms(self, status=None):
        """Ottiene la lista delle camere"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute("SELECT * FROM rooms WHERE status = ? ORDER BY room_number", (status,))
        else:
            cursor.execute("SELECT * FROM rooms ORDER BY room_number")
        
        rooms = cursor.fetchall()
        conn.close()
        return rooms
    
    def get_room(self, room_number):
        """Ottiene una camera specifica"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rooms WHERE room_number = ?", (room_number,))
        room = cursor.fetchone()
        conn.close()
        return room
    
    def update_room_status(self, room_number, status):
        """Aggiorna lo status di una camera"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE rooms SET status = ? WHERE room_number = ?",
            (status, room_number)
        )
        conn.commit()
        conn.close()
    
    def add_audio_message(self, name, file_path, duration=None, category='standard'):
        """Aggiunge un messaggio audio"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audio_messages (name, file_path, duration, category) VALUES (?, ?, ?, ?)",
            (name, file_path, duration, category)
        )
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        return message_id
    
    def get_audio_messages(self, category=None):
        """Ottiene la lista dei messaggi audio"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute("SELECT * FROM audio_messages WHERE category = ? ORDER BY name", (category,))
        else:
            cursor.execute("SELECT * FROM audio_messages ORDER BY name")
        
        messages = cursor.fetchall()
        conn.close()
        return messages
    
    def add_alarm(self, room_number, alarm_time, audio_message_id=None):
        """Aggiunge una sveglia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alarms (room_number, alarm_time, audio_message_id) VALUES (?, ?, ?)",
            (room_number, alarm_time, audio_message_id)
        )
        conn.commit()
        alarm_id = cursor.lastrowid
        conn.close()
        return alarm_id
    
    def get_alarms(self, status=None, room_number=None):
        """Ottiene le sveglie"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM alarms WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if room_number:
            query += " AND room_number = ?"
            params.append(room_number)
        
        query += " ORDER BY alarm_time"
        
        cursor.execute(query, params)
        alarms = cursor.fetchall()
        conn.close()
        return alarms
    
    def update_alarm_status(self, alarm_id, status):
        """Aggiorna lo status di una sveglia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE alarms SET status = ? WHERE id = ?",
            (status, alarm_id)
        )
        conn.commit()
        conn.close()
    
    def add_call_log(self, alarm_id, room_number, call_time, response=None, snooze_minutes=None, status='completed'):
        """Aggiunge un log di chiamata"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO call_logs (alarm_id, room_number, call_time, response, snooze_minutes, status) VALUES (?, ?, ?, ?, ?, ?)",
            (alarm_id, room_number, call_time, response, snooze_minutes, status)
        )
        conn.commit()
        conn.close()

if __name__ == "__main__":
    # Test del database
    db = DatabaseManager()
    print("Database inizializzato correttamente")
    
    # Test camere
    rooms = db.get_rooms()
    print(f"Camere trovate: {len(rooms)}")
    for room in rooms[:5]:  # Mostra solo le prime 5
        print(f"Camera {room[1]} - Status: {room[2]}")
