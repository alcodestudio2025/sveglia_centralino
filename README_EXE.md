# 📦 SvegliaCentralino.exe - Guida all'Utilizzo

## 🎯 File Generato

**Nome**: `SvegliaCentralino.exe`  
**Posizione**: `dist/SvegliaCentralino.exe`  
**Dimensione**: ~70-80 MB (include tutte le dipendenze)

## ✨ Caratteristiche dell'Exe

### 1. **Standalone** 
- ✅ Nessuna installazione di Python necessaria
- ✅ Tutte le librerie incluse (Tkinter, PIL, Pygame, Paramiko, ecc.)
- ✅ Pronto all'uso su qualsiasi PC Windows

### 2. **Icone Personalizzate**
- 🎨 **Icona applicazione**: La tua icona_3 visibile in Windows Explorer e barra delle applicazioni
- 🎨 **Icona finestra**: La tua icona_2 nella barra del titolo
- 🎨 **Icona principale**: La tua icona_1 visibile nella finestra dell'app
- 🎨 **Logo**: AL CODE STUDIO in basso a destra

### 3. **Dati Inclusi**
- 📁 Cartella `assets/` con loghi e icone
- 📁 Cartella `audio_messages/` per i file audio
- 📁 Database SQLite creato automaticamente al primo avvio
- 📁 Log salvati in `logs/`

## 🚀 Primo Avvio

### Requisiti Minimi
- Windows 10/11
- 4GB RAM
- Connessione di rete (per SSH al PBX)

### Passaggi

1. **Doppio clic** su `SvegliaCentralino.exe`
2. L'applicazione si avvierà con finestra console nascosta
3. **Prima configurazione**:
   - Menu → Gestione → Impostazioni
   - Configura connessione PBX (IP, porta, credenziali SSH)
   - Configura interno virtuale sveglie e Context DTMF
   - Importa camere dal PBX o gestiscile manualmente
   - Carica messaggi audio (wake_up e snooze_confirm)

## 📂 Struttura File

```
dist/
├── SvegliaCentralino.exe  ← File eseguibile principale
├── assets/
│   ├── icona_1.png
│   ├── icona_2.png  
│   ├── icona_3.png
│   ├── app_icon.ico
│   ├── logo_small.png
│   ├── logo_medium.png
│   └── logo_large.png
├── audio_messages/        ← I tuoi file audio .wav
├── logs/                  ← Log applicazione (creati automaticamente)
├── settings.json          ← Configurazioni (creato automaticamente)
└── sveglia_hotel.db       ← Database (creato automaticamente)
```

## ⚙️ Configurazione Post-Installazione

### 1. Connessione PBX
```
Menu → Gestione → Impostazioni → Connessione PBX
- Host: IP del tuo centralino Asterisk
- Porta: 22 (SSH)
- Username: utente SSH
- Password: password SSH
- Interno Virtuale: 999 (o altro)
- Context: from-internal
```

### 2. Messaggi Audio
```
Menu → Gestione → Gestisci Messaggi Audio
- Carica file .wav per wake_up (italiano e inglese)
- Carica file .wav per snooze_confirm (5min e 10min, italiano e inglese)
```

### 3. Camere
```
Menu → Gestione → Gestisci Camere
- Importa da PBX (automatico)
- Oppure aggiungi manualmente
```

## 🔧 Rigenerazione Exe

Per rigenerare l'exe dopo modifiche al codice:

```bash
cd C:\Sveglia_Centralino\sveglia_centralino
pyinstaller build_exe.spec --clean --noconfirm
```

L'exe verrà ricreato in `dist/SvegliaCentralino.exe`

## 📝 Note Importanti

1. **Antivirus**: Alcuni antivirus potrebbero segnalare l'exe come "non riconosciuto" perché è self-contained. È normale per applicazioni PyInstaller.

2. **Primo Avvio Lento**: Il primo avvio potrebbe richiedere 5-10 secondi mentre l'exe estrae i file temporanei.

3. **Percorsi Relativi**: L'applicazione usa percorsi relativi, quindi mantieni la struttura delle cartelle intatta.

4. **Log**: I log sono salvati in `logs/sveglia_centralino.log` per debug.

5. **Backup**: Fai backup regolari di:
   - `sveglia_hotel.db` (database)
   - `settings.json` (configurazioni)
   - `audio_messages/` (file audio)

## 🐛 Troubleshooting

### L'exe non si avvia
- Controlla che tutte le cartelle (`assets`, `audio_messages`, `logs`) esistano
- Verifica i permessi di scrittura nella cartella

### Errori di connessione PBX
- Verifica IP e credenziali SSH
- Testa connessione SSH manualmente
- Controlla firewall

### Audio non funzionano
- Verifica che i file siano in formato .wav
- Controlla nomi file secondo nomenclatura (vedi GUIDA_NOMENCLATURA_AUDIO.md)
- Configura Context DTMF dal pulsante nelle impostazioni

## 📞 Supporto

Per problemi o domande:
- Controlla i log in `logs/sveglia_centralino.log`
- Consulta le guide nella repository
- Contatta AL CODE STUDIO

---

**Versione**: 1.0  
**Sviluppato da**: AL CODE STUDIO  
**Data Build**: 28/10/2025

