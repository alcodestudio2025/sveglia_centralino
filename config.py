"""
Configurazione del sistema di gestione sveglie per hotel
"""
import os

# Configurazione database
DATABASE_PATH = "sveglie.db"

# Configurazione centralino PBX (valori di default)
PBX_CONFIG = {
    'host': '192.168.1.100',  # IP del centralino - da configurare
    'port': 22,
    'username': 'admin',       # Credenziali SSH - da configurare
    'password': 'password',    # Password SSH - da configurare
    'timeout': 10,
    'test_on_startup': True   # Test automatico all'avvio
}

# File per salvare le configurazioni utente
SETTINGS_FILE = 'settings.json'

def load_user_config():
    """Carica le configurazioni salvate dall'utente"""
    import json
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                user_settings = json.load(f)
                # Sovrascrivi PBX_CONFIG con le impostazioni utente
                if 'pbx' in user_settings:
                    PBX_CONFIG.update(user_settings['pbx'])
                return user_settings
        except Exception as e:
            print(f"Errore nel caricamento impostazioni: {e}")
    return None

def save_user_config(settings):
    """Salva le configurazioni utente"""
    import json
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Errore nel salvataggio impostazioni: {e}")
        return False

# Carica le impostazioni utente all'importazione
load_user_config()

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
