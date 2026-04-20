# Come pubblicare la landing page su GitHub Pages

## Prerequisiti

- La repo del progetto deve essere su GitHub (pubblica o privata con piano pro/team).
- Devi avere accesso alle impostazioni della repo.

---

## Passaggi

### 1. Copia la foto di Carlo nella cartella docs

Copia il file `data/photos/carloRe.png` dentro questa cartella `docs/`:

```
docs/
├── index.html
├── carloRe.png    ← copia qui
└── README.md
```

### 2. Inserisci l'URL del Google Form

Apri `docs/index.html` e sostituisci il placeholder con il link reale al form:

```html
href="INSERISCI_QUI_URL_DEL_FORM"
```

L'URL del form lo trovi aprendo il form in modifica → **Invia** → icona del link → **Copia**.

### 3. Fai il commit e push di tutto

```bash
git add docs/
git commit -m "feat: aggiungi landing page GitHub Pages"
git push
```

### 4. Abilita GitHub Pages

1. Vai sulla repo GitHub → **Settings** → **Pages** (nel menu laterale).
2. Sotto **"Branch"**, seleziona:
   - Branch: `main` (o il tuo branch principale)
   - Cartella: `/docs`
3. Clicca **Save**.

GitHub impiegherà circa 1-2 minuti a pubblicare la pagina.

### 5. Accedi alla pagina

L'URL sarà nel formato:

```
https://[tuo-username].github.io/[nome-repo]/
```

Lo trovi anche nella stessa schermata Settings → Pages dopo la pubblicazione.

---

## Note

- Ogni volta che fai push di modifiche a `docs/`, GitHub Pages si aggiorna automaticamente.
- Se vuoi un dominio personalizzato (es. `carlobot.it`), puoi configurarlo nella stessa schermata Pages sotto "Custom domain".
- La pagina funziona anche offline aprendo `docs/index.html` direttamente nel browser per testarla prima del deploy.
