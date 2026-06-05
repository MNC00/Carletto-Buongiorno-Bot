# Guida: Configurazione Google per Compleanni e Nickname

## 1. Google Form — Aggiungere data di nascita e preferenza auguri

1. Apri il Google Form collegato al foglio `users`
2. Clicca **"Aggiungi domanda"** (icona `+`) per la data di nascita
3. Seleziona il tipo **"Data"**
4. Titolo della domanda: **`Data di nascita`**
5. Nelle opzioni della domanda della data (⋮):
   - Disattiva **"Includi anno"** se vuoi solo giorno/mese, oppure lascialo attivo (il bot usa solo giorno e mese)
   - Scegli se rendere la domanda **obbligatoria** o facoltativa
6. Aggiungi una seconda domanda per la preferenza sugli auguri
7. Seleziona il tipo **"Scelta multipla"**
8. Titolo esatto della domanda: **`Auguri di compleanno pubblici?`**
9. Opzioni consigliate:
   - **`Sì, condividi gli auguri con tutti gli iscritti`**
   - **`No, invia gli auguri solo a me`**
10. Rendi questa domanda **obbligatoria**, cosi ogni nuovo iscritto sceglie esplicitamente
11. Posiziona le domande dove preferisci nel form
12. Invia una risposta di test e verifica che le colonne **"Data di nascita"** e **"Auguri di compleanno pubblici?"** appaiano nel foglio `users`

> **Nota**: il formato della data nel foglio dipende dal locale del Google Sheet. Il bot supporta i formati `GG/MM/AAAA`, `AAAA-MM-GG` e `GG-MM-AAAA`.

> **Importante**: il titolo **`Auguri di compleanno pubblici?`** deve combaciare con la variabile `BIRTHDAY_PUBLIC_FIELD_TITLE` in `grant_access.gs`.

---

## 2. Google Sheet — Colonne manuali e tecniche

Apri il foglio `users` dello spreadsheet collegato al form.

### Colonna `nickname`
1. Vai alla **prima colonna vuota** dopo le colonne esistenti
2. Nella cella dell'header (riga 1), scrivi: **`nickname`**
3. Compila manualmente il nickname per i contatti che vuoi personalizzare
4. Lascia vuoto per gli altri — il bot userà il nome

### Colonna `birthday_public`
1. Questa colonna viene creata automaticamente da `grant_access.gs` se non esiste
2. Header atteso: **`birthday_public`**
3. Per i nuovi iscritti viene compilata automaticamente in base alla risposta alla domanda **`Auguri di compleanno pubblici?`**:
   - `true` (default) → gli auguri di compleanno sono visibili a **tutti** gli iscritti
   - `false` → gli auguri vengono inviati **solo** al festeggiato
4. Per i contatti gia esistenti puoi compilarla o correggerla manualmente con **`true`** o **`false`**
5. Se la cella è vuota, il bot usa il default `true`

> **Importante**: `nickname` resta manuale. `birthday_public` resta una colonna tecnica del foglio, ma per i nuovi iscritti viene popolata automaticamente dallo script in base alla risposta del modulo.

---

## 3. Apps Script — Aggiornare `grant_access.gs`

Lo script è già stato aggiornato nel codice della repo. Per applicare le modifiche:

1. Apri il Google Form → menu **⋮** → **Editor di script** (Apps Script)
2. Apri il file `grant_access.gs`
3. Nella sezione **CONFIGURAZIONE** in alto, verifica che ci siano le variabili:
   ```javascript
   var BIRTHDAY_PUBLIC_FIELD_TITLE = "Auguri di compleanno pubblici?";
   var NICKNAME_COLUMN_TITLE = "nickname";
   var BIRTHDAY_PUBLIC_COLUMN_TITLE = "birthday_public";
   ```
4. Nella funzione `_ensureTechnicalColumns()`, verifica che `requiredHeaders` includa le nuove colonne:
   ```javascript
   var requiredHeaders = [ACTIVE_COLUMN_TITLE, UNSUBSCRIBED_AT_COLUMN_TITLE, NICKNAME_COLUMN_TITLE, BIRTHDAY_PUBLIC_COLUMN_TITLE];
   ```
5. Salva il file (Ctrl+S)
6. **Non serve re-deployare** — il trigger `onFormSubmit` usa automaticamente il codice aggiornato

> **Nota**: al prossimo invio del form, se le colonne `nickname` e `birthday_public` non esistono ancora nel foglio, lo script le creerà automaticamente. Inoltre scriverà `true` o `false` in `birthday_public` per la riga attiva.

---

## 4. Verifica

1. Invia una risposta di test dal Google Form con una data di nascita e scegli **"Sì, condividi gli auguri con tutti gli iscritti"**
2. Apri il foglio `users` e verifica:
   - La colonna **"Data di nascita"** è stata popolata
   - La colonna **"Auguri di compleanno pubblici?"** contiene la risposta del form
   - La colonna **"birthday_public"** contiene **`true`**
3. Invia una seconda risposta di test scegliendo **"No, invia gli auguri solo a me"**
4. Verifica che la nuova riga attiva abbia **`birthday_public=false`**
5. Se hai usato la stessa email, verifica che le righe precedenti siano **`active=false`** e l'ultima sia **`active=true`**
6. Compila manualmente un nickname per il contatto di test, se vuoi verificare anche il saluto personalizzato
7. Esegui il bot in dry-run per verificare che le nuove feature funzionino
