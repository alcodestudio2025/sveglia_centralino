# 🏨 Sistema Gestione Sveglie Hotel - v1.0

Sistema professionale per la gestione automatizzata delle sveglie in hotel tramite centralino PBX.

![Version](https://img.shields.io/badge/version-1.0--beta-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

---

## 📋 Indice

- [Caratteristiche](#-caratteristiche)
- [Requisiti](#-requisiti)
- [Installazione](#-installazione)
- [Configurazione](#-configurazione)
- [Utilizzo](#-utilizzo)
- [Funzionalità](#-funzionalità)
- [Architettura](#-architettura)
- [FAQ](#-faq)
- [Supporto](#-supporto)
- [Licenza](#-licenza)

---

## ✨ Caratteristiche

### 🎯 Core Features

- **Gestione Sveglie Automatica**: Programmazione, esecuzione e monitoraggio sveglie
- **Integrazione PBX**: Connessione SSH a centralini Asterisk/FreePBX
- **Multilingua**: 10 lingue supportate (IT, EN, FR, DE, ES, PT, RU, ZH, JA, AR)
- **Messaggi Personalizzati**: Audio MP3/WAV/OGG con azioni specifiche
- **Interno Telefonico**: Gestione separata numero camera vs interno telefonico
- **Posticipo Sveglie**: Opzioni snooze configurabili (5-10-15-30 minuti)
- **Monitor Sistema**: Monitoraggio real-time CPU, memoria, chiamate
- **Backup Automatico**: Sistema completo backup/ripristino
- **Logging Avanzato**: Log dettagliati con rotazione automatica

### 🌟 Advanced Features

- ✅ 50 camere precaricate (estendibile)
- ✅ Gestione stati camera (disponibile, occupata, manutenzione)
- ✅ Colori ed etichette personalizzate per camera
- ✅ Categorizzazione messaggi audio
- ✅ Dashboard con statistiche real-time
- ✅ Export report e log
- ✅ Interfaccia intuitiva e moderna

---

## 🔧 Requisiti

### Sistema Operativo
- Windows 10/11
- Linux (Ubuntu 20.04+, Debian 10+)
- macOS 10.15+

### Software
- **Python 3.8+** (richiesto)
- **Centralino PBX** con supporto SSH:
  - Asterisk 16+
  - FreePBX 15+
  - Altri PBX compatibili SSH

### Hardware Minimo
- CPU: 2 core
- RAM: 4 GB
- Disco: 1 GB spazio libero
- Rete: Connessione al PBX (LAN)

---

## 📦 Installazione

### 1. Clone Repository

```bash
git clone https://github.com/alcodestudio2025/sveglia_centralino.git
cd sveglia_centralino
```

### 2. Installa Dipendenze

```bash
pip install -r requirements.txt
```

### 3. Verifica Installazione

```bash
python main.py
```

---

## ⚙️ Configurazione

### Primo Avvio

Al primo avvio, configura il sistema tramite **Menu → Impostazioni**:

#### 1. **Configurazione PBX**
```python
# File: config.py
PBX_CONFIG = {
    'host': '192.168.1.100',      # IP del centralino
    'port': 22,                    # Porta SSH (default 22)
    'username': 'admin',           # Username SSH
    'password': 'your_password',   # Password SSH
    'timeout': 10                  # Timeout connessione (secondi)
}
```

#### 2. **Configurazione Hotel**
```python
HOTEL_CONFIG = {
    'name': 'Il Tuo Hotel',
    'total_rooms': 50,
    'room_prefix': '1'
}
```

#### 3. **Configurazione Email** (opzionale)
Per ricevere report giornalieri via email:
- Server SMTP
- Porta (465 SSL o 587 TLS)
- Email mittente
- Password

### Comandi PBX Personalizzati

Se usi un PBX diverso da Asterisk, modifica i comandi in `pbx_connection.py`:

```python
# Asterisk (default)
command = f"asterisk -rx 'originate Local/{extension}@internal'"

# Altri PBX - Adatta secondo necessità
```

---

## 🚀 Utilizzo

### Avvio Applicazione

```bash
python main.py
```

### Workflow Tipico

#### 1. **Configura Camere**
   - Menu → Gestione → Gestisci Camere
   - Aggiungi/modifica camere
   - Imposta numero camera e interno telefonico

#### 2. **Carica Messaggi Audio**
   - Menu → Gestione → Gestisci Messaggi Audio
   - Carica file MP3/WAV/OGG
   - Seleziona lingua e tipo azione:
     - Messaggio Sveglia
     - Conferma Riprogrammazione
     - Saluto

#### 3. **Programma Sveglia**
   - Schermata principale
   - Seleziona camera
   - Imposta data e ora
   - Scegli messaggio audio
   - Clicca "Programma Sveglia"

#### 4. **Monitora Esecuzione**
   - Visualizza sveglie attive nella lista principale
   - Controlla stato: Programmata, In Esecuzione, Completata
   - Modifica o elimina sveglie programmate

---

## 🎛️ Funzionalità

### Menu File
- **Impostazioni**: Configurazione completa sistema
- **Esci**: Chiudi applicazione

### Menu Gestione
- **Test Connessione PBX**: Verifica connessione al centralino
- **Gestisci Camere**: CRUD completo camere hotel
- **Gestisci Messaggi Audio**: Upload e gestione messaggi
- **Visualizza Log**: Log viewer con filtri avanzati
- **Monitor di Sistema**: Dashboard monitoraggio real-time
- **Backup e Ripristino**: Gestione backup completa

### Menu Aiuto
- **Informazioni**: Dettagli versione e crediti

---

## 🏗️ Architettura

### Struttura File

```
sveglia_centralino/
├── main.py                 # Applicazione principale
├── config.py              # Configurazioni
├── database.py            # Gestione database SQLite
├── pbx_connection.py      # Connessione PBX via SSH
├── alarm_manager.py       # Gestione sveglie (thread)
├── room_manager.py        # Gestione camere
├── audio_manager.py       # Gestione messaggi audio
├── settings.py            # Finestra impostazioni
├── log_viewer.py          # Visualizzatore log
├── system_monitor.py      # Monitor sistema
├── backup_manager.py      # Backup/ripristino
├── logger.py              # Sistema logging
├── requirements.txt       # Dipendenze Python
├── sveglie.db            # Database SQLite
├── audio_messages/        # Cartella messaggi audio
├── logs/                  # Cartella log
└── backup/                # Cartella backup
```

### Database Schema

```sql
-- Tabella Camere
CREATE TABLE rooms (
    id INTEGER PRIMARY KEY,
    room_number TEXT UNIQUE,
    phone_extension TEXT,      -- Interno telefonico
    status TEXT,               -- available, occupied, maintenance
    color TEXT,                -- Colore personalizzato
    label TEXT,                -- Etichetta/note
    created_at TIMESTAMP
);

-- Tabella Messaggi Audio
CREATE TABLE audio_messages (
    id INTEGER PRIMARY KEY,
    name TEXT,
    file_path TEXT,
    duration REAL,
    category TEXT,             -- standard, emergency, promotional
    language TEXT,             -- it, en, fr, de, es, ...
    action_type TEXT,          -- wake_up, snooze_confirm, goodbye
    created_at TIMESTAMP
);

-- Tabella Sveglie
CREATE TABLE alarms (
    id INTEGER PRIMARY KEY,
    room_number TEXT,
    alarm_time TIMESTAMP,
    audio_message_id INTEGER,
    status TEXT,               -- scheduled, executing, completed, snoozed
    snooze_count INTEGER,
    last_snooze_time TIMESTAMP,
    created_at TIMESTAMP,
    FOREIGN KEY (audio_message_id) REFERENCES audio_messages(id)
);

-- Tabella Log Chiamate
CREATE TABLE call_logs (
    id INTEGER PRIMARY KEY,
    alarm_id INTEGER,
    room_number TEXT,
    call_time TIMESTAMP,
    response TEXT,             -- answered, no_answer, busy
    snooze_minutes INTEGER,
    status TEXT,
    FOREIGN KEY (alarm_id) REFERENCES alarms(id)
);
```

### Flusso Sveglia

```
1. Sistema controlla sveglie programmate (ogni 30s)
   └─> Alarm Manager Thread

2. Quando è l'ora della sveglia:
   └─> Recupera interno telefonico camera
   └─> Connessione SSH al PBX
   └─> Esegue comando chiamata: originate Local/{interno}@internal

3. Cliente risponde:
   └─> Riproduce messaggio audio nella lingua impostata
   └─> Attende input DTMF (tastiera telefono)

4. Cliente può:
   a) Premere 1: Conferma sveglia
      └─> Riproduce "Saluto"
      └─> Termina chiamata
      └─> Marca sveglia come "completata"
   
   b) Premere 2,3,4,5: Posticipa (5,10,15,30 min)
      └─> Riproduce "Conferma Riprogrammazione"
      └─> Riprogramma sveglia
      └─> Riproduce "Saluto"
      └─> Termina chiamata
      └─> Marca sveglia come "snoozed"

5. Log completo operazione salvato nel database
```

---

## ❓ FAQ

### Come configuro il mio PBX?

Modifica `config.py` con i dati del tuo centralino. Assicurati che:
- L'IP del PBX sia raggiungibile dalla rete
- SSH sia abilitato sul PBX
- Hai credenziali con permessi per eseguire comandi

### Quali formati audio sono supportati?

- MP3 (consigliato)
- WAV
- OGG

**Nota**: Verifica che il tuo PBX supporti il formato scelto.

### Posso usare l'app senza PBX?

Sì, per test e configurazione. L'app si avvierà anche senza PBX connesso,
ma ovviamente non potrà effettuare chiamate reali.

### Come faccio backup?

Menu → Gestione → Backup e Ripristino
- Backup automatico di database, audio, log
- Ripristino completo o selettivo
- Export ZIP con metadati

### Quante camere supporta?

Il sistema supporta un numero illimitato di camere. Di default sono
precaricate 50 camere (101-150), ma puoi aggiungerne quante ne vuoi.

### Come aggiungo altre lingue?

Le lingue sono già configurate nel sistema. Basta caricare messaggi
audio nella lingua desiderata e selezionare la lingua corretta durante
l'upload.

---

## 🐛 Risoluzione Problemi

### Errore: "Timeout connessione PBX"

**Causa**: IP/credenziali PBX errate o PBX non raggiungibile

**Soluzione**:
1. Verifica IP in `config.py`
2. Testa connessione: Menu → Gestione → Test Connessione PBX
3. Verifica firewall/rete
4. Controlla che SSH sia abilitato sul PBX

### Errore: "File audio non trovato"

**Causa**: File audio spostato o eliminato

**Soluzione**:
1. Verifica che la cartella `audio_messages/` esista
2. Ricarica il file audio tramite l'interfaccia
3. Controlla i permessi della cartella

### Sveglia non si attiva

**Causa**: Problema con il comando PBX o interno errato

**Soluzione**:
1. Verifica interno telefonico in Gestione Camere
2. Controlla log: Menu → Gestione → Visualizza Log
3. Testa comando manualmente via SSH al PBX
4. Verifica che l'interno esista nel PBX

---

## 📞 Supporto

### Documentazione Completa
Vedi `VERSIONE_1.0_RECAP.md` per dettagli tecnici completi.

### Report Bug
Apri una issue su GitHub: [github.com/alcodestudio2025/sveglia_centralino/issues](https://github.com/alcodestudio2025/sveglia_centralino/issues)

### Contributi
Pull requests sono benvenuti! Per modifiche importanti, apri prima una issue per discutere le modifiche proposte.

---

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi file `LICENSE` per dettagli.

---

## 🙏 Crediti

Sviluppato da **AlcoDe Studio 2025**

### Tecnologie Utilizzate
- Python 3
- Tkinter (GUI)
- Paramiko (SSH)
- SQLite (Database)
- Psutil (System Monitoring)

---

## 🗺️ Roadmap

### v1.0 (Current)
- ✅ Core features complete
- ✅ PBX integration
- ✅ Multi-language support
- ✅ Backup system
- ⏳ Email reports
- ⏳ Complete audio integration

### v2.0 (Future)
- 📱 Web dashboard
- 📊 Advanced analytics
- 🌐 Multi-hotel support
- 🤖 AI optimization
- 📅 Calendar integration
- 🔌 REST API

---

**Versione**: 1.0-beta  
**Ultimo Aggiornamento**: 2025-01-XX  
**Python Version**: 3.8+

---

<p align="center">
  Made with ❤️ for Hotels
</p>
