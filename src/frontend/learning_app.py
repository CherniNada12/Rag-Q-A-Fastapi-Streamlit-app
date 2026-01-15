import streamlit as st
import requests
from pathlib import Path
import time

# -------------------------
# Configuration
# -------------------------
st.set_page_config(
    page_title="📚 Learning Assistant RAG",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000"

# -------------------------
# CSS Personnalisé
# -------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .question-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .answer-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1E88E5;
        margin: 1rem 0;
    }
    .source-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #ffc107;
        margin: 0.5rem 0;
    }
    .suggestion-btn {
        background-color: #e3f2fd;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 1px solid #90caf9;
        margin: 0.3rem;
        display: inline-block;
    }
    .level-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    .beginner { background-color: #c8e6c9; color: #2e7d32; }
    .intermediate { background-color: #fff9c4; color: #f57f17; }
    .advanced { background-color: #ffcdd2; color: #c62828; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Session State
# -------------------------
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'learning_level' not in st.session_state:
    st.session_state.learning_level = 'intermediate'

# -------------------------
# Header
# -------------------------
st.markdown('<p class="main-header">📚 Learning Assistant RAG</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Votre assistant pédagogique intelligent</p>', unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Health check
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        if r.status_code == 200:
            data = r.json()
            st.success("✅ Système opérationnel")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📚 Documents", data.get("num_vectors", 0))
            with col2:
                st.metric("🎓 Niveau", st.session_state.learning_level.title())
    except:
        st.error("❌ API hors ligne")
    
    st.divider()
    
    # Niveau d'apprentissage
    st.subheader("🎓 Niveau d'apprentissage")
    level = st.radio(
        "Choisissez votre niveau :",
        ["Débutant", "Intermédiaire", "Avancé"],
        index=1
    )
    
    level_map = {
        "Débutant": "beginner",
        "Intermédiaire": "intermediate",
        "Avancé": "advanced"
    }
    st.session_state.learning_level = level_map[level]
    
    # Informations du niveau
    level_info = {
        "beginner": "💡 Explications simples avec exemples",
        "intermediate": "📖 Explications détaillées et structurées",
        "advanced": "🎯 Analyse approfondie et technique"
    }
    st.info(level_info[st.session_state.learning_level])
    
    st.divider()
    
    # Paramètres de recherche
    st.subheader("🔍 Paramètres")
    top_k = st.slider("Sources à récupérer", 1, 10, 5)
    
    st.divider()
    
    # Documents indexés
    st.subheader("📚 Cours indexés")
    try:
        docs = requests.get(f"{API_URL}/list_documents").json()
        if docs["total"] > 0:
            for doc in docs["documents"]:
                with st.expander(f"📄 {doc['filename']}"):
                    st.write(f"📊 Sections : {doc['num_chunks']}")
                    st.write(f"📝 Caractères : {doc['total_characters']:,}")
        else:
            st.info("Aucun cours indexé")
    except:
        st.warning("Impossible de charger les cours")
    
    st.divider()
    
    # Actions
    if st.button("🗑️ Réinitialiser l'index"):
        try:
            requests.delete(f"{API_URL}/clear_index")
            st.success("Index réinitialisé")
            st.rerun()
        except:
            st.error("Erreur")
    
    if st.button("🔄 Nouvelle session"):
        st.session_state.conversation_history = []
        st.rerun()

# =========================
# MAIN CONTENT - TABS
# =========================
tab1, tab2, tab3 = st.tabs(["💬 Assistant", "📤 Upload Cours", "📊 Historique"])

# =========================
# TAB 1 - ASSISTANT
# =========================
with tab1:
    st.header("💬 Posez vos questions")
    
    # Zone de question avec exemples
    st.markdown("### ❓ Votre question")
    
    # Suggestions de questions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💡 C'est quoi ... ?"):
            st.session_state.example_question = "C'est quoi le machine learning ?"
    with col2:
        if st.button("🔍 Comment ... ?"):
            st.session_state.example_question = "Comment fonctionne un réseau de neurones ?"
    with col3:
        if st.button("📋 Exemple de ... ?"):
            st.session_state.example_question = "Donne-moi un exemple d'algorithme supervisé"
    
    # Question principale
    question = st.text_area(
        "Tapez votre question ici :",
        value=st.session_state.get('example_question', ''),
        height=100,
        placeholder="Ex: Explique-moi le concept de gradient descent..."
    )
    
    col_search, col_clear = st.columns([3, 1])
    with col_search:
        search_button = st.button("🔍 Rechercher", type="primary", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Effacer"):
            st.session_state.example_question = ''
            st.rerun()
    
    if search_button and question:
        with st.spinner("🤔 Recherche et analyse en cours..."):
            try:
                # Appel API
                response = requests.post(
                    f"{API_URL}/query",
                    json={
                        "question": question,
                        "top_k": top_k
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Sauvegarder dans l'historique
                    st.session_state.conversation_history.append({
                        'question': question,
                        'answer': data['answer'],
                        'sources': data.get('sources', []),
                        'question_type': data.get('question_type', 'general'),
                        'level': st.session_state.learning_level
                    })
                    
                    # Afficher la question
                    st.markdown(f"""
                    <div class="question-box">
                        <strong>❓ Votre question :</strong><br>
                        {question}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Afficher le type et niveau
                    col_type, col_level = st.columns([3, 1])
                    with col_type:
                        st.info(f"📑 Type : **{data.get('question_type', 'général').title()}**")
                    with col_level:
                        level_class = st.session_state.learning_level
                        st.markdown(f'<span class="level-badge {level_class}">{level.upper()}</span>', unsafe_allow_html=True)
                    
                    # Afficher la réponse
                    st.markdown("### 💡 Réponse")
                    st.markdown(f"""
                    <div class="answer-box">
                        {data['answer']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Suggestions de suivi
                    if 'follow_up_suggestions' in data and data['follow_up_suggestions']:
                        st.markdown("### 🎯 Questions de suivi suggérées")
                        for sugg in data['follow_up_suggestions']:
                            if st.button(f"💭 {sugg}"):
                                st.session_state.example_question = sugg
                                st.rerun()
                    
                    # Sources
                    if data.get('sources'):
                        st.markdown("### 📚 Sources utilisées")
                        for i, source in enumerate(data['sources'], 1):
                            st.markdown(f"""
                            <div class="source-box">
                                <strong>Source {i}</strong><br>
                                📄 Document: {source.get('document', 'N/A')}<br>
                                🎯 Pertinence: {source.get('score', 0):.2%}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error(f"Erreur : {response.text}")
                    
            except Exception as e:
                st.error(f"Erreur de connexion : {str(e)}")

# =========================
# TAB 2 - UPLOAD
# =========================
with tab2:
    st.header("📤 Ajouter un cours")
    
    st.info("💡 Formats acceptés : PDF, DOCX, TXT")
    
    uploaded_file = st.file_uploader(
        "Choisissez un fichier de cours",
        type=["pdf", "docx", "txt"]
    )
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Fichier :**", uploaded_file.name)
        with col2:
            st.write("**Taille :**", f"{uploaded_file.size / 1024:.1f} KB")
        
        if st.button("🚀 Indexer le cours", type="primary"):
            with st.spinner("⏳ Indexation en cours..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    r = requests.post(f"{API_URL}/upload_document", files=files)
                    
                    if r.status_code == 200:
                        data = r.json()
                        st.success("✅ Cours indexé avec succès !")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📊 Sections", data["num_chunks"])
                        with col2:
                            st.metric("📝 Caractères", f"{data['num_characters']:,}")
                        with col3:
                            st.metric("🎯 Total vecteurs", data["total_vectors"])
                        
                        st.balloons()
                    else:
                        st.error(f"Erreur : {r.text}")
                except Exception as e:
                    st.error(f"Erreur : {str(e)}")

# =========================
# TAB 3 - HISTORIQUE
# =========================
with tab3:
    st.header("📊 Historique des conversations")
    
    if st.session_state.conversation_history:
        for i, conv in enumerate(reversed(st.session_state.conversation_history)):
            with st.expander(f"Question {len(st.session_state.conversation_history) - i}: {conv['question'][:60]}..."):
                st.markdown(f"**❓ Question :** {conv['question']}")
                st.markdown(f"**💡 Réponse :** {conv['answer']}")
                st.markdown(f"**📑 Type :** {conv.get('question_type', 'N/A')}")
                st.markdown(f"**🎓 Niveau :** {conv.get('level', 'N/A')}")
                
                if conv.get('sources'):
                    st.markdown("**📚 Sources :**")
                    for source in conv['sources']:
                        st.write(f"- {source.get('document', 'N/A')}")
    else:
        st.info("Aucune conversation enregistrée")

# =========================
# FOOTER
# =========================
st.divider()
st.markdown(
    """
    <center>
        <p>🤖 <strong>Learning Assistant RAG</strong> • Propulsé par FastAPI & Streamlit</p>
        <p><a href='http://127.0.0.1:8000/docs' target='_blank'>📘 API Documentation</a></p>
    </center>
    """,
    unsafe_allow_html=True
)