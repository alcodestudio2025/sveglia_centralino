# 🔊 GUIDA TEST RIPRODUZIONE AUDIO

## ✅ Implementazione Completata

È stata implementata la **riproduzione audio completa** usando `pygame.mixer`.

---

## 🎵 Come Funziona

### **1. Audio Player (`audio_player.py`)**

- **Classe `AudioPlayer`**: Gestisce tutta la riproduzione audio
- **Singleton Pattern**: Una sola istanza condivisa nell'app
- **Pygame Mixer**: Backend audio robusto e affidabile
- **Supporto formati**: MP3, WAV, OGG, FLAC

#### Funzionalità Principali:
```python
player = get_audio_player()
player.play(audio_path)           # Riproduce
player.stop()                     # Ferma
player.is_playing()               # Verifica se sta riproducendo
player.set_volume(0.8)            # Imposta volume (0.0 - 1.0)
player.get_volume()               # Legge volume
```

---

## 🧪 TEST AUDIO - Passo per Passo

### **TEST 1: Dalla Schermata Principale**

1. **Avvia l'applicazione**
   ```bash
   python main.py
   ```

2. **Carica un audio** (se non presente):
   - Menu → Gestione → Gestisci Messaggi Audio
   - Nome: "Test_Wakeup"
   - Categoria: Sveglia
   - Lingua: it
   - Azione: Messaggio Sveglia
   - Click "Seleziona File Audio" → scegli un MP3
   - Conferma

3. **Testa dalla schermata principale**:
   - Seleziona "Test_Wakeup" dal menu a tendina
   - Click pulsante "🔊 Test Audio"
   - **RISULTATO ATTESO**: 
     - Popup con info audio
     - Audio si riproduce in background
     - Volume al 100%

---

### **TEST 2: Da Gestione Messaggi Audio**

1. **Apri gestione audio**:
   - Menu → Gestione → Gestisci Messaggi Audio

2. **Seleziona un messaggio** dalla lista

3. **Click pulsante "Riproduci Selezionato"**
   - **RISULTATO ATTESO**:
     - Popup con dettagli (nome, durata, categoria, lingua, azione)
     - Audio si riproduce

4. **Doppio click su un messaggio**
   - **RISULTATO ATTESO**: Riproduzione istantanea

---

### **TEST 3: Verifica Formati Audio**

Prova con diversi formati:
- ✅ **MP3**: Supportato
- ✅ **WAV**: Supportato
- ✅ **OGG**: Supportato
- ✅ **FLAC**: Supportato

---

## 🔧 Risoluzione Problemi

### **Problema: "Audio player non inizializzato"**
**Causa**: pygame.mixer non si è inizializzato correttamente

**Soluzione**:
```bash
pip install --upgrade pygame
```

---

### **Problema: "File audio non trovato"**
**Causa**: Il file è stato spostato o cancellato

**Verifica**:
- Controlla che il file esista in `audio_files/`
- Vedi log per il percorso esatto

---

### **Problema: Nessun suono**
**Causa**: Volume di sistema troppo basso o muto

**Verifica**:
1. Controlla volume di Windows
2. Controlla mixer audio (l'app Python deve avere volume)
3. Prova con un altro file audio

---

### **Problema: "Errore riproduzione audio"**
**Causa**: File audio corrotto o formato non supportato

**Soluzione**:
1. Ricodifica il file con Audacity/FFmpeg
2. Converti in MP3 standard (44.1kHz, 128kbps)
3. Ricarica il file

---

## 📊 Log e Debug

I log audio sono visibili in:
- **File**: `logs/sveglia_centralino.log`
- **Prefisso**: `[audio_player]`

**Esempi di log:**
```
[INFO] Audio player inizializzato con successo
[INFO] Riproduzione audio: audio_files/Wakeup_ita.mp3
[INFO] Riproduzione avviata: Wakeup_ita.mp3
[INFO] Volume impostato a: 1.00
[ERROR] File audio non trovato: audio_files/missing.mp3
```

---

## 🎛️ Configurazione Volume

Il volume di default è **100%** (1.0).

Per cambiarlo:
```python
from audio_player import get_audio_player
player = get_audio_player()
player.set_volume(0.5)  # 50%
```

---

## 🚀 Prossimi Passi

- [x] Riproduzione audio base
- [x] Test dalla schermata principale
- [x] Test da gestione messaggi
- [ ] Controlli volume nell'UI
- [ ] Pulsante Stop/Pausa
- [ ] Visualizzazione barra progresso
- [ ] Integrazione con sveglie PBX

---

## 📞 Integrazione PBX (Futuro)

Quando sarà collegato al PBX, l'audio verrà:
1. **Inviato al centralino** via SSH
2. **Riprodotto tramite Asterisk** al cliente
3. **Gestito dai DTMF** per snooze/conferma

---

## ✅ Checklist Test Completa

- [ ] Audio si riproduce da schermata principale
- [ ] Audio si riproduce da gestione messaggi
- [ ] Doppio click funziona
- [ ] Popup mostra info corrette
- [ ] Log registra eventi audio
- [ ] Formati multipli funzionano (MP3, WAV, OGG)
- [ ] Volume al 100%
- [ ] Nessun errore in console

---

**Testa ora la riproduzione audio e segnala eventuali problemi!** 🎵

