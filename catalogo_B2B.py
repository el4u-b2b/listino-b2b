import streamlit as st
import pandas as pd
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import numpy as np

# === Configurazione SMTP ===
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
SMTP_USER = "info@el4u.it"
SMTP_PASSWORD = st.secrets["SMTP_PASSWORD"]
EMAIL_DESTINATARIO = "info@el4u.it"

st.set_page_config(page_title="Listino B2B", layout="wide")

PIN_CORRETTO = st.secrets["ACCESS_PIN"]

# Inizializza lo stato di accesso
if "access_granted" not in st.session_state:
    st.session_state.access_granted = False

# === Bypass da URL ===
# Solo al primo giro, se il PIN è nella query string, salvalo
if not st.session_state.access_granted and "pin_checked" not in st.session_state:
    query_pin = st.query_params.get("pin", [""])[0]
    if query_pin == PIN_CORRETTO:
        st.session_state.access_granted = True
    st.session_state.pin_checked = True
    st.rerun()

# === Accesso manuale ===
if not st.session_state.access_granted:
    col1, col2, col3 = st.columns([2, 1.5, 2])
    with col2:
        pin_input = st.text_input("🔐 Inserisci PIN per accedere", type="password")
        if pin_input == PIN_CORRETTO:
            st.session_state.access_granted = True
            st.rerun()
        else:
            st.stop()

def load_data():
    return pd.read_csv("listino_B2B.csv", dtype=str)

# === Funzione invio email ===
def send_email(subject, body_html, destinatario):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = destinatario

    part = MIMEText(body_html, "html")
    msg.attach(part)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

# === Caricamento dati ===
data = load_data()

# === Pulizia prezzi ===
def format_price(price):
    try:
        return f"{float(price):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return ""

data['prezzo_vendita'] = data['prezzo_vendita'].apply(format_price)
data['prezzo_pubblico'] = data['prezzo_pubblico'].apply(format_price)

# === Stato sessione ===
if 'selected_products' not in st.session_state:
    st.session_state.selected_products = {}
if 'show_offer_form' not in st.session_state:
    st.session_state.show_offer_form = False
if 'page' not in st.session_state:
    st.session_state.page = 1

# === Funzione per reset pagina ===
def reset_page():
    st.session_state.page = 1

# === Sidebar ===
with st.sidebar:
    st.image("logo.png", width=200)
    st.title("Filtri")

    if st.button("Reset filtri"):
        st.session_state.filter_marchio = "Tutti"
        st.session_state.filter_cat1 = "Tutte"
        st.session_state.filter_cat2 = "Tutte"
        st.session_state.filter_cat3 = "Tutte"
        st.session_state.filter_search = ""
        st.session_state.page = 1
        st.rerun()

    selected_search = st.text_input("Ricerca prodotto", key="filter_search", on_change=reset_page)

# === Filtri dinamici ===
search_val = st.session_state.get("filter_search", "")
marchio_val = st.session_state.get("filter_marchio", "Tutti")
cat1_val = st.session_state.get("filter_cat1", "Tutte")
cat2_val = st.session_state.get("filter_cat2", "Tutte")
cat3_val = st.session_state.get("filter_cat3", "Tutte")

mask = np.ones(len(data), dtype=bool)
if search_val:
    mask &= data['descrizione'].str.contains(search_val, case=False, na=False)
if marchio_val != "Tutti":
    mask &= data['marchio'] == marchio_val
if cat1_val != "Tutte":
    mask &= data['categoria1'] == cat1_val
if cat2_val != "Tutte":
    mask &= data['categoria2'] == cat2_val
if cat3_val != "Tutte":
    mask &= data['categoria3'] == cat3_val

filtered = data[mask]

available_marchi = sorted(data[mask]['marchio'].dropna().unique())
available_cat1 = sorted(data[mask]['categoria1'].dropna().unique())
available_cat2 = sorted(data[mask]['categoria2'].dropna().unique())
available_cat3 = sorted(data[mask]['categoria3'].dropna().unique())

with st.sidebar:
    marchio_options = ["Tutti"] + available_marchi
    cat1_options = ["Tutte"] + available_cat1
    cat2_options = ["Tutte"] + available_cat2
    cat3_options = ["Tutte"] + available_cat3

    st.selectbox("Marchio", marchio_options, key="filter_marchio", index=marchio_options.index(marchio_val) if marchio_val in marchio_options else 0, on_change=reset_page)
    st.selectbox("Categoria 1° livello", cat1_options, key="filter_cat1", index=cat1_options.index(cat1_val) if cat1_val in cat1_options else 0, on_change=reset_page)
    st.selectbox("Categoria 2° livello", cat2_options, key="filter_cat2", index=cat2_options.index(cat2_val) if cat2_val in cat2_options else 0, on_change=reset_page)
    st.selectbox("Categoria 3° livello", cat3_options, key="filter_cat3", index=cat3_options.index(cat3_val) if cat3_val in cat3_options else 0, on_change=reset_page)

# === Paginazione ===
ITEMS_PER_PAGE = 50

def get_paginated_data(dataframe, page):
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    return dataframe.iloc[start:end], start + 1, min(end, len(dataframe))

total_pages = max(1, (len(filtered) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
if st.session_state.page > total_pages:
    st.session_state.page = 1
paginated, start_idx, end_idx = get_paginated_data(filtered, st.session_state.page)

# === Titolo finestra ===
st.title("Listino EL4U B2B")
st.markdown("Utilizza le funzioni di ricerca, seleziona i prodotti, modifica la quantità poi vai a fondo pagina per richiedere una quotazione personalizzata.")

# === Deseleziona tutto ===
if st.button("❌ Deseleziona tutti i prodotti"):
    st.session_state.selected_products.clear()
    for key in list(st.session_state.keys()):
        if key.startswith("checkbox_"):
            st.session_state[key] = False
    st.session_state.page = 1
    st.rerun()


# === Tabella corretta ===
header_cols = st.columns([0.4, 0.6, 1.0, 1.0, 1.5, 3.0, 1.2, 1.2, 1.0])
header_cols[0].markdown("**S**")
header_cols[1].markdown("**Qtà**")
header_cols[2].markdown("**SKU**")
header_cols[3].markdown("**Img**")
header_cols[4].markdown("**Marchio**")
header_cols[5].markdown("**Descrizione**")
header_cols[6].markdown("**B2B i.c.**")
header_cols[7].markdown("**Pubblico**")
header_cols[8].markdown("**Scheda**")

for idx, row in paginated.iterrows():
    sku = row['sku']
    cols = st.columns([0.4, 0.6, 1.0, 1.0, 1.5, 3.0, 1.2, 1.2, 1.0])

    checkbox_key = f"checkbox_{sku}"
    qty_key = f"qty_{sku}"

    selected = cols[0].checkbox(" ", key=checkbox_key, value=sku in st.session_state.selected_products, label_visibility="collapsed")
    quantity = cols[1].number_input(" ", min_value=1, max_value=9999, value=1, step=1, key=qty_key, label_visibility="collapsed")

    thumb_url = row['thumb_url'] if pd.notna(row['thumb_url']) and row['thumb_url'].strip() else "noimage.png"
    cols[3].image(thumb_url, width=60)

    cols[2].markdown(sku)
    cols[4].markdown(row['marchio'])
    cols[5].markdown(row['descrizione'])
    cols[6].markdown(f"{row['prezzo_vendita']} €")
    cols[7].markdown(f"{row['prezzo_pubblico']} €")
    if pd.notna(row['link_icecat']) and row['link_icecat'].strip():
        cols[8].markdown(f"[📄 Scheda]({row['link_icecat']})")
    else:
        cols[8].markdown("")

    if selected:
        st.session_state.selected_products[sku] = {
            "sku": sku,
            "Descrizione": row['descrizione'],
            "Marchio": row['marchio'],
            "Prezzo B2B i.c.": row['prezzo_vendita'],
            "Prezzo pubblico": row['prezzo_pubblico'],
            "Quantità": quantity
        }
    else:
        st.session_state.selected_products.pop(sku, None)

# === Navigazione ===
col_prev, col_info, col_next = st.columns([1, 2, 1])
with col_prev:
    if st.button("◀ Pagina precedente") and st.session_state.page > 1:
        st.session_state.page -= 1
        st.rerun()
with col_info:
    st.markdown(f"<center>Articoli da {start_idx} a {end_idx} di {len(filtered)} - Pagina {st.session_state.page} di {total_pages}</center>", unsafe_allow_html=True)
with col_next:
    if st.button("Pagina successiva ▶") and st.session_state.page < total_pages:
        st.session_state.page += 1
        st.rerun()

# === Richiedi Offerta ===
if st.button("✉️ Richiedi Offerta"):
    if not st.session_state.selected_products:
        st.warning("Seleziona almeno un prodotto per richiedere un'offerta!")
    else:
        st.session_state.show_offer_form = True

if st.session_state.show_offer_form:
    st.markdown("---")
    with st.container():
        st.subheader("Compila con i tuoi dati per ricevere un'offerta")
        azienda = st.text_input("Ragione Sociale")
        email_cliente = st.text_input("Email Cliente")
        telefono = st.text_input("Telefono Cliente")
        note = st.text_area("Note aggiuntive", "")

        if st.session_state.selected_products:
            st.subheader("Prodotti selezionati")
            riepilogo = pd.DataFrame.from_dict(st.session_state.selected_products, orient='index')
            st.table(riepilogo.set_index('sku'))

        col_a, col_b = st.columns(2)
        with col_a:
            invia = st.button("Invia Richiesta")
        with col_b:
            chiudi = st.button("Chiudi")

        if chiudi:
            st.session_state.show_offer_form = False
            st.rerun()

        if invia:
            if not (azienda and email_cliente and telefono):
                st.error("Compila tutti i campi obbligatori!")
            else:
                corpo_html = f"""
<html><body>
<img src='https://www.el4u.it/media/logo/stores/3/EL4U_1_4_.png' width='200'/><br><br>
Gentile {azienda},<br>Grazie per averci contattato. Ecco il riepilogo della sua richiesta:<br><br>
<b>Dati Cliente:</b><br>Email: {email_cliente}<br>Telefono: {telefono}<br>Note: {note}<br><br>
<table border='1' cellspacing='0' cellpadding='5'>
<tr><th>sku</th><th>Descrizione</th><th>Marchio</th><th>Prezzo B2B i.c.</th><th>Prezzo Pubblico</th><th>Quantità</th></tr>
"""
                for sku, info in st.session_state.selected_products.items():
                    corpo_html += f"<tr><td>{info['sku']}</td><td>{info['Descrizione']}</td><td>{info['Marchio']}</td><td>{info['Prezzo B2B i.c.']} €</td><td>{info['Prezzo pubblico']} €</td><td>{info['Quantità']}</td></tr>"
                corpo_html += """
</table><br>
Il nostro staff la contatterà a breve per un'offerta personalizzata.<br><br>
Cordiali saluti,<br><b>Team EL4U</b><br>
info@el4u.it | Wapp: +39 0432 664744</body></html>
"""
                try:
                    send_email(f"Richiesta Offerta da {azienda}", corpo_html, EMAIL_DESTINATARIO)
                    send_email(f"Conferma Richiesta Offerta", corpo_html, email_cliente)
                    st.session_state.show_offer_form = False
                    st.session_state.selected_products.clear()
                    st.success("✅ Offerta inviata con successo! Ti abbiamo inviato anche una copia della richiesta.")
                except Exception as e:
                    st.error(f"Errore nell'invio della richiesta: {e}")


# === Footer ===
st.markdown("""
---
**Di.S.eL. S.r.l.**  
Via G.B. Maddalena 1, Povoletto (UD)  
P.IVA: 00472220318  
Contatti: info@el4u.it | Wapp: +39 0432 664744  
[Condizioni di vendita](https://www.el4u.it/condizioni-di-vendita) | [Privacy](https://www.el4u.it/privacy)
""")

try:
    file_time = os.path.getmtime("listino_B2B.csv")
    dt = datetime.fromtimestamp(file_time).strftime("%d/%m/%Y")
    st.markdown(f"<br><i>Ultimo aggiornamento: {dt}</i>", unsafe_allow_html=True)
except:
    pass