import streamlit as st
import requests
from pathlib import Path

# -------------------------
# Configuration Streamlit
# -------------------------
st.set_page_config(
    page_title="RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# API URL
# -------------------------
API_URL = "http://127.0.0.1:8000"

# -------------------------
# CSS personnalisé
# -------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .chunk-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Header
# -------------------------
st.markdown('<p class="main-header">🤖 Système RAG - Question & Réponse</p>', unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("⚙️ État du système")

    # ---- Health check ----
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        if r.status_code == 200:
            data = r.json()
            st.success("✅ API connectée")
            st.metric("Vecteurs indexés", data.get("num_vectors", 0))
            st.info(f"Modèle: {data.get('embedding_model', 'N/A')}")
        else:
            st.error("❌ API hors ligne")
    except:
        st.error("❌ Impossible de joindre l'API")

    st.divider()

    # ---- Paramètres ----
    st.subheader("🔧 Recherche")
    top_k = st.slider("Nombre de chunks", 1, 10, 5)

    st.divider()

    # ---- Documents ----
    st.subheader("📚 Documents")
    try:
        docs = requests.get(f"{API_URL}/list_documents").json()
        if docs["total"] > 0:
            for doc in docs["documents"]:
                with st.expander(f"📄 {doc['filename']}"):
                    st.write(f"Chunks: {doc['num_chunks']}")
                    st.write(f"Caractères: {doc['total_characters']:,}")
        else:
            st.info("Aucun document indexé")
    except:
        st.warning("Impossible de charger les documents")

    st.divider()

    # ---- Clear index ----
    if st.button("🗑️ Vider l'index"):
        try:
            requests.delete(f"{API_URL}/clear_index")
            st.success("Index vidé")
            st.rerun()
        except:
            st.error("Erreur de connexion")

# =========================
# TABS
# =========================
tab1, tab2 = st.tabs(["📤 Upload", "❓ Question"])

# =========================
# TAB 1 — Upload
# =========================
with tab1:
    st.header("📤 Ajouter un document")

    uploaded_file = st.file_uploader("Choisir un fichier", type=["pdf", "docx", "txt"])

    if uploaded_file:
        st.write("Fichier:", uploaded_file.name)

        if st.button("🚀 Indexer"):
            with st.spinner("Indexation en cours..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    r = requests.post(f"{API_URL}/upload_document", files=files)

                    if r.status_code == 200:
                        data = r.json()
                        st.success("Document indexé")
                        st.metric("Chunks", data["num_chunks"])
                        st.metric("Caractères", data["num_characters"])
                    else:
                        st.error(r.text)
                except Exception as e:
                    st.error(str(e))

# =========================
# TAB 2 — Question & Réponse
# =========================
with tab2:
    st.header("❓ Posez une question")

    question = st.text_area("Votre question")

    if st.button("🔍 Rechercher"):
        if not question:
            st.warning("Entrez une question")
        else:
            with st.spinner("Recherche en cours..."):
                try:
                    # ✅ Correction ici : envoyer "question" et non "query"
                    r = requests.post(
                        f"{API_URL}/query",
                        json={"question": question, "top_k": top_k}
                    )

                    if r.status_code == 200:
                        data = r.json()

                        st.subheader("💡 Réponse")
                        st.success(data["answer"])

                        st.divider()
                        st.subheader("📄 Passages")

                        for i, c in enumerate(data["retrieved_chunks"], 1):
                            with st.expander(f"{i}. {c['document_name']} (score {c['score']:.3f})"):
                                st.markdown(c["content"])

                    else:
                        st.error(r.text)

                except Exception as e:
                    st.error(str(e))

# =========================
# FOOTER
# =========================
st.divider()
st.markdown(
    "<center>FastAPI RAG • <a href='http://127.0.0.1:8000/docs' target='_blank'>API Docs</a></center>",
    unsafe_allow_html=True
)
