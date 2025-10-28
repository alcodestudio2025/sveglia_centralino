# 🔊 GUIDA MESSAGGI AUDIO - SISTEMA SNOOZE

## ✅ SISTEMA IMPLEMENTATO

Il sistema di snooze con DTMF è stato completamente implementato!

---

## 🎵 MESSAGGI AUDIO NECESSARI

Per il sistema snooze servono **3 tipi** di messaggi audio:

### **1. MESSAGGIO SVEGLIA (wake_up)**
**Tipo Azione**: `Messaggio Sveglia`  
**Quando**: Riprodotto al risveglio del cliente  
**Esempio testo**:
```
"Buongiorno! Sono le 7:00. 
Questa è la sua sveglia.

Per posticipare di 5 minuti, prema il tasto 1.
Per posticipare di 10 minuti, prema il tasto 2.
Per terminare, riagganci pure."
```

---

### **2. CONFERMA SNOOZE 5 MINUTI**
**Tipo Azione**: `Conferma Riprogrammazione`  
**Nome file**: Deve contenere "5" (es: `Ritarda_5`)  
**Quando**: Dopo che il cliente preme il tasto 1  
**Esempio testo**:
```
"Sveglia posticipata di 5 minuti.
La richiameremo alle 7:05.
Buon riposo! Arrivederci."
```
⚠️ **Importante**: Include già il saluto finale!

---

### **3. CONFERMA SNOOZE 10 MINUTI**
**Tipo Azione**: `Conferma Riprogrammazione`  
**Nome file**: Deve contenere "10" (es: `Ritarda_10`)  
**Quando**: Dopo che il cliente preme il tasto 2  
**Esempio testo**:
```
"Sveglia posticipata di 10 minuti.
La richiameremo alle 7:10.
Buon riposo! Arrivederci."
```
⚠️ **Importante**: Include già il saluto finale!

---

## 📋 COME CARICARE I MESSAGGI

### **Passo 1: Preparazione File Audio**

**Formato raccomandato**: WAV o MP3  
**Qualità**: 44.1kHz, 16-bit, Mono  
**Durata**: 5-15 secondi ciascuno  

**Nomi file suggeriti**:
```
wakeup_main_ita.wav
ritarda_5_ita.wav
ritarda_10_ita.wav
```

---

### **Passo 2: Caricamento nell'App**

**1. MESSAGGIO SVEGLIA PRINCIPALE**
- Menu → Gestione → Gestisci Messaggi Audio
- Nome: `Wakeup_Main_IT`
- Categoria: `standard`
- Lingua: `it`
- Tipo Azione: `Messaggio Sveglia`
- Click "Seleziona File Audio" → `wakeup_main_ita.wav`

**2. CONFERMA SNOOZE 5 MINUTI**
- Nome: `Ritarda_5` *(importante: contiene "5")*
- Categoria: `standard`
- Lingua: `it`
- Tipo Azione: `Conferma Riprogrammazione`
- Click "Seleziona File Audio" → `ritarda_5_ita.wav`

**3. CONFERMA SNOOZE 10 MINUTI**
- Nome: `Ritarda_10` *(importante: contiene "10")*
- Categoria: `standard`
- Lingua: `it`
- Tipo Azione: `Conferma Riprogrammazione`
- Click "Seleziona File Audio" → `ritarda_10_ita.wav`

---

## 🔄 FLUSSO OPERATIVO

### **Scenario 1: Cliente Posticipa 5 Minuti**

```
1. 🔔 Chiamata avviata → Interno 103
2. 🔊 Audio: "Buongiorno... Per posticipare di 5 minuti prema 1..."
3. ☎️ Cliente: Preme tasto "1"
4. ✅ Sistema: Rileva DTMF "1"
5. 🔊 Audio: "Sveglia posticipata di 5 minuti..."
6. 📅 Sistema: Crea nuova sveglia per +5 minuti
7. ✓ Sveglia riprogrammata per 07:05
```

---

### **Scenario 2: Cliente Posticipa 10 Minuti**

```
1. 🔔 Chiamata avviata → Interno 103
2. 🔊 Audio: "Buongiorno... Per posticipare di 10 minuti prema 2..."
3. ☎️ Cliente: Preme tasto "2"
4. ✅ Sistema: Rileva DTMF "2"
5. 🔊 Audio: "Sveglia posticipata di 10 minuti..."
6. 📅 Sistema: Crea nuova sveglia per +10 minuti
7. ✓ Sveglia riprogrammata per 07:10
```

---

### **Scenario 3: Cliente Accetta Sveglia (Nessun Tasto)**

```
1. 🔔 Chiamata avviata → Interno 103
2. 🔊 Audio: "Buongiorno... Per posticipare prema 1 o 2..."
3. ☎️ Cliente: NON preme nulla / Riaggancia
4. ⏱️ Sistema: Timeout (30 secondi) o hangup
5. ✓ Sveglia completata (nessun audio aggiuntivo)
```

---

## 🧪 TEST SISTEMA SNOOZE

### **Test Manuale (quando PBX connesso):**

1. **Programma sveglia** per tra 1-2 minuti
2. **Camera**: 103 (o altra configurata)
3. **Audio**: Seleziona "Wakeup_Main_IT"
4. **Attendi chiamata**
5. **Test DTMF**:
   - Premi "1" → Verifica: sveglia riprogrammata +5 min
   - Premi "2" → Verifica: sveglia riprogrammata +10 min
   - Non premere nulla → Verifica: sveglia completata

---

## 📊 CONFIGURAZIONE OPZIONI SNOOZE

Attualmente configurato:
- **Tasto 1**: 5 minuti
- **Tasto 2**: 10 minuti

### **Per Modificare:**

Modifica `alarm_manager.py`, metodo `_execute_alarm_with_snooze`:

```python
if dtmf_digit == '1':
    snooze_minutes = 5  # Cambia qui per modificare
    
elif dtmf_digit == '2':
    snooze_minutes = 10  # Cambia qui per modificare
```

---

## 🔍 LOG E DEBUG

### **Log Sveglia con Snooze:**

```
============================================================
SVEGLIA CON SNOOZE - Camera 103 - Interno 103
============================================================
✓ Chiamata avviata a 103
Riproduzione messaggio sveglia con opzioni snooze...
✓ DTMF '1' ricevuto - Snooze 5 minuti
Audio trovato: Snooze_5min_IT (snooze_confirm, it, 5min)
Riproduzione conferma snooze 5 minuti...
Riprogrammazione sveglia per 07:05
✓ Sveglia riprogrammata con successo
============================================================
```

---

## ⚙️ COMANDI ASTERISK UTILIZZATI

### **1. Chiamata + DTMF:**
```bash
asterisk -rx 'channel originate Local/103@internal application Read dtmf_input,wakeup_main_ita,1,n,30'
```

### **2. Riproduzione Audio:**
```bash
asterisk -rx 'playback snooze_5min_ita'
```

---

## ✅ CHECKLIST SETUP COMPLETO

- [ ] File audio preparati (**3 file**: wake, snooze 5, snooze 10)
- [ ] Audio caricati nell'app con **tipo azione corretto**
- [ ] Nome file snooze contiene "5" e "10"
- [ ] Lingua impostata correttamente (IT)
- [ ] Test riproduzione da "Gestisci Messaggi Audio"
- [ ] PBX connesso e raggiungibile
- [ ] Camera configurata con interno valido
- [ ] Test sveglia manuale con DTMF
- [ ] Messaggi conferma includono saluto finale

---

## 🎯 PROSSIMI PASSI

1. **Prepara i 4 file audio** (registrazione o text-to-speech)
2. **Carica nell'app** seguendo la guida sopra
3. **Testa con sveglia reale**
4. **Verifica log** per debugging
5. **Adatta messaggi** in base al feedback clienti

---

## 🌍 MULTI-LINGUA

Per aggiungere altre lingue:

**Inglese:**
- Nome: `Wakeup_Main_EN`, `Snooze_5min_EN`, etc.
- Lingua: `en`
- Stesso processo di caricamento

Il sistema selezionerà automaticamente l'audio nella lingua corretta!

---

**Sistema pronto per i test reali con PBX!** 🚀📞

