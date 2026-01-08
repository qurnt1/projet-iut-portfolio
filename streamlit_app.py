import os
import time
import streamlit as st
from dotenv import load_dotenv
from upstash_vector import Index

# Import backend adapté
from rag_backend import Agent, GroqProvider, Tool

load_dotenv()

# ================================
# CONFIGURATION
# ================================

USER_AVATAR = "👤" 
BOT_AVATAR = "assets/profile.png" 
MAX_QUESTIONS = 4 

st.set_page_config(
    page_title="Quentin Chabot - Assistant IA",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stChatInput textarea { border-radius: 12px; border: 1px solid #D1D1D1; }
    div.stButton > button { border-radius: 20px; border: 1px solid #E0E0E0; transition: all 0.2s; }
    div.stButton > button:hover { border-color: #D97757; color: #D97757 !important; background-color: #FFF8F5; }
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
        
        # Récupération du TOP_K depuis le .env (défaut à 5 si vide)
        top_k_env = os.getenv("TOP_K", "5")
        top_k = int(top_k_env) if top_k_env.isdigit() else 5
        
        print(f"🔍 Recherche Upstash (Top {top_k}): '{query}'")
        res = index.query(data=query, top_k=top_k, include_metadata=True)
        
        if not res: 
            return "Aucune information trouvée dans la base de connaissances."
            
        context = "\n".join([f"- [Source: {r.metadata.get('title','Doc')}] {r.data}" for r in res])
        return f"CONTEXTE TROUVÉ :\n{context}"
        
    except Exception as e:
        print(f"❌ Erreur search: {e}")
        return f"Erreur technique: {e}"

def initialize_resources():
    # 1. Init Upstash
    if "upstash_index" not in st.session_state:
        url = os.getenv("UPSTASH_VECTOR_REST_URL")
        token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
        if url and token:
            st.session_state.upstash_index = Index(url=url, token=token)

    # 2. Init Groq Agent avec les variables du .env
    if "agent" not in st.session_state:
        api_key = os.getenv("GROQ_API_KEY")
        model_name = os.getenv("GROQ_MODEL", "llama3-70b-8192") # Fallback de sécurité
        
        if api_key:
            sys_prompt = """Tu es l'IA de Quentin Chabot.
            Ton rôle : Répondre aux recruteurs de manière professionnelle et factuelle.
            RÈGLE ABSOLUE : Si tu utilises l'outil search_portfolio, tu DOIS utiliser le contenu retourné ("CONTEXTE TROUVÉ") pour formuler ta réponse.
            Si le contexte contient l'info, ne dis jamais "je ne sais pas". Synthétise l'info.
            Sois concis."""
            
            st.session_state.agent = Agent(
                name="QuentinAI",
                instructions=sys_prompt,
                tools=[search_portfolio],
                provider=GroqProvider(api_key),
                model=model_name
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

    with st.sidebar:
        st.header("Quentin Chabot")
        if st.button("🗑️ Reset conversation"):
            st.session_state.messages = []
            if "agent" in st.session_state:
                del st.session_state.agent
            st.rerun()

    st.markdown("<br><h1 style='text-align: center;'>Un moment café avec Quentin ?</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Je suis son jumeau numérique. Posez-moi vos questions.</p><br>", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Bonjour. Je suis prêt à détailler le parcours de Quentin."}]

    user_questions_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    should_lock_input = user_questions_count >= MAX_QUESTIONS

    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            avatar = BOT_AVATAR if os.path.exists(BOT_AVATAR) else "🤖"
        elif msg["role"] == "user":
            avatar = USER_AVATAR
        else:
            avatar = None 
            
        if msg["role"] in ["user", "assistant"]:
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    if should_lock_input:
        st.info("💡 Vous avez posé pas mal de questions... Et si on passait au réel ?")
        col1, col2 = st.columns(2)
        col1.link_button("📧 M'envoyer un mail", "mailto:quentin.chabot@etu.univ-poitiers.fr", use_container_width=True)
        col2.link_button("👔 LinkedIn", "https://fr.linkedin.com/in/chabotquentin", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)

    prompt_input = None
    if not should_lock_input and user_questions_count < 2:
        col1, col2, col3 = st.columns(3)
        if col1.button("🎓 Parcours", use_container_width=True): prompt_input = "Quel est ton parcours académique ?"
        if col2.button("💼 Expériences", use_container_width=True): prompt_input = "Détaille tes expériences pro."
        if col3.button("🛠️ Stack Tech", use_container_width=True): prompt_input = "Quelles technos maîtrises-tu ?"

    placeholder_text = "La conversation est terminée." if should_lock_input else "Posez votre question..."
    user_input = st.chat_input(placeholder_text, disabled=should_lock_input)
    final_input = prompt_input if prompt_input else user_input

    if final_input and not should_lock_input:
        st.session_state.messages.append({"role": "user", "content": final_input})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(final_input)

        avatar_path = BOT_AVATAR if os.path.exists(BOT_AVATAR) else "🤖"
        with st.chat_message("assistant", avatar=avatar_path):
            response_placeholder = st.empty()
            full_response = ""
            
            if hasattr(st.session_state, 'agent'):
                with st.spinner("Analyse du parcours..."):
                    try:
                        raw_response = st.session_state.agent.run(final_input).get_text()
                    except Exception as e:
                        raw_response = f"Erreur backend: {e}"
                
                for chunk in stream_text(raw_response):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
            else:
                st.error("Backend non initialisé (vérifiez .env).")
                full_response = "Erreur système."

            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        st.rerun()

if __name__ == "__main__":
    main()