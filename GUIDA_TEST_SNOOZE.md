# Guida al Test dello Snooze con Conferma Audio

## ⚠️ IMPORTANTE - Prima di Testare

### 1. Riconfigura il Context DTMF
**OBBLIGATORIO**: Ogni volta che modifichi gli audio o le impostazioni PBX:

1. Apri l'applicazione
2. Vai su **Gestione → Impostazioni**
3. Nella tab **"Connessione PBX"**
4. Clicca su **"Configura Context DTMF"**
5. Attendi la conferma di successo

Questo aggiorna il dialplan su Asterisk con la nuova logica SHELL() per leggere gli audio.

---

## 📋 Checklist Pre-Test

- [ ] Audio sveglia principale caricato (action: `wake_up`)
- [ ] Audio conferma 5min caricato (action: `snooze_confirm`, nome contiene "5")
- [ ] Audio conferma 10min caricato (action: `snooze_confirm`, nome contiene "10")
- [ ] Lingue impostate correttamente per ogni audio
- [ ] Lingua camera corrispondente agli audio disponibili
- [ ] Context DTMF riconfigurato (pulsante nelle impostazioni)
- [ ] Connessione PBX attiva e testata

---

## 🧪 Procedura di Test

### Test 1: Snooze 5 Minuti

1. **Imposta Sveglia**:
   - Camera: Scegli una camera con interno valido
   - Ora: Tra 1-2 minuti da ora corrente
   - Lingua: Scegli lingua degli audio caricati (es. IT o EN)

2. **Attendi la Chiamata**:
   - L'interno dovrebbe squillare
   - Sul display dovrebbe apparire "Servizio Sveglie" o l'interno configurato (999)

3. **Rispondi e Ascolta**:
   - Rispondi alla chiamata
   - Dovresti sentire il messaggio audio principale

4. **Premi '1'**:
   - Durante o dopo l'audio, premi il tasto **1**
   - **Immediatamente** dovresti sentire: "La sveglia è stata posticipata di 5 minuti"
   - La chiamata si chiude automaticamente

5. **Verifica**:
   - Controlla che sia stata creata una nuova sveglia tra 5 minuti
   - Attendi la nuova chiamata per confermare il funzionamento

### Test 2: Snooze 10 Minuti

1. Ripeti la procedura del Test 1
2. Al punto 4, premi il tasto **2** invece dell'1
3. Dovresti sentire: "La sveglia è stata posticipata di 10 minuti"

### Test 3: Nessuno Snooze

1. Ripeti la procedura del Test 1
2. **Non premere nessun tasto** (o riaggancia)
3. Dopo 30 secondi la chiamata si chiude
4. La sveglia viene segnata come "completed" senza riprogrammazione

---

## 🔍 Cosa Controllare nei Log

### Log Applicazione (logs/alarm_manager.log)

Dovresti vedere:
```
============================================================
SVEGLIA CON SNOOZE - Camera 101 - Interno 130 - Lingua: IT
============================================================
Audio conferma 5min: C:\...\snooze_5_it.wav
Audio conferma 10min: C:\...\snooze_10_it.wav
Avvio chiamata con audio, DTMF e conferma...
✓ DTMF '1' ricevuto - Snooze 5 minuti (conferma già riprodotta)
Riprogrammazione sveglia per 11:25
✓ Sveglia riprogrammata con successo
```

### Log PBX (logs/pbx_connection.log)

Dovresti vedere:
```
Upload audio sveglia: C:\...\wakeup_audio.wav
Upload audio conferma 5min: C:\...\snooze_5_it.wav
✓ Conferma 5min: custom/snooze_5_it
✓ File snooze 5min creato: /tmp/snooze_5_audio_130_1730123456.txt
  Contenuto: custom/snooze_5_it
  Verifica contenuto: [custom/snooze_5_it]
Chiamata con DTMF a 130: custom/wakeup_audio
✓ Chiamata avviata verso wakeup-service
✓ DTMF ricevuto: 1
```

### Log Asterisk (CLI o /var/log/asterisk/full)

Dovresti vedere (accedi via SSH):
```bash
ssh admin@192.168.1.100
tail -f /var/log/asterisk/full
```

Cerca:
```
NoOp(=== SVEGLIA CON SNOOZE ===)
NoOp(Audio extension: custom-wakeup_audio)
NoOp(Call ID: 130_1730123456)
NoOp(Audio file path: custom/wakeup_audio)
Background(custom/wakeup_audio)
NoOp(DTMF 1 ricevuto - Snooze 5 min)
NoOp(Cerco file: /tmp/snooze_5_audio_130_1730123456.txt)
NoOp(Audio letto: [custom/snooze_5_it])
NoOp(Riproduzione conferma: custom/snooze_5_it)
Playback(custom/snooze_5_it)
```

---

## ❌ Problemi Comuni e Soluzioni

### Problema: Nessuna Chiamata Ricevuta

**Soluzione**:
1. Verifica connessione PBX nelle impostazioni
2. Testa con "Test Connessione"
3. Controlla che l'interno telefonico sia corretto
4. Verifica nei log: `logs/pbx_connection.log`

### Problema: Chiamata Arriva ma Non Si Sente Nulla

**Soluzione**:
1. Verifica che l'audio sia in formato WAV/GSM compatibile Asterisk
2. Controlla nei log Asterisk se trova il file: `asterisk -rx "core show file formats"`
3. Ricarica il file audio:
   - Gestione → Audio/Messaggi
   - Elimina e ricarica

### Problema: Audio Sveglia OK, ma NO Audio Conferma

**Soluzione**:
1. **Ricontrolla la nomenclatura dei file**:
   - Il nome deve contenere "5" per 5 minuti
   - Il nome deve contenere "10" per 10 minuti
2. **Verifica action_type** in Gestione Audio:
   - Deve essere `snooze_confirm` (non `wake_up`)
3. **Verifica lingua**:
   - Lingua audio deve corrispondere a lingua camera
4. **Riconfiura Context**:
   - Gestione → Impostazioni → "Configura Context DTMF"

### Problema: DTMF Non Viene Rilevato

**Soluzione**:
1. Verifica nelle impostazioni SIP/PJSIP del centralino:
   - `dtmfmode=rfc2833` (consigliato)
   - oppure `dtmfmode=inband`
2. Nei log Asterisk verifica:
   ```bash
   asterisk -rx "core set verbose 5"
   asterisk -rx "core set debug 5"
   ```
3. Testa manualmente DTMF dal centralino

### Problema: File Temporanei Non Trovati

**Verifica sul Server Asterisk** (via SSH):
```bash
# Durante una chiamata attiva, controlla:
ls -la /tmp/snooze_*
cat /tmp/snooze_5_audio_*.txt
cat /tmp/snooze_10_audio_*.txt
```

Se i file non esistono:
1. Problema permessi SSH
2. Problema esecuzione comando `echo`
3. Controlla log: `logs/pbx_connection.log`

---

## 📊 Risultato Atteso

**Esperienza Utente Ideale**:

1. 🔔 Telefono squilla
2. 📞 Cliente risponde
3. 🔊 Ascolta: "Buongiorno, sono le 7:00. Premi 1 per 5 minuti, 2 per 10 minuti"
4. ⌨️ Cliente preme **1**
5. 🔊 Ascolta **immediatamente**: "La sveglia è stata posticipata di 5 minuti"
6. 📴 Chiamata si chiude
7. ⏰ Dopo 5 minuti esatti: nuova chiamata (ripete dal punto 1)

**UNA SOLA chiamata** - tutto avviene nella stessa sessione!

---

## 🐛 Debug Avanzato

### Abilita Debug Completo Asterisk

```bash
ssh admin@192.168.1.100
asterisk -rvvvvv
core set verbose 10
core set debug 10
dialplan reload
```

### Testa Manualmente il Dialplan

```bash
# Sul CLI Asterisk:
originate Local/130@from-internal extension custom-wakeup_audio@wakeup-service
```

### Verifica Che gli Audio Siano Caricati

```bash
ls -la /var/lib/asterisk/sounds/custom/
file /var/lib/asterisk/sounds/custom/wakeup_audio.wav
file /var/lib/asterisk/sounds/custom/snooze_5_it.wav
```

### Controlla Dialplan Caricato

```bash
asterisk -rx "dialplan show wakeup-service"
```

Dovresti vedere tutte le extension (1, 2, t, i, _.)

---

## ✅ Successo!

Se tutto funziona correttamente:

- [ ] Chiamata ricevuta con CallerID corretto
- [ ] Audio sveglia riprodotto correttamente
- [ ] DTMF '1' o '2' rilevato
- [ ] Audio conferma riprodotto **nella stessa chiamata**
- [ ] Chiamata chiusa automaticamente
- [ ] Nuova sveglia creata dopo X minuti
- [ ] Log completi e senza errori

**Congratulazioni! Il sistema di snooze con conferma audio è completamente funzionante! 🎉**

---

## 📞 Supporto

In caso di problemi persistenti:

1. Raccogli i log:
   - `logs/alarm_manager.log`
   - `logs/pbx_connection.log`
   - Log Asterisk (`/var/log/asterisk/full`)

2. Verifica configurazione:
   - `settings.json`
   - Database: `alarms.db` → tabella `audio_messages`
   - Context Asterisk: `/etc/asterisk/extensions_custom.conf`

3. Controlla versione Asterisk:
   ```bash
   asterisk -rx "core show version"
   ```

4. Documenta l'errore con:
   - Cosa hai fatto
   - Cosa ti aspettavi
   - Cosa è successo invece
   - Log rilevanti

