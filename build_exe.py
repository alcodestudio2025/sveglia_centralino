"""
Script per generare l'eseguibile Windows del Sistema Gestione Sveglie Hotel
"""
import os
import sys
import subprocess
import shutil

# Fix encoding per Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_pyinstaller():
    """Verifica se PyInstaller è installato"""
    try:
        import PyInstaller
        print("✓ PyInstaller trovato")
        return True
    except ImportError:
        print("✗ PyInstaller non trovato")
        print("\nInstallazione PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installato con successo")
            return True
        except:
            print("✗ Errore nell'installazione di PyInstaller")
            return False

def clean_build():
    """Pulisce le cartelle di build precedenti"""
    folders = ['build', 'dist', '__pycache__']
    for folder in folders:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"✓ Rimossa cartella {folder}")
            except:
                print(f"✗ Errore nella rimozione di {folder}")
    
    # Rimuovi file .spec precedenti
    spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
    for spec_file in spec_files:
        try:
            os.remove(spec_file)
            print(f"✓ Rimosso {spec_file}")
        except:
            print(f"✗ Errore nella rimozione di {spec_file}")

def create_version_file():
    """Crea il file version.txt per l'eseguibile"""
    version_info = """# UTF-8
#
# For more details about fixed file info:
# See https://docs.microsoft.com/en-us/windows/win32/menurc/versioninfo-resource

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'AlcoDe Studio 2025'),
        StringStruct(u'FileDescription', u'Sistema Gestione Sveglie Hotel'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'Sveglia Centralino'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2025 AlcoDe Studio'),
        StringStruct(u'OriginalFilename', u'SvegliaHotel.exe'),
        StringStruct(u'ProductName', u'Sistema Gestione Sveglie Hotel'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    print("✓ File version_info.txt creato")

def build_executable():
    """Genera l'eseguibile usando PyInstaller"""
    print("\n" + "="*60)
    print("GENERAZIONE ESEGUIBILE")
    print("="*60 + "\n")
    
    # Comando PyInstaller
    cmd = [
        'pyinstaller',
        '--name=SvegliaHotel',
        '--onefile',
        '--windowed',
        '--icon=NONE',
        '--add-data=audio_messages;audio_messages',
        '--add-data=logs;logs',
        '--add-data=backup;backup',
        '--hidden-import=tkinter',
        '--hidden-import=paramiko',
        '--hidden-import=psutil',
        '--hidden-import=sqlite3',
        '--collect-all=tkinter',
        '--noconsole',
        'main.py'
    ]
    
    print("Comando PyInstaller:")
    print(" ".join(cmd))
    print("\nGenerazione in corso...\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("\n✓ Eseguibile generato con successo!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Errore nella generazione:")
        print(e.stdout)
        print(e.stderr)
        return False

def create_portable_package():
    """Crea un package portable con tutti i file necessari"""
    print("\n" + "="*60)
    print("CREAZIONE PACKAGE PORTABLE")
    print("="*60 + "\n")
    
    if not os.path.exists('dist/SvegliaHotel.exe'):
        print("✗ Eseguibile non trovato")
        return False
    
    # Crea cartella release
    release_folder = 'SvegliaHotel_v1.0'
    if os.path.exists(release_folder):
        shutil.rmtree(release_folder)
    os.makedirs(release_folder)
    
    print(f"✓ Creata cartella {release_folder}")
    
    # Copia eseguibile
    shutil.copy('dist/SvegliaHotel.exe', release_folder)
    print("✓ Copiato eseguibile")
    
    # Crea cartelle necessarie
    folders = ['audio_messages', 'logs', 'backup']
    for folder in folders:
        folder_path = os.path.join(release_folder, folder)
        os.makedirs(folder_path, exist_ok=True)
        # Crea file .gitkeep per mantenere la cartella
        with open(os.path.join(folder_path, '.gitkeep'), 'w') as f:
            f.write('')
    print("✓ Create cartelle necessarie")
    
    # Copia file di configurazione esempio
    config_example = """# Copia questo file in config.py e modifica con i tuoi dati

# Configurazione centralino PBX
PBX_CONFIG = {
    'host': '192.168.1.100',      # IP del tuo centralino
    'port': 22,                    # Porta SSH (default 22)
    'username': 'admin',           # Username SSH
    'password': 'password',        # Password SSH - CAMBIALA!
    'timeout': 10
}

# Configurazione hotel
HOTEL_CONFIG = {
    'name': 'Il Tuo Hotel',
    'total_rooms': 50,
    'room_prefix': '1'
}

# Configurazione audio
AUDIO_CONFIG = {
    'supported_formats': ['.mp3', '.wav', '.ogg'],
    'audio_folder': 'audio_messages',
    'default_volume': 0.8
}

# Configurazione sveglie
ALARM_CONFIG = {
    'snooze_options': [5, 10, 15, 30],
    'max_snooze_attempts': 3,
    'call_timeout': 30
}
"""
    
    with open(os.path.join(release_folder, 'config.example.py'), 'w', encoding='utf-8') as f:
        f.write(config_example)
    print("✓ Creato config.example.py")
    
    # Copia README
    if os.path.exists('README.md'):
        shutil.copy('README.md', release_folder)
        print("✓ Copiato README.md")
    
    # Crea guida rapida
    quick_guide = """# 🚀 GUIDA RAPIDA - Sistema Gestione Sveglie Hotel v1.0

## PRIMO AVVIO

1. **Copia config.example.py in config.py**
   - Apri config.example.py
   - Modifica con i dati del TUO centralino PBX
   - Salva come config.py

2. **Avvia SvegliaHotel.exe**
   - Doppio click su SvegliaHotel.exe
   - L'applicazione si aprirà

3. **Configura il Sistema**
   - Menu → Impostazioni
   - Tab "Centralino PBX": verifica i dati
   - Clicca "Test Connessione" per verificare

## CONFIGURAZIONE MINIMA

### Dati Necessari per config.py:
```python
PBX_CONFIG = {
    'host': '192.168.1.XXX',    # IP del centralino
    'port': 22,
    'username': 'tuo_username',
    'password': 'tua_password',
    'timeout': 10
}
```

### Come Trovare l'IP del Centralino:
- Controlla il pannello di amministrazione del PBX
- Oppure usa `ping nome_centralino`
- O chiedi all'amministratore di rete

## UTILIZZO RAPIDO

### 1. Configura Camere
- Menu → Gestione → Gestisci Camere
- Verifica le camere precaricate (101-150)
- Modifica gli interni telefonici se necessario

### 2. Carica Messaggi Audio
- Menu → Gestione → Gestisci Messaggi Audio
- Carica file MP3 per:
  - Messaggio Sveglia
  - Conferma Riprogrammazione
  - Saluto
- Seleziona la lingua corretta

### 3. Programma una Sveglia
- Schermata principale
- Seleziona camera
- Imposta ora
- Scegli messaggio audio
- Clicca "Programma Sveglia"

## RISOLUZIONE PROBLEMI

### "Errore di connessione timeout"
- Verifica IP in config.py
- Controlla che il centralino sia acceso
- Verifica che SSH sia abilitato sul PBX
- Testa con: Menu → Gestione → Test Connessione PBX

### "File audio non trovato"
- Verifica che i file siano nella cartella audio_messages/
- Ricarica i file tramite l'interfaccia

### Il programma non si avvia
- Verifica che config.py esista
- Controlla che le cartelle audio_messages, logs, backup esistano
- Guarda i log in logs/sveglia_centralino.log

## SUPPORTO

- GitHub: https://github.com/alcodestudio2025/sveglia_centralino
- Email: support@alcodestudio.com
- Documentazione completa: README.md

## NOTE IMPORTANTI

⚠️ **PRIMA DEL PRIMO UTILIZZO:**
1. Crea config.py da config.example.py
2. Configura i dati del PBX
3. Testa la connessione
4. Carica almeno un messaggio audio

⚠️ **BACKUP:**
- Menu → Gestione → Backup e Ripristino
- Fai backup regolari del database

⚠️ **SICUREZZA:**
- Non condividere il file config.py (contiene password)
- Cambia la password di default del PBX

---

Versione: 1.0.0
Data: 2025-01-XX
"""
    
    with open(os.path.join(release_folder, 'GUIDA_RAPIDA.txt'), 'w', encoding='utf-8') as f:
        f.write(quick_guide)
    print("✓ Creata GUIDA_RAPIDA.txt")
    
    # Crea file batch per avvio rapido
    batch_file = """@echo off
title Sistema Gestione Sveglie Hotel
echo.
echo ================================================
echo   Sistema Gestione Sveglie Hotel v1.0
echo   AlcoDe Studio 2025
echo ================================================
echo.
echo Avvio applicazione...
echo.

REM Verifica se config.py esiste
if not exist config.py (
    echo ATTENZIONE: File config.py non trovato!
    echo.
    echo Prima del primo avvio:
    echo 1. Copia config.example.py in config.py
    echo 2. Modifica config.py con i dati del tuo PBX
    echo 3. Riavvia l'applicazione
    echo.
    pause
    exit
)

REM Avvia l'applicazione
start "" SvegliaHotel.exe

exit
"""
    
    with open(os.path.join(release_folder, 'AVVIA.bat'), 'w', encoding='utf-8') as f:
        f.write(batch_file)
    print("✓ Creato AVVIA.bat")
    
    print(f"\n✓ Package portable creato: {release_folder}/")
    print(f"\nContenuto:")
    for item in os.listdir(release_folder):
        item_path = os.path.join(release_folder, item)
        if os.path.isfile(item_path):
            size = os.path.getsize(item_path)
            print(f"  - {item} ({size:,} bytes)")
        else:
            print(f"  - {item}/ (cartella)")
    
    return True

def create_zip_archive():
    """Crea un archivio ZIP del package"""
    release_folder = 'SvegliaHotel_v1.0'
    
    if not os.path.exists(release_folder):
        print("✗ Package non trovato")
        return False
    
    print("\n" + "="*60)
    print("CREAZIONE ARCHIVIO ZIP")
    print("="*60 + "\n")
    
    zip_name = f'{release_folder}.zip'
    
    try:
        shutil.make_archive(release_folder, 'zip', '.', release_folder)
        if os.path.exists(zip_name):
            size = os.path.getsize(zip_name)
            print(f"✓ Archivio creato: {zip_name} ({size:,} bytes)")
            print(f"\nIl file è pronto per la distribuzione!")
            return True
        else:
            print("✗ Errore nella creazione dell'archivio")
            return False
    except Exception as e:
        print(f"✗ Errore: {e}")
        return False

def main():
    """Funzione principale"""
    print("\n" + "="*60)
    print("SISTEMA GESTIONE SVEGLIE HOTEL v1.0")
    print("BUILD SCRIPT")
    print("="*60 + "\n")
    
    # Step 1: Verifica PyInstaller
    print("STEP 1: Verifica dipendenze")
    print("-" * 60)
    if not check_pyinstaller():
        print("\n✗ Impossibile continuare senza PyInstaller")
        return
    
    # Step 2: Pulizia
    print("\nSTEP 2: Pulizia build precedenti")
    print("-" * 60)
    clean_build()
    
    # Step 3: Crea file versione
    print("\nSTEP 3: Creazione file versione")
    print("-" * 60)
    create_version_file()
    
    # Step 4: Build eseguibile
    print("\nSTEP 4: Build eseguibile")
    print("-" * 60)
    if not build_executable():
        print("\n✗ Build fallita")
        return
    
    # Step 5: Package portable
    print("\nSTEP 5: Creazione package portable")
    print("-" * 60)
    if not create_portable_package():
        print("\n✗ Creazione package fallita")
        return
    
    # Step 6: Archivio ZIP
    print("\nSTEP 6: Creazione archivio ZIP")
    print("-" * 60)
    create_zip_archive()
    
    # Riepilogo finale
    print("\n" + "="*60)
    print("BUILD COMPLETATA CON SUCCESSO!")
    print("="*60 + "\n")
    
    print("📦 File generati:")
    print(f"  - dist/SvegliaHotel.exe (eseguibile singolo)")
    print(f"  - SvegliaHotel_v1.0/ (package completo)")
    print(f"  - SvegliaHotel_v1.0.zip (archivio distribuzione)")
    
    print("\n📋 Prossimi passi:")
    print("  1. Testa SvegliaHotel_v1.0/SvegliaHotel.exe")
    print("  2. Configura config.py con dati PBX reali")
    print("  3. Esegui test completi")
    print("  4. Distribuisci SvegliaHotel_v1.0.zip")
    
    print("\n✨ Pronto per i test reali!\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Build interrotta dall'utente")
    except Exception as e:
        print(f"\n\n✗ Errore imprevisto: {e}")
        import traceback
        traceback.print_exc()

