"""
Configurazione del sistema di gestione sveglie per hotel
"""
import os

# Configurazione database
DATABASE_PATH = "sveglie.db"

# Configurazione centralino PBX
PBX_CONFIG = {
    'host': '192.168.1.100',  # IP del centralino - da configurare
    'port': 22,
    'username': 'admin',       # Credenziali SSH - da configurare
    'password': 'password',    # Password SSH - da configurare
    'timeout': 10
}

# Configurazione audio
AUDIO_CONFIG = {
    'supported_formats': ['.mp3', '.wav', '.ogg'],
    'audio_folder': 'audio_messages',
    'default_volume': 0.8
}

# Configurazione sveglie
ALARM_CONFIG = {
    'snooze_options': [5, 10, 15, 30],  # minuti
    'max_snooze_attempts': 3,
    'call_timeout': 30  # secondi
}

# Configurazione hotel
HOTEL_CONFIG = {
    'name': 'Hotel Centralino',
    'total_rooms': 50,
    'room_prefix': '1'  # Prefisso per numeri di camera
}

# Crea cartelle necessarie
def create_directories():
    """Crea le cartelle necessarie per il funzionamento del sistema"""
    directories = [
        AUDIO_CONFIG['audio_folder'],
        'logs',
        'backup'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Creata cartella: {directory}")

if __name__ == "__main__":
    create_directories()
