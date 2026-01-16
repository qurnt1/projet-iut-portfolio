# app.py
import os
import time
import streamlit as st
from dotenv import load_dotenv
# --- MODIFICATION : Import de check_upstash_connection ---
from rag_backend import run_agent_query, check_upstash_connection

load_dotenv()

# ================================
# 1. CONFIGURATION
# ================================

st.set_page_config(
    page_title="Quentin Chabot - Assistant IA",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- AJOUT : Initialisation du statut Upstash au chargement ---
if "upstash_status" not in st.session_state:
    st.session_state["upstash_status"] = check_upstash_connection()

USER_AVATAR = "👤"
BOT_AVATAR = "assets/profile.png"

THRESHOLD_QUESTIONS = 4

# UI/history
MEMORY_WINDOW_UI = 60          # historique affiché (UI)
MEMORY_WINDOW_MODEL = 14       # nb de messages envoyés au LLM (hors system)

ICON_MAIL = "https://cdn-icons-png.flaticon.com/512/732/732200.png"
ICON_LINKEDIN = "https://cdn-icons-png.flaticon.com/512/3536/3536505.png"
ICON_GITHUB = "https://cdn-icons-png.flaticon.com/512/733/733553.png"

# ================================
# 3. DATA / SERVICES
# ================================

def stream_text(text: str):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)


def render_custom_button(url: str, text: str, icon_url: str):
    st.markdown(
        f"""
        <a href="{url}" target="_blank" class="custom-img-btn">
            <img src="{icon_url}">
            {text}
        </a>
        """,
        unsafe_allow_html=True,
    )


def trim_ui_history(limit: int = MEMORY_WINDOW_UI):
    msgs = st.session_state.get("messages", [])
    if len(msgs) <= limit:
        return
    head = msgs[:1]
    tail = msgs[-(limit - 1) :]
    st.session_state.messages = head + tail


def render_sidebar():
    with st.sidebar:
        st.title("Quentin Chabot")
        st.caption("Développeur / Data Scientist")

        st.divider()

        if st.button("🗑️ Nouvelle conversation", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Bonjour. Je suis l'assistant virtuel de Quentin. Quel aspect de son profil souhaitez-vous approfondir aujourd'hui ?",
                }
            ]
            st.rerun()

        st.divider()
        st.subheader("État du système")
        if os.getenv("GROQ_API_KEY"):
            st.success("Agent IA : Prêt")
        else:
            st.error("Clé API manquante")

        if st.session_state.get("upstash_status"):
            st.success("Mémoire (Vector DB) : Connectée")
        else:
            st.error("Mémoire (Vector DB) : Déconnectée")


# ================================
# 4. APP
# ================================

def main():
    render_sidebar()

    st.title("Échangez avec Quentin !")
    st.write("Posez vos questions sur mon parcours académique et mes expériences.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Bonjour. Je suis l'assistant virtuel de Quentin. Quel aspect de son profil souhaitez-vous approfondir aujourd'hui ?",
            }
        ]

    trim_ui_history()

    # Affichage historique
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            avatar = BOT_AVATAR if os.path.exists(BOT_AVATAR) else "🤖"
        else:
            avatar = USER_AVATAR
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    prompt_to_process = None

    user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
    show_contact = len(user_msgs) >= THRESHOLD_QUESTIONS

    # Suggestions au démarrage
    if len(st.session_state.messages) == 1 and not show_contact:
        st.caption("Suggestions de questions :")
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("🎓 Études", use_container_width=True):
            prompt_to_process = "Quel est ton parcours académique ?"
        if col2.button("💼 Expériences", use_container_width=True):
            prompt_to_process = "Détaille tes expériences professionnelles techniques (Alternance, Stages et jobs étudiants)."
        if col3.button("🛠️ Tech", use_container_width=True):
            prompt_to_process = "Quelles sont tes compétences techniques ?"
        if col4.button("🧠 Soft Skills", use_container_width=True):
            prompt_to_process = "Quelles sont tes qualités humaines ?"

    # Zone contact
    if show_contact:
        st.divider()
        st.subheader("Passons au réel")
        st.info("L'IA c'est bien, l'humain c'est mieux. Retrouvez-moi sur mes canaux professionnels.")
        
        c1, c2, c3 = st.columns(3)
        
        btn_style = "display: flex; align-items: center; justify-content: center; background-color: #eee8d1ff; color: #141413; border: 1px solid #E8E6DC; border-radius: 8px; padding: 0.6rem; text-decoration: none; font-weight: 600; width: 100%;"
        img_style = "width: 20px; height: 20px; margin-right: 10px;"

        with c1:
            st.markdown(f"""
            <a href="mailto:quentin.chabot@etu.univ-poitiers.fr" target="_blank" style="{btn_style}">
                <img src="{ICON_MAIL}" style="{img_style}"> Email
            </a>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <a href="https://fr.linkedin.com/in/chabotquentin" target="_blank" style="{btn_style}">
                <img src="{ICON_LINKEDIN}" style="{img_style}"> LinkedIn
            </a>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <a href="https://github.com/qurnt1" target="_blank" style="{btn_style}">
                <img src="{ICON_GITHUB}" style="{img_style}"> GitHub
            </a>
            """, unsafe_allow_html=True)
            
        st.write("")

    # Input
    user_input = st.chat_input("Posez votre question ici...", key="chat_input")
    if user_input:
        prompt_to_process = user_input

    # Traitement
    if prompt_to_process:
        # 1. Afficher le message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt_to_process})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt_to_process)

        # 2. Appel à l'Agent
        avatar_assistant = BOT_AVATAR if os.path.exists(BOT_AVATAR) else "🤖"
        with st.chat_message("assistant", avatar=avatar_assistant):
            placeholder = st.empty()
            full_res = ""

            with st.spinner("L'agent réfléchit..."):
                try:
                    # C'est ici que la magie opère : appel unique au backend
                    full_res = run_agent_query(prompt_to_process)
                except Exception as e:
                    full_res = f"Une erreur est survenue : {e}"
            
            # 3. Affichage (Simulation de streaming pour l'UX)
            # L'agent synchrone répond tout d'un coup, on stream le résultat pour l'effet visuel
            temp_text = ""
            for chunk in stream_text(full_res):
                temp_text += chunk
                placeholder.markdown(temp_text + "▌")
            placeholder.markdown(full_res)

            # 4. Sauvegarde historique
            st.session_state.messages.append({"role": "assistant", "content": full_res})

        # Petit délai pour fluidité
        time.sleep(0.2)
        st.rerun()
        

if __name__ == "__main__":
    main()
