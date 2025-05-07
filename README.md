# 📦 Listino B2B4U - Web App

Questa applicazione Streamlit consente di visualizzare un listino prodotti B2B con filtri dinamici, richiesta offerte via email e gestione selezioni.

---

## 🚀 Avvio locale

### 1. Clona o scarica il progetto nella tua cartella:
```bash
cd percorso/del/progetto
```

### 2. Crea un ambiente virtuale (opzionale ma consigliato):
```bash
python -m venv venv
venv\Scripts\activate  # Su Windows
source venv/bin/activate  # Su Mac/Linux
```

### 3. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

### 4. Avvia l'app Streamlit:
```bash
streamlit run catalogo_B2B.py
```

---

## 📋 Requisiti

- Python 3.9 o superiore
- Connessione internet per l'invio delle email
- File `listino_B2B.csv` nella stessa cartella

---

## 📧 Invio Offerte

Lo script invia email tramite SMTP di Microsoft 365 (`smtp.office365.com`). Configura i seguenti dati nello script:

```python
SMTP_USER = "info@el4u.it"
SMTP_PASSWORD = "LA_TUA_PASSWORD"
```

---

## ✅ Funzionalità

- Filtri per marchio e categoria multilivello
- Ricerca libera
- Selezione multipla con quantità
- Modulo per richiesta offerta via email
- Riepilogo selezioni con tabella
- Navigazione su più pagine
- Supporto schede tecniche (Icecat)

---

## 📁 File principali

- `catalogo_B2B.py` → Script principale Streamlit
- `listino_B2B.csv` → Dati del listino da visualizzare
- `requirements.txt` → Librerie da installare
- `README.md` → Questa guida

---

## 🔐 Sicurezza

Non committare mai il file con password SMTP nei repository pubblici!
Ultimo aggiornamento: 2025-05-07 16:57:15
