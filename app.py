import os
import time
import streamlit as st
from dotenv import load_dotenv
from upstash_vector import Index

# Import backend
# Assure-toi que ton fichier rag_backend.py contient bien les classes corrigées (Agent, Tool, OpenAIProvider)
from rag_backend import Agent, OpenAIProvider, Tool

load_dotenv()

# ================================
# CONFIGURATION
# ================================

USER_AVATAR = "👤" 
BOT_AVATAR = "assets/profile.png" 
MAX_QUESTIONS = 4 # Limite de questions utilisateur

st.set_page_config(
    page_title="Quentin Chabot - Assistant IA",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================================
# CSS & DESIGN NETTOYÉ
# ================================
# Le gros du style est maintenant dans .streamlit/config.toml
# Ici, on garde juste les hacks pour masquer le footer et ajuster les arrondis
st.markdown("""
<style>
    /* Masquer menu et footer */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Ajustement input pour correspondre au design */
    .stChatInput textarea {
        border-radius: 12px;
        border: 1px solid #D1D1D1;
    }
    
    /* Boutons suggestions */
    div.stButton > button {
        border-radius: 20px;
        border: 1px solid #E0E0E0;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        border-color: #D97757;
        color: #D97757 !important;
        background-color: #FFF8F5;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# LOGIQUE BACKEND
# ================================

@Tool(
    name="search_portfolio",
    description="Cherche dans le CV et le parcours. Utilise ce tool si la question porte sur Quentin."
)
def search_portfolio(query: str) -> str:
    try:
        index = st.session_state.get("upstash_index")
        if not index: return "Erreur: DB non connectée."
        
        # DEBUG: Voir ce qui se passe dans le terminal
        print(f"🔍 Recherche Upstash: '{query}'")
        
        res = index.query(data=query, top_k=5, include_metadata=True)
        
        if not res: 
            return "Aucune information trouvée dans la base de connaissances."
            
        # Construction claire du contexte pour le LLM
        context = "\n".join([f"- [Source: {r.metadata.get('title','Doc')}] {r.data}" for r in res])
        return f"CONTEXTE TROUVÉ :\n{context}"
        
    except Exception as e:
        print(f"❌ Erreur search: {e}")
        return f"Erreur technique: {e}"

def initialize_resources():
    if "upstash_index" not in st.session_state:
        url = os.getenv("UPSTASH_VECTOR_REST_URL")
        token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
        if url and token:
            st.session_state.upstash_index = Index(url=url, token=token)

    if "agent" not in st.session_state:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            # Prompt système renforcé pour forcer l'usage du contexte
            sys_prompt = """Tu es l'IA de Quentin Chabot.
            Ton rôle : Répondre aux recruteurs de manière professionnelle et factuelle.
            RÈGLE ABSOLUE : Si tu utilises l'outil search_portfolio, tu DOIS utiliser le contenu retourné ("CONTEXTE TROUVÉ") pour formuler ta réponse.
            Si le contexte contient l'info, ne dis jamais "je ne sais pas". Synthétise l'info."""
            
            st.session_state.agent = Agent(
                name="QuentinAI",
                instructions=sys_prompt,
                tools=[search_portfolio],
                provider=OpenAIProvider(api_key),
                model="gpt-4.1-nano" # Modèle valide obligatoire
            )

def stream_text(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)

# ================================
# INTERFACE
# ================================

def main():
    initialize_resources()

    # SIDEBAR
    with st.sidebar:
        st.header("Quentin Chabot")
        if st.button("🗑️ Reset conversation"):
            st.session_state.messages = []
            # On reset aussi l'agent pour vider sa mémoire interne
            if "agent" in st.session_state:
                del st.session_state.agent
            st.rerun()

    # HEADER
    st.markdown("<br><h1 style='text-align: center;'>Un moment café avec Quentin ?</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Je suis son jumeau numérique. Posez-moi vos questions.</p><br>", unsafe_allow_html=True)

    # INITIALISATION STATE
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Bonjour. Je suis prêt à détailler le parcours de Quentin."}]

    # 1. CALCUL DU COMPTEUR DE QUESTIONS UTILISATEUR
    # On compte combien de fois l'utilisateur a parlé
    user_questions_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    should_lock_input = user_questions_count >= MAX_QUESTIONS

    # AFFICHAGE HISTORIQUE
    for msg in st.session_state.messages:
        # Gestion avatar
        if msg["role"] == "assistant":
            avatar = BOT_AVATAR if os.path.exists(BOT_AVATAR) else "🤖"
        elif msg["role"] == "user":
            avatar = USER_AVATAR
        else:
            avatar = None # Pour les messages tools s'ils apparaissent
            
        # On n'affiche pas les messages techniques (tool calls) s'ils sont dans l'historique brut
        if msg["role"] in ["user", "assistant"]:
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # CTA DE FIN (Si limite atteinte)
    if should_lock_input:
        st.info("💡 Vous avez posé pas mal de questions... Et si on passait au réel ?")
        col1, col2 = st.columns(2)
        col1.link_button("📧 M'envoyer un mail", "mailto:quentin.chabot@etu.univ-poitiers.fr", use_container_width=True)
        col2.link_button("👔 LinkedIn", "https://fr.linkedin.com/in/chabotquentin", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # SUGGESTIONS (Seulement si non bloqué)
    prompt_input = None
    if not should_lock_input and user_questions_count < 2:
        col1, col2, col3 = st.columns(3)
        if col1.button("🎓 Parcours", use_container_width=True): prompt_input = "Quel est ton parcours académique ?"
        if col2.button("💼 Expériences", use_container_width=True): prompt_input = "Détaille tes expériences pro."
        if col3.button("🛠️ Stack Tech", use_container_width=True): prompt_input = "Quelles technos maîtrises-tu ?"

    # ZONE DE SAISIE
    # Le paramètre disabled bloque physiquement l'input
    placeholder_text = "La conversation est terminée." if should_lock_input else "Posez votre question..."
    user_input = st.chat_input(placeholder_text, disabled=should_lock_input)

    # GESTION ENVOI
    final_input = prompt_input if prompt_input else user_input

    if final_input and not should_lock_input:
        # 1. User Message
        st.session_state.messages.append({"role": "user", "content": final_input})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(final_input)

        # 2. Assistant Response
        avatar_path = BOT_AVATAR if os.path.exists(BOT_AVATAR) else "🤖"
        with st.chat_message("assistant", avatar=avatar_path):
            response_placeholder = st.empty()
            full_response = ""
            
            if hasattr(st.session_state, 'agent'):
                # IMPORTANT : On n'envoie QUE la nouvelle question.
                # L'agent a sa propre mémoire dans st.session_state.agent.messages
                with st.spinner("Analyse du parcours..."):
                    try:
                        # Appel direct sans historique manuel
                        raw_response = st.session_state.agent.run(final_input).get_text()
                    except Exception as e:
                        raw_response = f"Erreur backend: {e}"
                
                # Streaming
                for chunk in stream_text(raw_response):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
            else:
                st.error("Backend non initialisé (vérifiez API KEY).")
                full_response = "Erreur système."

            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        # Rerun pour mettre à jour l'interface (compteurs, boutons grisés, etc.)
        st.rerun()

if __name__ == "__main__":
    main()