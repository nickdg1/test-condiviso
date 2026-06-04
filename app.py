import streamlit as st
import qrcode
import pandas as pd
import plotly.express as px
import io
import os

# --- GESTIONE DATI COMPATIBILE CON STREAMLIT CLOUD (CSV in /tmp) ---
CSV_PATH = "/tmp/risposte_docente.csv"


def init_db():
    if not os.path.exists(CSV_PATH):
        df = pd.DataFrame(columns=["caso", "q1", "q2", "q3"])
        df.to_csv(CSV_PATH, index=False)


def salva_risposta(caso, q1, q2, q3):
    init_db()
    df = pd.read_csv(CSV_PATH)
    nuova_riga = pd.DataFrame([{"caso": caso, "q1": q1, "q2": q2, "q3": q3}])
    df = pd.concat([df, nuova_riga], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)


def leggi_dati():
    init_db()
    try:
        return pd.read_csv(CSV_PATH)
    except:
        return pd.DataFrame(columns=["caso", "q1", "q2", "q3"])


def reset_db():
    if os.path.exists(CSV_PATH):
        os.remove(CSV_PATH)
    init_db()


# Inizializzazione immediata
init_db()

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="Sistema Casi Interattivi", layout="wide")

# I tuoi 3 Casi di Studio
CASI = {
    "caso1": {
        "titolo": "Caso 1: Emergenza Infrastruttura Server",
        "descrizione": "Il server principale ha subito un picco di carico del 300% al minuto 45. I log mostrano connessioni anomale sulla porta 8080.",
        "immagine": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=500",
        "opzioni_q1": ["Bassa", "Media", "Critica"],
        "opzioni_q2": ["Riavviare il server", "Isolare la porta 8080", "Nessuna azione"]
    },
    "caso2": {
        "titolo": "Caso 2: Anomalie Flusso Logistico",
        "descrizione": "I tempi di consegna dell'hub centrale sono raddoppiati nelle ultime 24 ore. Il grafico mostra un blocco al reparto smistamento.",
        "immagine": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=500",
        "opzioni_q1": ["Lieve", "Moderato", "Grave"],
        "opzioni_q2": ["Aumentare i turni", "Raddoppiare i mezzi", "Cambiare corriere"]
    },
    "caso3": {
        "titolo": "Caso 3: Sicurezza dei Dati Clienti",
        "descrizione": "Rilevato tentativo di phishing massivo verso i dipendenti del reparto finanziario. Tre account hanno inserito le credenziali.",
        "immagine": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=500",
        "opzioni_q1": ["Contenuto", "Preoccupante", "Disastroso"],
        "opzioni_q2": ["Reset password forzato", "Isolare la rete", "Inviare email di avviso"]
    }
}

NOMI_MENU = {"caso1": "Caso 1", "caso2": "Caso 2", "caso3": "Caso 3"}

# --- NAVIGAZIONE RUOLI (Menu laterale modificato per Smartphone) ---
st.sidebar.title("🔑 Ruolo")
# Riconoscimento automatico: se l'URL contiene il parametro del caso, imposta la modalità discente di default
URL_PARAMS = st.query_params
default_ruolo_index = 0
if "caso" in URL_PARAMS:
    default_ruolo_index = 0
else:
    default_ruolo_index = 1  # Se apre la home pulita, mostra il pannello docente

ruolo = st.sidebar.radio("Interfaccia:", ["Discente (Smartphone)", "Docente (Dashboard)"], index=default_ruolo_index)

# --- INTERFACCIA DISCENTE ---
if ruolo == "Discente (Smartphone)":
    st.title("📱 Rispondi al Caso Studio")

    caso_default = "caso1"
    if "caso" in URL_PARAMS:
        param_val = URL_PARAMS["caso"]
        if param_val in CASI:
            caso_default = param_val

    caso_scelto = st.selectbox(
        "Seleziona il Caso:",
        list(CASI.keys()),
        index=list(CASI.keys()).index(caso_default),
        format_func=lambda x: NOMI_MENU[x]
    )

    st.info(f"**{CASI[caso_scelto]['titolo']}**")

    with st.form("quiz_form", clear_on_submit=True):
        q1 = st.radio("1. Livello di gravità:", CASI[caso_scelto]["opzioni_q1"])
        q2 = st.selectbox("2. Azione immediata consigliata:", CASI[caso_scelto]["opzioni_q2"])
        q3 = st.slider("3. Sicurezza della scelta (1-10):", 1, 10, 5)

        if st.form_submit_button("Invia Risposte 🚀"):
            salva_risposta(caso_scelto, q1, q2, q3)
            st.success("Risposte inviate! I grafici del docente si stanno aggiornando.")

# --- INTERFACCIA DOCENTE ---
else:
    st.title("👨‍🏫 Pannello di Controllo Docente")
    tab1, tab2, tab3 = st.tabs(["📺 Proiezione & QR", "📊 Grafici Risposte", "⚙️ Reset"])

    with tab1:
        caso_da_presentare = st.radio("Caso attuale:", list(CASI.keys()), horizontal=True,
                                      format_func=lambda x: NOMI_MENU[x])
        st.write("---")
        col_testo, col_qr = st.columns([2, 1])

        with col_testo:
            st.header(CASI[caso_da_presentare]["titolo"])
            st.write(CASI[caso_da_presentare]["descrizione"])
            st.image(CASI[caso_da_presentare]["immagine"], width=450)

        with col_qr:
            st.subheader("📱 QR Code Aula")
            base_url = "https://test-condiviso-vxadys2qemxuwjgbgpelyn.streamlit.app"
            link_discente = f"{base_url}/?caso={caso_da_presentare}"

            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(link_discente)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")

            buf = io.BytesIO()
            img_qr.save(buf, format="PNG")
            st.image(buf.getvalue(), caption="Inquadra per rispondere")

    with tab2:
        st.header("📊 Statistiche Ricevute")
        df = leggi_dati()

        if df.empty:
            st.info("Nessuna risposta presente nel sistema.")
        else:
            caso_filtro = st.selectbox("Filtra grafici:", list(CASI.keys()), format_func=lambda x: NOMI_MENU[x])
            df_filtrato = df[df['caso'] == caso_filtro]

            if df_filtrato.empty:
                st.warning("Nessun dato per questo caso.")
            else:
                st.metric("Risposte totali riceveute", len(df_filtrato))
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    fig1 = px.histogram(df_filtrato, x="q1", title="Impatto Rilevato", color="q1")
                    st.plotly_chart(fig1, use_container_width=True)
                with col_g2:
                    fig2 = px.pie(df_filtrato, names="q2", title="Protocolli scelti")
                    st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.header("⚙️ Pulizia Sistema")
        if st.button("🚨 AZZERA TUTTE LE RISPOSTE"):
            reset_db()
            st.success("Tutte le risposte dei discenti sono state eliminate.")
            st.rerun()