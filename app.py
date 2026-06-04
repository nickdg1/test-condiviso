import streamlit as st
import qrcode
import sqlite3
import pandas as pd
import plotly.express as px
import io


# --- CONFIGURAZIONE DATABASE LOCAL SQLITE ---
def init_db():
    conn = sqlite3.connect('risposte_master.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS risposte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caso TEXT,
            q1 TEXT,
            q2 TEXT,
            q3 INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def salva_risposta(caso, q1, q2, q3):
    conn = sqlite3.connect('risposte_master.db')
    c = conn.cursor()
    c.execute('INSERT INTO risposte (caso, q1, q2, q3) VALUES (?, ?, ?, ?)', (caso, q1, q2, q3))
    conn.commit()
    conn.close()


def leggi_dati():
    conn = sqlite3.connect('risposte_master.db')
    df = pd.read_sql_query("SELECT * FROM risposte", conn)
    conn.close()
    return df


def reset_db():
    conn = sqlite3.connect('risposte_master.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS risposte')
    conn.commit()
    conn.close()
    init_db()


# Inizializza il database all'avvio
init_db()

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="Sistema Casi Interattivi", layout="wide")

# Configurazione dei 3 Casi di Studio
CASI = {
    "Caso 1": {
        "titolo": "Caso 1: Emergenza Infrastruttura Server",
        "descrizione": "Il server principale ha subito un picco di carico del 300% al minuto 45. I log mostrano connessioni anomale sulla porta 8080.",
        "immagine": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=500",
        # Sostituisci con file locali es. "caso1.jpg"
        "opzioni_q1": ["Bassa", "Media", "Critica"],
        "opzioni_q2": ["Riavviare il server", "Isolare la porta 8080", "Nessuna azione"]
    },
    "Caso 2": {
        "titolo": "Caso 2: Anomalie Flusso Logistico",
        "descrizione": "I tempi di consegna dell'hub centrale sono raddoppiati nelle ultime 24 ore. Il grafico mostra un blocco al reparto smistamento.",
        "immagine": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=500",
        "opzioni_q1": ["Lieve", "Moderato", "Grave"],
        "opzioni_q2": ["Aumentare i turni", "Raddoppiare i mezzi", "Cambiare corriere"]
    },
    "Caso 3": {
        "titolo": "Caso 3: Sicurezza dei Dati Clienti",
        "descrizione": "Rilevato tentativo di phishing massivo verso i dipendenti del reparto finanziario. Tre account hanno inserito le credenziali.",
        "immagine": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=500",
        "opzioni_q1": ["Contenuto", "Preoccupante", "Disastroso"],
        "opzioni_q2": ["Reset password forzato", "Isolare la rete", "Inviare email di avviso"]
    }
}

# ---NAVIGAZIONE RUOLI ---
# Usiamo la barra laterale per dividere nettamente Docente e Discente
st.sidebar.title("🔑 Controllo Accessi")
ruolo = st.sidebar.radio("Seleziona la tua interfaccia:", ["Discente (Smartphone)", "Docente (Proiezione e Dashboard)"])

# --- INTERFACCIA DISCENTE (SMARTPHONE) ---
if ruolo == "Discente (Smartphone)":
    st.title("📱 Rispondi al Caso Studio")

    # Selezione del caso su cui rispondere (agganciato al QR Code)
    # query_params permette di autoselezionare il caso se l'URL contiene ?caso=Caso1
    url_params = st.query_params
    caso_default = url_params.get("caso", "Caso 1")
    if caso_default not in CASI:
        caso_default = "Caso 1"

    caso_scelto = st.selectbox("Seleziona il Caso a cui stai rispondendo:", list(CASI.keys()),
                               index=list(CASI.keys()).index(caso_default))

    st.info(f"Stai rispondendo a: **{CASI[caso_scelto]['titolo']}**")

    # Form per l'invio delle risposte
    with st.form("quiz_form", clear_on_submit=True):
        st.subheader("Domande:")
        q1 = st.radio("1. Valutazione dell'impatto / gravità:", CASI[caso_scelto]["opzioni_q1"])
        q2 = st.selectbox("2. Quale azione immediata intraprenderesti?", CASI[caso_scelto]["opzioni_q2"])
        q3 = st.slider("3. Qual è il tuo livello di confidenza in questa scelta (1-10)?", 1, 10, 5)

        submit = st.form_submit_button("Invia Risposte 🚀")
        if submit:
            salva_risposta(caso_scelto, q1, q2, q3)
            st.success("Risposte inviate correttamente al docente! Puoi chiudere questa pagina.")

# --- INTERFACCIA DOCENTE (PROIEZIONE + GRAFICI) ---
else:
    st.title("👨‍🏫 Pannello di Controllo del Docente")

    tab1, tab2, tab3 = st.tabs(["📺 Proiezione Casi & QR", "📊 Risultati in Tempo Reale", "⚙️ Amministrazione & Reset"])

    # TAB 1: PRESENTAZIONE E GENERAZIONE QR
    with tab1:
        caso_da_presentare = st.radio("Seleziona il caso da proiettare a schermo:", list(CASI.keys()), horizontal=True)

        st.markdown("---")
        col_testo, col_qr = st.columns([2, 1])

        with col_testo:
            st.header(CASI[caso_da_presentare]["titolo"])
            st.write(CASI[caso_da_presentare]["descrizione"])
            st.image(CASI[caso_da_presentare]["immagine"], width=500)

        with col_qr:
            st.subheader("📱 Scansiona per rispondere")

            # Qui configuriamo l'indirizzo dinamico per lo smartphone del discente
            # Quando distribuisci l'app, sostituisci localhost con il vero URL pubblico o locale
            base_url = "http://test-condiviso-vxadys2qemxuwjgbgpelyn.streamlit.app/:8501"
            link_discente = f"{base_url}/?caso={caso_da_presentare.replace(' ', '+')}"

            # Generazione dinamica del QR Code
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(link_discente)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")

            buf = io.BytesIO()
            img_qr.save(buf, format="PNG")
            st.image(buf.getvalue(), caption="Inquadra con lo smartphone")
            st.caption(f"Link incorporato: [Apri modulo]({link_discente})")

    # TAB 2: GRAFICI AGGREGATI
    with tab2:
        st.header("📊 Analisi delle risposte dei discenti")
        df = leggi_dati()

        if df.empty:
            st.info("In attesa delle prime risposte da parte dei discenti...")
        else:
            caso_filtro = st.selectbox("Filtra i grafici per:", list(CASI.keys()), key="filtro_grafici")
            df_filtrato = df[df['caso'] == caso_filtro]

            if df_filtrato.empty:
                st.warning(f"Ancora nessuna risposta per il {caso_filtro}")
            else:
                st.metric("Totale Risposte Ricevute per questo caso", len(df_filtrato))

                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    # Grafico Domanda 1
                    fig1 = px.histogram(df_filtrato, x="q1", title="Distribuzione Gravità", color="q1",
                                        color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig1, use_container_width=True)
                with col_g2:
                    # Grafico Domanda 2
                    fig2 = px.pie(df_filtrato, names="q2", title="Scelta del Protocollo Intervento",
                                  color_discrete_sequence=px.colors.qualitative.Safe)
                    st.plotly_chart(fig2, use_container_width=True)

                # Media Domanda 3
                media_confidenza = df_filtrato['q3'].mean()
                st.metric("Livello medio di confidenza dei discenti", f"{media_confidenza:.1f} / 10")

                # Tabella dati grezzi
                with st.expander("Vedi dati grezzi"):
                    st.dataframe(df_filtrato)

    # TAB 3: RESET E AMMINISTRAZIONE
    with tab3:
        st.header("⚙️ Gestione Sessione")
        st.warning(
            "Attenzione: L'azione di reset eliminerà definitivamente tutte le risposte salvate nel database per tutti i casi.")

        # Bottone di reset sicuro con doppia conferma
        if st.button("🚨 AZZERA TUTTE LE RISPOSTE"):
            reset_db()
            st.success("Database azzerato con successo! Tutti i grafici sono stati ripuliti.")
            st.rerun()