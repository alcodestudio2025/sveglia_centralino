# 🎵 Audio Conferma Snooze - Istruzioni Rapide

## ✅ Cosa è stato implementato

Dopo aver premuto **1** o **2** per lo snooze, il sistema ora:

1. ✅ Riproduce un **messaggio di conferma** personalizzato
2. ✅ Riprogramma automaticamente la sveglia
3. ✅ Chiude la chiamata

---

## 📁 File Audio Necessari

### **Per ogni lingua supportata, devi caricare 3 file:**

1. **Messaggio Sveglia** (`wake_up`)
2. **Conferma Snooze 5 minuti** (`snooze_confirm` con "5" nel nome)
3. **Conferma Snooze 10 minuti** (`snooze_confirm` con "10" nel nome)

---

## 🎯 COME RINOMINARE I FILE

### **ITALIANO:**

```
wakeup_standard_it_1.wav          → Messaggio sveglia
snooze_5min_it_1.wav             → Conferma 5 minuti (DEVE contenere "5")
snooze_10min_it_1.wav            → Conferma 10 minuti (DEVE contenere "10")
```

### **INGLESE:**

```
wakeup_standard_en_1.wav          → Wake-up message
snooze_5min_en_1.wav             → Confirm 5 minutes (MUST contain "5")
snooze_10min_en_1.wav            → Confirm 10 minutes (MUST contain "10")
```

### **TEDESCO:**

```
wakeup_standard_de_1.wav          → Weckruf
snooze_5min_de_1.wav             → Bestätigung 5 Minuten (MUSS "5" enthalten)
snooze_10min_de_1.wav            → Bestätigung 10 Minuten (MUSS "10" enthalten)
```

### **FRANCESE:**

```
wakeup_standard_fr_1.wav          → Message de réveil
snooze_5min_fr_1.wav             → Confirmation 5 minutes (DOIT contenir "5")
snooze_10min_fr_1.wav            → Confirmation 10 minutes (DOIT contenir "10")
```

---

## 📝 Testi Consigliati

### **ITALIANO - Conferma 5 minuti:**
> "Perfetto! La sveglia suonerà nuovamente tra 5 minuti. Buona giornata!"

### **ITALIANO - Conferma 10 minuti:**
> "Perfetto! La sveglia suonerà nuovamente tra 10 minuti. Buona giornata!"

### **ENGLISH - Confirm 5 minutes:**
> "Perfect! Your alarm will ring again in 5 minutes. Have a nice day!"

### **ENGLISH - Confirm 10 minutes:**
> "Perfect! Your alarm will ring again in 10 minutes. Have a nice day!"

---

## 🚀 PROCEDURA CARICAMENTO

### **1. Carica i file nell'app:**

1. Apri l'applicazione
2. Vai su **Gestione → Audio/Messaggi**
3. Clicca **"Nuovo Audio"**

### **2. Per il file "Conferma 5 minuti":**

- **Nome:** "Conferma Snooze 5min ITA" (o qualsiasi nome descrittivo)
- **File:** Seleziona `snooze_5min_it_1.wav`
- **Lingua:** Seleziona `Italiano`
- **Tipo Azione:** Seleziona **"Conferma Snooze"**
- **Salva**

⚠️ **IMPORTANTE:** Il nome del FILE deve contenere "5" (es: `snooze_5min_it_1.wav`)

### **3. Per il file "Conferma 10 minuti":**

- **Nome:** "Conferma Snooze 10min ITA" (o qualsiasi nome descrittivo)
- **File:** Seleziona `snooze_10min_it_1.wav`
- **Lingua:** Seleziona `Italiano`
- **Tipo Azione:** Seleziona **"Conferma Snooze"**
- **Salva**

⚠️ **IMPORTANTE:** Il nome del FILE deve contenere "10" (es: `snooze_10min_it_1.wav`)

---

## 🔧 RICONFIGURAZIONE ASTERISK (OBBLIGATORIA)

### **Prima di testare, DEVI riconfigurare il dialplan Asterisk:**

1. Apri l'applicazione
2. Vai su **Gestione → Impostazioni**
3. Tab **"Connessione PBX"**
4. Clicca sul pulsante **"Configura Context DTMF"**
5. Attendi il messaggio di conferma

Questo aggiornerà il dialplan Asterisk con il nuovo context `wakeup-service-simple` per riprodurre i messaggi di conferma.

---

## 📊 VERIFICA FUNZIONAMENTO

### **Test completo:**

1. ✅ Imposta una sveglia di test
2. ✅ Rispondi alla chiamata
3. ✅ Ascolta il messaggio sveglia
4. ✅ Premi **1** (snooze 5 min)
5. ✅ **Ascolta il messaggio di conferma "La sveglia suonerà tra 5 minuti"**
6. ✅ Verifica che la sveglia sia riprogrammata di 5 minuti

### **Log di successo:**

```
✓ DTMF '1' ricevuto - Snooze 5 minuti
Riproduzione conferma snooze 5 minuti...
Upload audio conferma su Asterisk: audio_messages\snooze_5min_it_1.wav
✓ Audio caricato: /var/lib/asterisk/sounds/custom/snooze_5min_it_1.wav
✓ Audio semplice riprodotto
Riprogrammazione sveglia per 07:05
✓ Sveglia riprogrammata con successo
```

---

## ⚠️ Risoluzione Problemi

### **Errore: "Audio non trovato: snooze_confirm, it, 5"**

**Causa:** File non caricato o nome file errato

**Soluzione:**
1. Verifica che il file sia caricato in "Audio/Messaggi"
2. Verifica che la lingua sia corretta (es: `it`)
3. Verifica che "Tipo Azione" sia **"Conferma Snooze"**
4. **VERIFICA che il NOME FILE contenga "5" o "10"** (es: `snooze_5min_it_1.wav`, NON `conferma_it_1.wav`)

---

### **Errore: "Errore upload audio"**

**Causa:** Problema connessione SSH o permessi Asterisk

**Soluzione:**
1. Verifica la connessione PBX in "Impostazioni"
2. Verifica i permessi su `/var/lib/asterisk/sounds/custom/`
3. Controlla i log per dettagli

---

### **Audio non riprodotto dopo DTMF**

**Causa:** Context Asterisk non aggiornato

**Soluzione:**
1. Vai in "Impostazioni → Connessione PBX"
2. Clicca su **"Configura Context DTMF"**
3. Attendi il messaggio di successo
4. Riprova il test

---

## 📖 Documentazione Completa

Per maggiori dettagli sulla nomenclatura e supporto multilingua, vedi:

👉 **`GUIDA_NOMENCLATURA_AUDIO.md`**

---

**🎉 Buon lavoro!**

