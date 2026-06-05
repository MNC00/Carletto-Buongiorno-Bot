# Guida: Configurazione Google per Compleanni e Nickname

## 1. Google Form — Aggiungere "Data di nascita"

1. Apri il Google Form collegato al foglio `users`
2. Clicca **"Aggiungi domanda"** (icona `+`)
3. Seleziona il tipo **"Data"**
4. Titolo della domanda: **`Data di nascita`**
5. Nelle opzioni della domanda (⋮):
   - Disattiva **"Includi anno"** se vuoi solo giorno/mese, oppure lascialo attivo (il bot usa solo giorno e mese)
   - Scegli se rendere la domanda **obbligatoria** o facoltativa
6. Posiziona la domanda dove preferisci nel form
7. Invia una risposta di test e verifica che la colonna **"Data di nascita"** appaia nel foglio `users`

> **Nota**: il formato della data nel foglio dipende dal locale del Google Sheet. Il bot supporta i formati `GG/MM/AAAA`, `AAAA-MM-GG` e `GG-MM-AAAA`.

---

## 2. Google Sheet — Aggiungere colonne manuali

Apri il foglio `users` dello spreadsheet collegato al form.

### Colonna `nickname`
1. Vai alla **prima colonna vuota** dopo le colonne esistenti
2. Nella cella dell'header (riga 1), scrivi: **`nickname`**
3. Compila manualmente il nickname per i contatti che vuoi personalizzare
4. Lascia vuoto per gli altri — il bot userà il nome

### Colonna `birthday_public`
1. Nella colonna successiva, scrivi nell'header: **`birthday_public`**
2. Compila con **`true`** o **`false`** per ogni contatto:
   - `true` (default) → gli auguri di compleanno sono visibili a **tutti** gli iscritti
   - `false` → gli auguri vengono inviati **solo** al festeggiato
3. Se lasci la cella vuota, il default è `true`

> **Importante**: queste colonne NON devono essere aggiunte al Google Form. Sono colonne tecniche gestite manualmente.

---

## 3. Apps Script — Aggiornare `grant_access.gs`

Lo script è già stato aggiornato nel codice della repo. Per applicare le modifiche:

1. Apri il Google Form → menu **⋮** → **Editor di script** (Apps Script)
2. Apri il file `grant_access.gs`
3. Nella sezione **CONFIGURAZIONE** in alto, verifica che ci siano le variabili:
   ```javascript
   var NICKNAME_COLUMN_TITLE = "nickname";
   var BIRTHDAY_PUBLIC_COLUMN_TITLE = "birthday_public";
   ```
4. Nella funzione `_ensureTechnicalColumns()`, verifica che `requiredHeaders` includa le nuove colonne:
   ```javascript
   var requiredHeaders = [ACTIVE_COLUMN_TITLE, UNSUBSCRIBED_AT_COLUMN_TITLE, NICKNAME_COLUMN_TITLE, BIRTHDAY_PUBLIC_COLUMN_TITLE];
   ```
5. Salva il file (Ctrl+S)
6. **Non serve re-deployare** — il trigger `onFormSubmit` usa automaticamente il codice aggiornato

> **Nota**: al prossimo invio del form, se le colonne `nickname` e `birthday_public` non esistono ancora nel foglio, lo script le creerà automaticamente.

---

## 4. Verifica

1. Invia una risposta di test dal Google Form con una data di nascita
2. Apri il foglio `users` e verifica:
   - La colonna **"Data di nascita"** è stata popolata
   - Le colonne **"nickname"** e **"birthday_public"** esistono (create manualmente o dallo script)
3. Compila manualmente un nickname e un valore `birthday_public` per il contatto di test
4. Esegui il bot in dry-run per verificare che le nuove feature funzionino
