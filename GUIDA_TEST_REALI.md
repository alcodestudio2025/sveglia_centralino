# 🧪 GUIDA TEST REALI - Sistema Gestione Sveglie Hotel v1.0

## 📦 PREPARAZIONE TEST

### File Generato
✅ `SvegliaHotel_v1.0.zip` (15.8 MB)

### Contenuto Package
```
SvegliaHotel_v1.0/
├── SvegliaHotel.exe          # Eseguibile (16 MB)
├── AVVIA.bat                  # Launcher con verifica config
├── config.example.py          # Template configurazione
├── GUIDA_RAPIDA.txt          # Quick start guide
├── README.md                  # Documentazione completa
├── audio_messages/            # Cartella messaggi audio
├── logs/                      # Cartella log
└── backup/                    # Cartella backup
```

---

## 🚀 FASE 1: SETUP AMBIENTE TEST

### 1.1 Estrazione Package
```bash
# Windows
1. Estrai SvegliaHotel_v1.0.zip in una cartella
2. Apri la cartella estratta
```

### 1.2 Configurazione PBX
```bash
1. Copia config.example.py -> config.py
2. Modifica config.py con dati PBX reali:
```

```python
PBX_CONFIG = {
    'host': '192.168.X.XXX',      # IP REALE del centralino
    'port': 22,
    'username': 'admin',           # Username SSH REALE
    'password': 'TUA_PASSWORD',    # Password SSH REALE
    'timeout': 10
}
```

### 1.3 Verifica Rete
```bash
# Testa raggiungibilità PBX
ping 192.168.X.XXX

# Testa SSH manualmente
ssh admin@192.168.X.XXX
```

---

## 🧪 FASE 2: TEST FUNZIONALI

### 2.1 Test Avvio Applicazione

**Obiettivo**: Verificare che l'app si avvii correttamente

**Steps:**
1. Doppio click su `AVVIA.bat` oppure `SvegliaHotel.exe`
2. Verificare che l'interfaccia si apra
3. Controllare barra di stato (in basso)

**Expected:**
- ✅ Finestra principale si apre
- ✅ Nessun errore critico
- ⚠️ Possibile warning timeout PBX (normale se non configurato)

**Logs:**
- `logs/sveglia_centralino.log`

---

### 2.2 Test Connessione PBX

**Obiettivo**: Verificare connessione SSH al centralino

**Steps:**
1. Menu → Gestione → Test Connessione PBX
2. Attendere risposta
3. Verificare messaggio di conferma

**Expected:**
- ✅ "Connessione PBX riuscita!"
- ❌ Se fallisce: verificare config.py e rete

**Troubleshooting:**
```
Errore                        | Soluzione
------------------------------|----------------------------------
"Timeout"                     | Verifica IP e rete
"Authentication failed"       | Verifica username/password
"Connection refused"          | Verifica che SSH sia abilitato
"Host unreachable"            | Verifica firewall e routing
```

---

### 2.3 Test Gestione Camere

**Obiettivo**: Verificare CRUD camere

**Steps:**
1. Menu → Gestione → Gestisci Camere
2. Verificare che le 50 camere siano caricate (101-150)
3. Modifica camera 101:
   - Interno telefonico: 2101
   - Status: occupied
   - Colore: rosso
   - Salva
4. Verifica che le modifiche siano salvate
5. Aggiungi nuova camera 201
6. Elimina camera test

**Expected:**
- ✅ Lista camere visibile
- ✅ Modifiche salvate
- ✅ Aggiunta/eliminazione funzionante

---

### 2.4 Test Gestione Audio

**Obiettivo**: Caricare e gestire messaggi audio

**Steps:**
1. Menu → Gestione → Gestisci Messaggi Audio
2. Prepara 3 file MP3:
   - `sveglia_it.mp3` (Messaggio sveglia IT)
   - `conferma_it.mp3` (Conferma riprogrammazione IT)
   - `saluto_it.mp3` (Saluto IT)
3. Carica ogni file:
   - Nome descrittivo
   - Seleziona lingua (IT)
   - Seleziona azione corretta
   - Categoria: standard
4. Verifica che appaiano nella lista
5. Test riproduzione (se implementata)

**Expected:**
- ✅ Upload file funzionante
- ✅ File copiati in audio_messages/
- ✅ Visibili nella lista

**File Audio Test:**
```
Tipo                | Contenuto Esempio
--------------------|--------------------------------
Messaggio Sveglia   | "Buongiorno, sono le 08:00..."
Conferma Snooze     | "Sveglia posticipata alle 08:15"
Saluto              | "Buona giornata!"
```

---

### 2.5 Test Programmazione Sveglia

**Obiettivo**: Programmare una sveglia di test

**Steps:**
1. Schermata principale
2. Seleziona camera 101
3. Imposta ora: +2 minuti da ora attuale
4. Seleziona messaggio "Messaggio Sveglia IT"
5. Clicca "Programma Sveglia"
6. Verifica che appaia nella lista "Sveglie Programmate"

**Expected:**
- ✅ Sveglia aggiunta al database
- ✅ Visibile nella lista con status "Programmata"
- ✅ Countdown visibile

---

### 2.6 Test Esecuzione Sveglia (CRITICO)

**Obiettivo**: Test chiamata reale al centralino

⚠️ **ATTENZIONE**: Questo test effettua una chiamata REALE

**Prerequisiti:**
- Centralino PBX raggiungibile
- Interno 2101 configurato e esistente
- Telefono camera 101 disponibile

**Steps:**
1. Programma sveglia camera 101 tra 1 minuto
2. Attendi esecuzione
3. Rispondi al telefono camera 101
4. Ascolta messaggio audio
5. (Se implementato) Prova DTMF snooze

**Expected:**
- ✅ Chiamata parte al momento giusto
- ✅ Telefono squilla
- ✅ Messaggio audio riprodotto
- ✅ Status sveglia aggiornato a "Completata"

**Verifica Logs:**
```bash
# Controlla logs/sveglia_centralino.log
INFO - Sveglia eseguita per camera 101 (interno 2101)
INFO - Chiamata effettuata all'interno 2101
INFO - Sveglia ID:X completata
```

**Troubleshooting:**
```
Problema                    | Causa Probabile           | Soluzione
----------------------------|---------------------------|------------------------
Chiamata non parte          | Comando PBX errato       | Verifica pbx_connection.py
Telefono non squilla        | Interno errato           | Verifica interno in Gestisci Camere
Audio non si sente          | File non trovato         | Verifica path audio
Chiamata cade subito        | Timeout PBX              | Aumenta timeout in config.py
```

---

### 2.7 Test Snooze (Se Implementato)

**Obiettivo**: Testare posticipo sveglia

**Steps:**
1. Programma sveglia
2. Quando squilla, premi tasto DTMF:
   - 2 = snooze 5 min
   - 3 = snooze 10 min
   - 4 = snooze 15 min
   - 5 = snooze 30 min
3. Verifica che sveglia sia riprogrammata
4. Verifica messaggio "Conferma Riprogrammazione"

**Expected:**
- ✅ DTMF riconosciuto
- ✅ Sveglia riprogrammata
- ✅ Status "Snoozed"
- ✅ Nuova chiamata dopo tempo snooze

---

### 2.8 Test Monitor Sistema

**Obiettivo**: Verificare monitoring real-time

**Steps:**
1. Menu → Gestione → Monitor di Sistema
2. Verifica tutti i 5 tab:
   - Sistema: CPU, RAM visibili
   - Database: Statistiche corrette
   - PBX: Stato connessione
   - Sveglie: Contatori aggiornati
   - Performance: Metriche real-time
3. Lascia aperto durante esecuzione sveglia
4. Verifica aggiornamento real-time

**Expected:**
- ✅ Dati visualizzati correttamente
- ✅ Aggiornamento ogni 2 secondi
- ✅ Statistiche accurate

---

### 2.9 Test Backup/Ripristino

**Obiettivo**: Verificare sistema backup

**Steps:**
1. Menu → Gestione → Backup e Ripristino
2. Tab "Crea Backup"
3. Seleziona tutto
4. Scegli percorso
5. Crea backup
6. Verifica file ZIP creato
7. Tab "Gestione Backup"
8. Verifica backup nella lista

**Expected:**
- ✅ Backup creato
- ✅ ZIP contiene tutti i file
- ✅ Metadati corretti

**Test Ripristino** (opzionale):
1. Modifica qualche dato
2. Ripristina backup precedente
3. Verifica che dati tornino allo stato originale

---

### 2.10 Test Log Viewer

**Obiettivo**: Verificare visualizzazione log

**Steps:**
1. Menu → Gestione → Visualizza Log
2. Filtra per livello: ERROR
3. Cerca testo: "sveglia"
4. Attiva auto-refresh
5. Genera eventi (programma sveglie)
6. Verifica aggiornamento log in real-time

**Expected:**
- ✅ Log visibili con colori
- ✅ Filtri funzionanti
- ✅ Ricerca funzionante
- ✅ Auto-refresh attivo

---

## 📊 FASE 3: TEST DI CARICO

### 3.1 Test Multiple Sveglie

**Obiettivo**: Verificare gestione sveglie simultanee

**Steps:**
1. Programma 10 sveglie per 10 camere diverse
2. Tutte con orario ravvicinato (1-2 minuti differenza)
3. Verifica esecuzione sequenziale
4. Controlla CPU e memoria (Monitor Sistema)

**Expected:**
- ✅ Tutte le sveglie eseguite
- ✅ Nessun crash
- ✅ Performance accettabili

---

### 3.2 Test Stress Database

**Obiettivo**: Verificare performance con molti dati

**Steps:**
1. Aggiungi 100+ camere
2. Carica 50+ messaggi audio
3. Programma 50+ sveglie
4. Verifica tempi di risposta interfaccia
5. Verifica dimensione database

**Expected:**
- ✅ UI reattiva
- ✅ Query veloci
- ✅ Database sotto 100MB

---

## 🐛 FASE 4: TEST ERRORI

### 4.1 Test Disconnessione PBX

**Obiettivo**: Gestione perdita connessione

**Steps:**
1. Durante una sveglia attiva
2. Disconnetti rete/spegni PBX
3. Verifica comportamento app

**Expected:**
- ✅ Errore loggato
- ✅ App non crasha
- ✅ Retry automatico (se implementato)

---

### 4.2 Test File Mancanti

**Obiettivo**: Gestione file audio mancanti

**Steps:**
1. Programma sveglia con messaggio audio
2. Elimina file audio da audio_messages/
3. Attendi esecuzione sveglia

**Expected:**
- ✅ Errore gestito gracefully
- ✅ Log errore chiaro
- ✅ Sveglia marcata come "failed"

---

### 4.3 Test Camera Inesistente

**Obiettivo**: Gestione interno inesistente nel PBX

**Steps:**
1. Programma sveglia per interno 9999 (non esistente)
2. Attendi esecuzione

**Expected:**
- ✅ Chiamata fallisce
- ✅ Errore loggato
- ✅ Status "failed"

---

## 📝 FASE 5: DOCUMENTAZIONE TEST

### 5.1 Report Test
Compila per ogni test:

```markdown
## Test: [Nome Test]
**Data**: 2025-XX-XX
**Tester**: [Nome]
**Versione**: 1.0

### Risultato
- [ ] PASS
- [ ] FAIL
- [ ] PARTIAL

### Note
[Osservazioni, screenshot, log rilevanti]

### Issues Trovati
1. [Descrizione issue]
2. ...

### Suggerimenti
[Miglioramenti proposti]
```

---

### 5.2 Log Test
Salva i log di ogni test:
```bash
logs/
├── test_01_avvio_2025-XX-XX.log
├── test_02_pbx_2025-XX-XX.log
├── test_06_esecuzione_sveglia_2025-XX-XX.log
└── ...
```

---

### 5.3 Screenshots
Cattura screenshot per:
- Interfaccia principale
- Ogni finestra di gestione
- Messaggi di errore
- Monitor sistema durante esecuzione

---

## ✅ CHECKLIST FINALE PRE-PRODUZIONE

Prima di dichiarare il sistema "Production Ready":

### Funzionalità
- [ ] Connessione PBX testata con successo
- [ ] Chiamate reali eseguite correttamente
- [ ] Audio riprodotto su telefono
- [ ] Snooze funzionante (se implementato)
- [ ] Tutti i CRUD testati e funzionanti
- [ ] Backup/ripristino testati

### Stabilità
- [ ] Nessun crash durante test
- [ ] Gestione errori robusta
- [ ] Log completi e informativi
- [ ] Performance accettabili sotto carico

### Sicurezza
- [ ] Password PBX non in chiaro nel log
- [ ] Backup configurazioni sensibili
- [ ] Permessi file corretti

### Documentazione
- [ ] README aggiornato
- [ ] GUIDA_RAPIDA completa
- [ ] FAQ con problemi comuni
- [ ] Comandi PBX documentati

---

## 🚀 GO/NO-GO DECISION

### GO (Ready for Production)
Se **TUTTI** questi criteri sono soddisfatti:
- ✅ 100% test core passati
- ✅ Chiamata PBX funzionante
- ✅ Audio riprodotto correttamente
- ✅ Zero crash durante test
- ✅ Documentazione completa

### NO-GO (Needs More Work)
Se **UNO** di questi è presente:
- ❌ Chiamate PBX falliscono
- ❌ Crash frequenti
- ❌ Audio non si sente
- ❌ Dati persi durante uso

---

## 📞 SUPPORTO DURANTE TEST

### Dove Riportare Issues
- GitHub Issues: [Link repo]
- Email: support@alcodestudio.com
- Log: Sempre allegare `logs/sveglia_centralino.log`

### Informazioni da Includere
```
Sistema Operativo: Windows X
Versione App: 1.0
PBX Model: [Asterisk/FreePBX/Altro]
PBX Version: [X.X]
Descrizione Problema:
Steps per Riprodurre:
Log Rilevanti:
Screenshots:
```

---

## 🎉 NEXT STEPS DOPO TEST

1. **Se test OK:**
   - Distribuisci a hotel pilota
   - Formazione staff
   - Monitoring primo mese

2. **Se test FAIL:**
   - Analizza log
   - Fix issues critici
   - Nuovo ciclo test

3. **Post-Deployment:**
   - Feedback utenti
   - Ottimizzazioni
   - Pianifica v2.0

---

**Buon Testing! 🚀**

*Documento creato: 2025-01-XX*
*Versione: 1.0*

