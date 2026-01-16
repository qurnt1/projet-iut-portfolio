"""
Interface utilisateur Streamlit pour l'assistant virtuel de Quentin Chabot.

Ce module implémente l'application de chat interactive permettant aux utilisateurs
d'interroger l'agent IA sur le profil professionnel de Quentin.

Fonctionnalités principales :
    - Interface de chat avec historique des messages
    - Suggestions de questions prédéfinies au démarrage
    - Sidebar avec statut des connexions (API OpenAI, Upstash)
    - Affichage progressif des réponses (effet de streaming)
    - Zone de contact après un certain nombre d'échanges

Usage:
    streamlit run streamlit_app.py

Dependencies:
    - streamlit
    - rag_backend (module local)
"""

import os
import time
from typing import Generator, List, Dict, Any, Optional

import streamlit as st
from dotenv import load_dotenv

from rag_backend import run_agent_query, check_upstash_connection

# Chargement des variables d'environnement
load_dotenv()


# ============================================================================
# CONFIGURATION
# ============================================================================

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Quentin Chabot - Assistant IA",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialisation du statut Upstash au premier chargement
if "upstash_status" not in st.session_state:
    st.session_state["upstash_status"] = check_upstash_connection()

# Avatars pour l'affichage des messages
USER_AVATAR: str = "👤"
BOT_AVATAR: str = "assets/profile.png"

# Seuil de questions avant affichage de la zone de contact
THRESHOLD_QUESTIONS: int = 4

# Gestion de l'historique des messages
MEMORY_WINDOW_UI: int = 60       # Nombre max de messages affichés dans l'UI
MEMORY_WINDOW_MODEL: int = 14    # Nombre de messages envoyés au LLM (hors system)

# URLs des icônes pour les boutons de contact
ICON_MAIL: str = "https://cdn-icons-png.flaticon.com/512/732/732200.png"
ICON_LINKEDIN: str = "https://cdn-icons-png.flaticon.com/512/3536/3536505.png"
ICON_GITHUB: str = "https://cdn-icons-png.flaticon.com/512/733/733553.png"


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def stream_text(text: str) -> Generator[str, None, None]:
    """
    Génère un flux de mots pour simuler un effet de streaming.

    Cette fonction découpe le texte en mots et les renvoie un par un
    avec un délai, créant un effet visuel de frappe progressive.

    Args:
        text: Le texte complet à streamer.

    Yields:
        Chaque mot suivi d'un espace, avec un délai de 20ms entre chaque.

    Example:
        >>> for word in stream_text("Bonjour monde"):
        ...     print(word, end="")
        Bonjour monde
    """
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)


def render_custom_button(url: str, text: str, icon_url: str) -> None:
    """
    Affiche un bouton personnalisé avec icône via HTML.

    Args:
        url: URL de destination du lien.
        text: Texte affiché sur le bouton.
        icon_url: URL de l'icône à afficher.

    Returns:
        None

    Note:
        Utilise unsafe_allow_html pour le rendu HTML personnalisé.
    """
    st.markdown(
        f"""
        <a href="{url}" target="_blank" class="custom-img-btn">
            <img src="{icon_url}">
            {text}
        </a>
        """,
        unsafe_allow_html=True,
    )


def trim_ui_history(limit: int = MEMORY_WINDOW_UI) -> None:
    """
    Limite la taille de l'historique des messages affiché.

    Conserve le premier message (message de bienvenue) et les N-1 derniers
    messages pour éviter une surcharge de l'interface.

    Args:
        limit: Nombre maximum de messages à conserver. Par défaut MEMORY_WINDOW_UI.

    Returns:
        None

    Note:
        Modifie directement st.session_state.messages.
    """
    msgs: List[Dict[str, Any]] = st.session_state.get("messages", [])
    if len(msgs) <= limit:
        return

    # Conservation du premier message (bienvenue) + les derniers messages
    head: List[Dict[str, Any]] = msgs[:1]
    tail: List[Dict[str, Any]] = msgs[-(limit - 1):]
    st.session_state.messages = head + tail


def render_sidebar() -> None:
    """
    Affiche la barre latérale avec les informations et contrôles.

    Contenu affiché :
        - Titre et sous-titre du profil
        - Bouton de nouvelle conversation
        - Statut des connexions (API OpenAI, Upstash Vector)

    Returns:
        None
    """
    with st.sidebar:
        st.title("Quentin Chabot")
        st.caption("Développeur / Data Scientist")

        st.divider()

        # Bouton de réinitialisation de la conversation
        if st.button("🗑️ Nouvelle conversation", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Bonjour. Je suis l'assistant virtuel de Quentin. "
                               "Quel aspect de son profil souhaitez-vous approfondir aujourd'hui ?",
                }
            ]
            st.rerun()

        st.divider()
        st.subheader("État du système")

        # Indicateur de statut API OpenAI
        if os.getenv("openAI_API_KEY"):
            st.success("Agent IA : Prêt")
        else:
            st.error("Clé API manquante")

        # Indicateur de statut Upstash Vector
        if st.session_state.get("upstash_status"):
            st.success("Mémoire (Vector DB) : Connectée")
        else:
            st.error("Mémoire (Vector DB) : Déconnectée")


# ============================================================================
# APPLICATION PRINCIPALE
# ============================================================================

def main() -> None:
    """
    Point d'entrée principal de l'application Streamlit.

    Orchestre le flux complet de l'interface :
        1. Rendu de la sidebar
        2. Initialisation de l'historique des messages
        3. Affichage des messages existants
        4. Gestion des suggestions et de la zone de contact
        5. Traitement des nouvelles questions
        6. Appel à l'agent et affichage de la réponse

    Returns:
        None
    """
    render_sidebar()

    st.title("Échangez avec Quentin !")
    st.write("Posez vos questions sur mon parcours académique et mes expériences.")

    # --- Initialisation de l'historique ---
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Bonjour. Je suis l'assistant virtuel de Quentin. "
                           "Quel aspect de son profil souhaitez-vous approfondir aujourd'hui ?",
            }
        ]

    # Nettoyage de l'historique si nécessaire
    trim_ui_history()

    # --- Affichage de l'historique des messages ---
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            avatar = BOT_AVATAR if os.path.exists(BOT_AVATAR) else "🤖"
        else:
            avatar = USER_AVATAR
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Variable pour stocker la question à traiter
    prompt_to_process: Optional[str] = None

    # Calcul du nombre de messages utilisateur pour la logique d'affichage
    user_msgs: List[Dict[str, Any]] = [m for m in st.session_state.messages if m["role"] == "user"]
    show_contact: bool = len(user_msgs) >= THRESHOLD_QUESTIONS

    # --- Suggestions de questions au démarrage ---
    if len(st.session_state.messages) == 1 and not show_contact:
        st.caption("Suggestions de questions :")
        col1, col2, col3 = st.columns(3)

        if col1.button("Parcours académique", use_container_width=True):
            prompt_to_process = "Quel est ton parcours académique ?"
        if col2.button("Éxpériences professionnelles", use_container_width=True):
            prompt_to_process = "Détaille tes expériences professionnelles techniques (Alternance et Stage)."
        if col3.button("Compétences techniques", use_container_width=True):
            prompt_to_process = "Quelles sont tes compétences techniques ?"

    # --- Zone de contact (après plusieurs échanges) ---
    if show_contact:
        st.divider()
        st.subheader("Passons au réel")
        st.info("L'IA c'est bien, l'humain c'est mieux. Retrouvez-moi sur mes canaux professionnels.")

        c1, c2, c3 = st.columns(3)

        # Styles inline pour les boutons de contact
        btn_style: str = (
            "display: flex; align-items: center; justify-content: center; "
            "background-color: #eee8d1ff; color: #141413; border: 1px solid #E8E6DC; "
            "border-radius: 8px; padding: 0.6rem; text-decoration: none; "
            "font-weight: 600; width: 100%;"
        )
        img_style: str = "width: 20px; height: 20px; margin-right: 10px;"

        with c1:
            st.markdown(
                f"""
                <a href="mailto:quentin.chabot@etu.univ-poitiers.fr" target="_blank" style="{btn_style}">
                    <img src="{ICON_MAIL}" style="{img_style}"> Email
                </a>
                """,
                unsafe_allow_html=True
            )

        with c2:
            st.markdown(
                f"""
                <a href="https://fr.linkedin.com/in/chabotquentin" target="_blank" style="{btn_style}">
                    <img src="{ICON_LINKEDIN}" style="{img_style}"> LinkedIn
                </a>
                """,
                unsafe_allow_html=True
            )

        with c3:
            st.markdown(
                f"""
                <a href="https://github.com/qurnt1" target="_blank" style="{btn_style}">
                    <img src="{ICON_GITHUB}" style="{img_style}"> GitHub
                </a>
                """,
                unsafe_allow_html=True
            )

        st.write("")

    # --- Zone de saisie utilisateur ---
    user_input: Optional[str] = st.chat_input("Posez votre question ici...", key="chat_input")
    if user_input:
        prompt_to_process = user_input

    # --- Traitement de la question ---
    if prompt_to_process:
        # 1. Enregistrement et affichage du message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt_to_process})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt_to_process)

        # 2. Appel à l'agent et affichage de la réponse
        avatar_assistant = BOT_AVATAR if os.path.exists(BOT_AVATAR) else "🤖"
        with st.chat_message("assistant", avatar=avatar_assistant):
            placeholder = st.empty()
            full_res: str = ""

            with st.spinner("L'agent réfléchit..."):
                try:
                    # Appel au backend RAG pour obtenir la réponse
                    full_res = run_agent_query(prompt_to_process)
                except Exception as e:
                    full_res = f"Une erreur est survenue : {e}"

            # 3. Affichage progressif (simulation de streaming pour l'UX)
            temp_text: str = ""
            for chunk in stream_text(full_res):
                temp_text += chunk
                placeholder.markdown(temp_text + "▌")
            placeholder.markdown(full_res)

            # 4. Sauvegarde dans l'historique
            st.session_state.messages.append({"role": "assistant", "content": full_res})

        # Délai pour fluidité avant le refresh
        time.sleep(0.2)
        st.rerun()


if __name__ == "__main__":
    main()
