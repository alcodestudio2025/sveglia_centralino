# 🎵 Guida Nomenclatura File Audio

## 📋 Sistema di Denominazione File Audio

Il sistema riconosce automaticamente i file audio in base al **nome del file** e all'**azione** associata nel database.

---

## 🔑 Regole per Nomenclatura File

### **1️⃣ MESSAGGIO SVEGLIA (wake_up)**

**Formato Nome File:**
```
wakeup_<nome>_<lingua>_<numero>.wav
```

**Esempi:**
- `wakeup_didimos_asterisk_1.wav` → Nome visualizzato: "Wakeup_ITA"
- `wakeup_hotel_en_1.wav` → Nome visualizzato: "Wakeup_ENG"
- `wakeup_standard_de_1.wav` → Nome visualizzato: "Wakeup_DEU"
- `wakeup_deluxe_fr_1.wav` → Nome visualizzato: "Wakeup_FRA"

**Parametri nel Database:**
- **Nome:** Quello che vuoi (es: "Wakeup_ITA", "Buongiorno Cliente")
- **Lingua:** `it`, `en`, `de`, `fr`, `es`, ecc.
- **Azione:** `wake_up`
- **Variante:** (vuoto o numero versione)

---

### **2️⃣ CONFERMA SNOOZE 5 MINUTI (snooze_confirm + variant "5")**

**Formato Nome File:**
```
snooze_5min_<lingua>_<versione>.wav
```

**Esempi:**
- `snooze_5min_it_1.wav` → "La sveglia suonerà tra 5 minuti. Buona giornata!"
- `snooze_5min_en_1.wav` → "Your alarm will ring in 5 minutes. Have a nice day!"
- `snooze_5min_de_1.wav` → "Ihr Wecker klingelt in 5 Minuten. Schönen Tag!"
- `snooze_5min_fr_1.wav` → "Votre réveil sonnera dans 5 minutes. Bonne journée!"

**Parametri nel Database:**
- **Nome:** "Conferma Snooze 5min ITA" (o qualsiasi nome descrittivo)
- **Lingua:** `it`, `en`, `de`, `fr`, `es`
- **Azione:** `snooze_confirm`
- **Variante:** `5` ⚠️ **IMPORTANTE: deve contenere "5" nel nome!**

---

### **3️⃣ CONFERMA SNOOZE 10 MINUTI (snooze_confirm + variant "10")**

**Formato Nome File:**
```
snooze_10min_<lingua>_<versione>.wav
```

**Esempi:**
- `snooze_10min_it_1.wav` → "La sveglia suonerà tra 10 minuti. Buona giornata!"
- `snooze_10min_en_1.wav` → "Your alarm will ring in 10 minutes. Have a nice day!"
- `snooze_10min_de_1.wav` → "Ihr Wecker klingelt in 10 Minuten. Schönen Tag!"
- `snooze_10min_fr_1.wav` → "Votre réveil sonnera dans 10 minutes. Bonne journée!"

**Parametri nel Database:**
- **Nome:** "Conferma Snooze 10min ITA" (o qualsiasi nome descrittivo)
- **Lingua:** `it`, `en`, `de`, `fr`, `es`
- **Azione:** `snooze_confirm`
- **Variante:** `10` ⚠️ **IMPORTANTE: deve contenere "10" nel nome!**

---

## 📂 Struttura Cartelle

```
audio_messages/
├── wakeup_didimos_asterisk_1.wav     (ITA - wake_up)
├── wakeup_hotel_en_1.wav             (ENG - wake_up)
├── snooze_5min_it_1.wav              (ITA - snooze_confirm variant 5)
├── snooze_10min_it_1.wav             (ITA - snooze_confirm variant 10)
├── snooze_5min_en_1.wav              (ENG - snooze_confirm variant 5)
├── snooze_10min_en_1.wav             (ENG - snooze_confirm variant 10)
└── ...
```

---

## 🔍 Come il Sistema Trova i File

### **Messaggio Sveglia:**
1. Cerca `action_type = 'wake_up'`
2. Filtra per `language = 'it'` (lingua della camera)
3. Restituisce il primo file trovato

### **Conferma Snooze:**
1. Cerca `action_type = 'snooze_confirm'`
2. Filtra per `language = 'it'` (lingua della camera)
3. Filtra per **variant** (cerca "5" o "10" nel **nome** del file)
4. Esempio:
   - Se premi `1` → cerca file con "5" nel nome
   - Se premi `2` → cerca file con "10" nel nome

---

## 🎯 Codici Lingua Supportati (ISO 639-1)

| Codice | Lingua       | Esempio Nome File               |
|--------|--------------|---------------------------------|
| `it`   | Italiano     | `wakeup_standard_it_1.wav`      |
| `en`   | Inglese      | `wakeup_standard_en_1.wav`      |
| `de`   | Tedesco      | `wakeup_standard_de_1.wav`      |
| `fr`   | Francese     | `wakeup_standard_fr_1.wav`      |
| `es`   | Spagnolo     | `wakeup_standard_es_1.wav`      |
| `ru`   | Russo        | `wakeup_standard_ru_1.wav`      |
| `zh`   | Cinese       | `wakeup_standard_zh_1.wav`      |
| `ja`   | Giapponese   | `wakeup_standard_ja_1.wav`      |
| `ar`   | Arabo        | `wakeup_standard_ar_1.wav`      |

---

## ✅ Checklist Caricamento Audio

### **Per ogni lingua supportata:**

- [ ] 1 file sveglia (`wake_up`)
- [ ] 1 file conferma 5 minuti (`snooze_confirm` con "5" nel nome)
- [ ] 1 file conferma 10 minuti (`snooze_confirm` con "10" nel nome)

### **Esempio set completo ITALIANO:**
```
✅ wakeup_standard_it_1.wav          → wake_up, it
✅ snooze_5min_it_1.wav              → snooze_confirm, it (nome contiene "5")
✅ snooze_10min_it_1.wav             → snooze_confirm, it (nome contiene "10")
```

### **Esempio set completo INGLESE:**
```
✅ wakeup_standard_en_1.wav          → wake_up, en
✅ snooze_5min_en_1.wav              → snooze_confirm, en (nome contiene "5")
✅ snooze_10min_en_1.wav             → snooze_confirm, en (nome contiene "10")
```

---

## 🎤 Testi Suggeriti per Messaggi Audio

### **ITALIANO**

**Sveglia (wake_up):**
> "Buongiorno! È ora di svegliarsi. Premi 1 per posticipare di 5 minuti, premi 2 per posticipare di 10 minuti."

**Conferma 5 minuti (snooze_confirm - 5):**
> "Perfetto! La sveglia suonerà nuovamente tra 5 minuti. Buona giornata!"

**Conferma 10 minuti (snooze_confirm - 10):**
> "Perfetto! La sveglia suonerà nuovamente tra 10 minuti. Buona giornata!"

---

### **ENGLISH**

**Wake-up (wake_up):**
> "Good morning! Time to wake up. Press 1 to snooze for 5 minutes, press 2 to snooze for 10 minutes."

**Confirm 5 minutes (snooze_confirm - 5):**
> "Perfect! Your alarm will ring again in 5 minutes. Have a nice day!"

**Confirm 10 minutes (snooze_confirm - 10):**
> "Perfect! Your alarm will ring again in 10 minutes. Have a nice day!"

---

### **DEUTSCH**

**Aufwachen (wake_up):**
> "Guten Morgen! Zeit aufzuwachen. Drücken Sie 1 für 5 Minuten Schlummern, drücken Sie 2 für 10 Minuten Schlummern."

**Bestätigung 5 Minuten (snooze_confirm - 5):**
> "Perfekt! Ihr Wecker klingelt in 5 Minuten erneut. Schönen Tag!"

**Bestätigung 10 Minuten (snooze_confirm - 10):**
> "Perfekt! Ihr Wecker klingelt in 10 Minuten erneut. Schönen Tag!"

---

### **FRANÇAIS**

**Réveil (wake_up):**
> "Bonjour ! Il est temps de se réveiller. Appuyez sur 1 pour reporter de 5 minutes, appuyez sur 2 pour reporter de 10 minutes."

**Confirmation 5 minutes (snooze_confirm - 5):**
> "Parfait ! Votre réveil sonnera à nouveau dans 5 minutes. Bonne journée !"

**Confirmation 10 minutes (snooze_confirm - 10):**
> "Parfait ! Votre réveil sonnera à nouveau dans 10 minutes. Bonne journée !"

---

## 🚨 Errori Comuni

### ❌ **ERRORE: Audio non trovato**

**Log:**
```
WARNING: Audio non trovato: snooze_confirm, it, 5
```

**Cause possibili:**
1. ❌ File non caricato nell'applicazione
2. ❌ Lingua errata (es: file è `en` ma camera è `it`)
3. ❌ Azione errata (non impostata come `snooze_confirm`)
4. ❌ **Nome file NON contiene "5" o "10"**

**Soluzioni:**
1. ✅ Verifica che il file sia presente in "Gestione → Audio/Messaggi"
2. ✅ Verifica che la lingua corrisponda (es: `it` per italiano)
3. ✅ Verifica che "Tipo Azione" sia `snooze_confirm`
4. ✅ **Verifica che il NOME FILE contenga "5" o "10"** (es: `snooze_5min_it_1.wav`)

---

## 🎯 Esempio Pratico Completo

### **Scenario:**
- Hotel con camere ITA e ENG
- Snooze 5 e 10 minuti

### **File da caricare:**

| File                          | Nome Visualizzato      | Lingua | Azione           | Note              |
|-------------------------------|------------------------|--------|------------------|-------------------|
| `wakeup_standard_it_1.wav`    | Sveglia Standard ITA   | it     | wake_up          |                   |
| `wakeup_standard_en_1.wav`    | Sveglia Standard ENG   | en     | wake_up          |                   |
| `snooze_5min_it_1.wav`        | Conferma 5min ITA      | it     | snooze_confirm   | Nome contiene "5" |
| `snooze_10min_it_1.wav`       | Conferma 10min ITA     | it     | snooze_confirm   | Nome contiene "10"|
| `snooze_5min_en_1.wav`        | Confirm 5min ENG       | en     | snooze_confirm   | Nome contiene "5" |
| `snooze_10min_en_1.wav`       | Confirm 10min ENG      | en     | snooze_confirm   | Nome contiene "10"|

### **Flusso Esempio:**

1. **Cliente in camera 130 (lingua: IT)**
   - Ore 07:00 → Squilla telefono
   - Riproduce: `wakeup_standard_it_1.wav`
   - Cliente preme **1**
   - Riproduce: `snooze_5min_it_1.wav` (contiene "5" nel nome!)
   - Riprogramma sveglia per 07:05

2. **Cliente in camera 205 (lingua: EN)**
   - Ore 08:00 → Squilla telefono
   - Riproduce: `wakeup_standard_en_1.wav`
   - Cliente preme **2**
   - Riproduce: `snooze_10min_en_1.wav` (contiene "10" nel nome!)
   - Riprogramma sveglia per 08:10

---

## 📝 Note Finali

- ✅ **Il nome del file NON deve necessariamente seguire il formato suggerito**, ma è **ALTAMENTE RACCOMANDATO** per chiarezza
- ✅ **Ciò che CONTA è:**
  1. Lingua corretta nel database
  2. Azione corretta (`wake_up` o `snooze_confirm`)
  3. **Per snooze: il NOME del file deve contenere "5" o "10"**
- ✅ Il sistema è **case-insensitive** (maiuscole/minuscole non importano)
- ✅ Puoi avere **più versioni** dello stesso audio (es: `snooze_5min_it_1.wav`, `snooze_5min_it_2.wav`) selezionando manualmente quella da usare

---

## 🆘 Supporto

Se un audio non viene trovato, controlla i **log** per vedere cosa sta cercando:

```
WARNING: Audio non trovato: snooze_confirm, it, 5
```

Questo significa che sta cercando:
- **Azione:** `snooze_confirm`
- **Lingua:** `it`
- **Variante:** "5" (deve essere NEL NOME del file!)

✅ Soluzione: Carica un file con nome tipo `snooze_5min_it_1.wav` e imposta:
- Lingua: `it`
- Azione: `snooze_confirm`

---

**🎉 Buon lavoro con il sistema di sveglie!**

