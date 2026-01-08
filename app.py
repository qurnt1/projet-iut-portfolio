import os
from dotenv import load_dotenv
import streamlit as st
from upstash_vector import Index

# --- CHANGEMENT ICI : Import depuis le nouveau fichier ---
from rag_backend import Agent, OpenAIProvider, Tool

# Charger les variables d'environnement
load_dotenv()

# ================================
# CONFIGURATION
# ================================

def initialize_upstash_index():
    url = os.getenv("UPSTASH_VECTOR_REST_URL")
    token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
    if not url or not token:
        st.error("Configuration Upstash manquante (.env).")
        return None
    return Index(url=url, token=token)

def initialize_agent():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("Clé API OpenAI manquante.")
        return None
    
    # Instruction système
    sys_prompt = """Tu es l'assistant portfolio de Quentin.
    Utilise 'search_portfolio' pour répondre aux questions.
    Si l'info est introuvable, dis-le. Sois pro."""
    
    return Agent(
        name="Portfolio Agent",
        instructions=sys_prompt,
        tools=[search_portfolio],
        provider=OpenAIProvider(api_key),
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
    )

# ================================
# OUTILS
# ================================

@Tool(
    name="search_portfolio",
    description="Cherche des infos sur Quentin Chabot (parcours, projets, skills)."
)
def search_portfolio(query: str) -> str:
    try:
        index = st.session_state.get("upstash_index")
        if not index: return "Erreur: DB non connectée."
        
        res = index.query(data=query, top_k=3, include_metadata=True)
        if not res: return "Aucune info trouvée."
        
        return "\n".join([f"- {r.metadata.get('title','Doc')}: {r.data}" for r in res])
    except Exception as e:
        return f"Erreur recherche: {e}"

# ================================
# INTERFACE
# ================================

def main():
    st.set_page_config(page_title="Portfolio IA", page_icon="🤖")
    st.title("🤖 Assistant Portfolio")

    # Init States
    if "messages" not in st.session_state: st.session_state.messages = []
    if "upstash_index" not in st.session_state: st.session_state.upstash_index = initialize_upstash_index()
    if "agent" not in st.session_state: st.session_state.agent = initialize_agent()

    # Affichage Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input Utilisateur
    if prompt := st.chat_input("Votre question sur Quentin ?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyse..."):
                if st.session_state.agent:
                    resp = st.session_state.agent.run(prompt)
                    txt = resp.get_text()
                    st.markdown(txt)
                    st.session_state.messages.append({"role": "assistant", "content": txt})

if __name__ == "__main__":
    main()