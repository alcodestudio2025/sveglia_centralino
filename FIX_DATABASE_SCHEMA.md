# FIX SCHEMA DATABASE

## PROBLEMA TROVATO

Il database `sveglie.db` ha le colonne della tabella `rooms` nell'ordine SBAGLIATO a causa di migration precedenti.

**Ordine trovato nel database:**
```
0: id
1: room_number
2: phone_extension ← CONTIENE 'available' ❌
3: description ← CONTIENE timestamp ❌
4: status ← CONTIENE numero interno ❌
5: color ← CONTIENE descrizione ❌
6: label ← CONTIENE colore ❌
7: created_at ← CONTIENE label ❌
```

**Ordine CORRETTO nel codice:**
```sql
CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number TEXT UNIQUE NOT NULL,
    phone_extension TEXT DEFAULT '',
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'available',
    color TEXT DEFAULT '#FFFFFF',
    label TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## SOLUZIONE

### WINDOWS (PowerShell):
```powershell
Remove-Item sveglie.db
python main.py
```

### LINUX/MAC:
```bash
rm sveglie.db
python main.py
```

Il database verrà ricreato automaticamente con lo schema corretto.

## DOPO IL FIX

1. Apri l'applicazione
2. Menu → Gestione → Gestisci Camere
3. Click "🗑️ Pulisci e Reimporta"
4. Click "🔄 Aggiorna Stato"

Gli stati online/offline dovrebbero apparire correttamente!

