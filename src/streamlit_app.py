# app.py
import os
import time
import streamlit as st
from dotenv import load_dotenv
from upstash_vector import Index
import requests

load_dotenv()

# ================================
# 1. CONFIGURATION
# ================================

st.set_page_config(
    page_title="Quentin Chabot - Assistant IA",
    layout="wide",
    initial_sidebar_state="expanded",
)

USER_AVATAR = "👤"
BOT_AVATAR = "assets/profile.png"

THRESHOLD_QUESTIONS = 4

# UI/history
MEMORY_WINDOW_UI = 60          # historique affiché (UI)
MEMORY_WINDOW_MODEL = 14       # nb de messages envoyés au LLM (hors system)

ICON_MAIL = "https://cdn-icons-png.flaticon.com/512/732/732200.png"
ICON_LINKEDIN = "https://cdn-icons-png.flaticon.com/512/3536/3536505.png"
ICON_GITHUB = "https://cdn-icons-png.flaticon.com/512/733/733553.png"

DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

SYS_PROMPT = (
    "Tu es l'assistant professionnel de Quentin Chabot.\n"
    "Objectif : répondre de manière factuelle, synthétique et convaincante pour un recruteur.\n\n"
    "Règles:\n"
    "- Si un contexte interne est fourni, utilise-le pour être précis.\n"
    "- Ne mentionne jamais d'outils, de base vectorielle, de sources techniques, ni de noms de documents.\n"
    "- Si l'information n'est pas dans le contexte, dis-le clairement et propose une formulation prudente.\n"
)

# ================================
# 2. STYLES CSS
# ================================

st.markdown(
    """
<style>
    div[data-testid="stChatInput"] > div {
        border-color: #D97757 !important;
        border-width: 2px !important;
        border-radius: 25px !important;
    }
    div[data-testid="stChatInput"] > div:focus-within {
        box-shadow: 0 0 0 1px #D97757 !important;
    }

    a.custom-img-btn {
        display: flex !important;
        align-items: center;
        justify-content: center;
        background-color: #eee8d1ff;
        color: #141413;
        border: 1px solid #E8E6DC;
        border-radius: 8px;
        padding: 0.6rem 0.75rem;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.2s;
        width: 100%;
        box-sizing: border-box;
    }
    a.custom-img-btn:hover {
        border-color: #D97757;
        color: #D97757 !important;
        background-color: #FFF8F5;
    }
    a.custom-img-btn img {
        width: 20px;
        height: 20px;
        margin-right: 10px;
        object-fit: contain;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ================================
# 3. DATA / SERVICES
# ================================

def initialize_upstash():
    if "upstash_index" in st.session_state:
        return

    url = os.getenv("UPSTASH_VECTOR_REST_URL")
    token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
    if not url or not token:
        st.session_state.upstash_index = None
        st.session_state.upstash_status = False
        return

    try:
        st.session_state.upstash_index = Index(url=url, token=token)
        # test best-effort
        try:
            st.session_state.upstash_index.info()
        except Exception:
            pass
        st.session_state.upstash_status = True
    except Exception:
        st.session_state.upstash_index = None
        st.session_state.upstash_status = False


def groq_is_configured() -> bool:
    return bool(os.getenv("GROQ_API_KEY"))


def build_internal_context(query: str, top_k: int = 5) -> str:
    """
    Retourne un contexte "interne" à injecter au LLM (sans sources).
    """
    index = st.session_state.get("upstash_index")
    if not index:
        return ""

    try:
        res = index.query(
            data=query,
            top_k=top_k,
            include_metadata=True,
            include_data=True,
        )
        if not res:
            return ""

        # IMPORTANT: on ne met pas les "sources" dans le contexte (réduit le risque de fuite)
        chunks = []
        for r in res:
            txt = (r.data or "").strip()
            if txt:
                chunks.append(f"- {txt}")

        return "\n".join(chunks).strip()
    except Exception:
        return ""


def groq_chat(messages, model: str, temperature: float = 0.3, timeout_s: int = 60) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY manquante.")

    url = f"{GROQ_BASE_URL}/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": float(temperature),
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    r = requests.post(url, json=payload, headers=headers, timeout=timeout_s)
    if r.status_code != 200:
        # On remonte le message brut (utile au debug)
        raise RuntimeError(f"HTTP {r.status_code}: {r.text}")

    data = r.json()
    return data["choices"][0]["message"]["content"]


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

        if groq_is_configured():
            st.success("IA (LLM) : Configurée")
        else:
            st.error("IA (LLM) : Non configurée")

        if st.session_state.get("upstash_status"):
            st.success("Mémoire (Vector DB) : Connectée")
        else:
            st.error("Mémoire (Vector DB) : Déconnectée")


# ================================
# 4. APP
# ================================

def main():
    initialize_upstash()
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
            prompt_to_process = "Détaille tes expériences pro."
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
        with c1:
            render_custom_button("mailto:quentin.chabot@etu.univ-poitiers.fr", "M'envoyer un Email", ICON_MAIL)
        with c2:
            render_custom_button("https://fr.linkedin.com/in/chabotquentin", "Mon Profil LinkedIn", ICON_LINKEDIN)
        with c3:
            render_custom_button("https://github.com/chabotquentin", "Mon Profil GitHub", ICON_GITHUB)
        st.write("")

    # Input
    user_input = st.chat_input("Posez votre question ici...", key="chat_input")
    if user_input:
        prompt_to_process = user_input

    # Traitement
    if prompt_to_process:
        st.session_state.messages.append({"role": "user", "content": prompt_to_process})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt_to_process)

        avatar_assistant = BOT_AVATAR if os.path.exists(BOT_AVATAR) else "🤖"
        with st.chat_message("assistant", avatar=avatar_assistant):
            placeholder = st.empty()

            if not groq_is_configured():
                full_res = "⚠️ GROQ_API_KEY manquante (service IA non configuré)."
                placeholder.error(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                time.sleep(0.2)
                st.rerun()

            # Build context (Upstash facultatif)
            context = ""
            if st.session_state.get("upstash_status"):
                with st.spinner("📚 Consultation de la base..."):
                    context = build_internal_context(
                        query=prompt_to_process,
                        top_k=int(os.getenv("UPSTASH_TOP_K", "5")),
                    )

            # Build model messages
            model = (os.getenv("GROQ_MODEL") or DEFAULT_GROQ_MODEL).strip()
            print(f"DEBUG: Appel LLM avec le modèle {model}...")

            history = st.session_state.messages[-MEMORY_WINDOW_MODEL:]
            llm_messages = [{"role": "system", "content": SYS_PROMPT}]

            if context:
                llm_messages.append(
                    {
                        "role": "system",
                        "content": "Contexte interne (ne jamais mentionner son origine, ni citer de documents):\n"
                                   f"{context}",
                    }
                )

            # Injecter l'historique (user/assistant) tel quel
            for m in history:
                if m["role"] in ("user", "assistant"):
                    llm_messages.append({"role": m["role"], "content": m["content"]})

            # Retry (API)
            max_retries = 3
            success = False
            full_res = ""

            with st.spinner("Analyse en cours..."):
                for attempt in range(max_retries):
                    try:
                        full_res = groq_chat(llm_messages, model=model, temperature=0.3)
                        success = True
                        break
                    except Exception as e:
                        print(f"⚠️ Tentative {attempt+1} échouée : {e}")
                        time.sleep(1)

            if not success:
                full_res = "Une erreur technique persistante empêche la réponse."

            # Affichage progressif
            if success:
                temp = ""
                for chunk in stream_text(full_res):
                    temp += chunk
                    placeholder.markdown(temp + "▌")
                placeholder.markdown(full_res)
            else:
                placeholder.error(full_res)

            st.session_state.messages.append({"role": "assistant", "content": full_res})

        time.sleep(0.2)
        st.rerun()


if __name__ == "__main__":
    main()
