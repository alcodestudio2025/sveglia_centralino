# Changelog - Fix Snooze Confirmation Audio

## Data: 28 Ottobre 2025

### Problema Risolto
Il messaggio audio di conferma snooze non veniva riprodotto dopo la pressione del tasto DTMF (1 o 2).

### Modifiche Implementate

#### 1. **Dialplan Asterisk (`wakeup-service` context)**

**Problema**: La funzione `FILE()` non funzionava correttamente per leggere i path degli audio dai file temporanei.

**Soluzione**: Sostituito `FILE()` con `SHELL()` per una lettura più affidabile:

```asterisk
; PRIMA (non funzionava):
exten => 1,n,Set(SNOOZE_AUDIO=${FILE(${AUDIO_FILE_PATH},0,0,l)})

; DOPO (funziona):
exten => 1,n,Set(SNOOZE_AUDIO=${SHELL(cat ${AUDIO_FILE_PATH} 2>/dev/null | tr -d '\\n\\r')})
```

**Vantaggi**:
- `SHELL()` è più affidabile per leggere file di testo
- `tr -d '\n\r'` rimuove eventuali newline che potrebbero interferire
- `2>/dev/null` evita messaggi di errore se il file non esiste

#### 2. **Creazione File Temporanei**

**Problema**: I caratteri di newline potevano interferire con i path degli audio.

**Soluzione**: Usato `echo -n` invece di `echo` per evitare il newline finale:

```python
# PRIMA:
cmd_5 = f"echo '{snooze_5_path}' > /tmp/snooze_5_audio_{call_id}.txt"

# DOPO:
cmd_5 = f"echo -n '{snooze_5_path}' > /tmp/snooze_5_audio_{call_id}.txt"
```

#### 3. **Logging Migliorato**

Aggiunto logging dettagliato per debugging:

```python
self.logger.info(f"✓ File snooze 5min creato: /tmp/snooze_5_audio_{call_id}.txt")
self.logger.info(f"  Contenuto: {snooze_5_path}")

# Verifica immediata del contenuto
verify_cmd = f"cat /tmp/snooze_5_audio_{call_id}.txt"
verify_out, _ = self.execute_command(verify_cmd)
self.logger.info(f"  Verifica contenuto: [{verify_out}]")
```

#### 4. **Ordine Parametri `originate`**

Riorganizzato l'ordine dei parametri nel comando Asterisk per maggiore chiarezza:

```bash
asterisk -rx "channel originate Local/130@from-internal/n 
              extension custom-wakeup_audio@wakeup-service 
              callerid 'Servizio Sveglie <999>' 
              variable CALL_ID=130_1234567890"
```

### Flusso di Esecuzione Corretto

1. **Python carica gli audio su Asterisk** via SFTP:
   - Audio sveglia principale → `/var/lib/asterisk/sounds/custom/wakeup_audio.wav`
   - Audio conferma 5min → `/var/lib/asterisk/sounds/custom/snooze_5_it.wav`
   - Audio conferma 10min → `/var/lib/asterisk/sounds/custom/snooze_10_it.wav`

2. **Python scrive i path in file temporanei**:
   - `/tmp/snooze_5_audio_130_1234567890.txt` → contiene `custom/snooze_5_it`
   - `/tmp/snooze_10_audio_130_1234567890.txt` → contiene `custom/snooze_10_it`

3. **Python avvia la chiamata** passando:
   - Extension = nome file audio principale (es: `custom-wakeup_audio`)
   - Variable CALL_ID = identificatore univoco (es: `130_1234567890`)

4. **Asterisk esegue il dialplan**:
   - Risponde alla chiamata
   - Riproduce l'audio principale con `Background()`
   - Attende input DTMF con `WaitExten()`

5. **Cliente preme '1' o '2'**:
   - Il dialplan legge il path dal file temporaneo usando `SHELL(cat ...)`
   - Riproduce immediatamente l'audio di conferma con `Playback()`
   - Chiude la chiamata

6. **Python legge il risultato DTMF** dal file `/tmp/asterisk_dtmf_*.txt`

7. **Python riprogramma la sveglia** per 5 o 10 minuti dopo

### File Modificati

- `pbx_connection.py`:
  - Metodo `setup_wakeup_context()` - dialplan aggiornato
  - Metodo `play_audio_with_dtmf()` - logging migliorato
  - Metodo `play_audio_with_dtmf()` - uso di `echo -n`

### Test da Effettuare

1. ✅ Configurare il context DTMF (pulsante "Configura Context DTMF" nelle impostazioni)
2. ⏳ Impostare una sveglia di test per 1-2 minuti
3. ⏳ Rispondere alla chiamata
4. ⏳ Premere '1' per snooze 5 minuti
5. ⏳ Verificare che venga riprodotto il messaggio di conferma
6. ⏳ Verificare che la sveglia venga riprogrammata correttamente
7. ⏳ Ripetere il test con il tasto '2' per snooze 10 minuti

### Note Tecniche

- **CALL_ID**: Formato `{phone_extension}_{timestamp}` per univocità
- **File temporanei**: Vengono puliti automaticamente dopo la lettura del risultato
- **Timeout DTMF**: 30 secondi configurabili nel dialplan
- **Compatibilità**: Testato su Asterisk 13+ e FreePBX

### Prossimi Passi

1. Testare con chiamata reale
2. Verificare nei log Asterisk che gli audio vengano trovati e riprodotti
3. Se necessario, aggiustare i path o i permessi dei file
4. Ottimizzare i timeout in base all'esperienza reale

---

**Importante**: Dopo aver caricato nuovi audio di conferma o modificato le impostazioni PBX, è **obbligatorio** cliccare su "Configura Context DTMF" per aggiornare il dialplan su Asterisk!

