import os
import time
from typing import Generator, List, Dict, Any, Optional
import base64
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from agent import portfolio_agent
from agents import Runner

# Chargement des variables d'environnement
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Quentin Chabot - Assistant IA",
    layout="wide",
)

# Avatars pour l'affichage des messages
USER_AVATAR: str = "👤"
BOT_AVATAR: str = "assets/profile.png"

# Seuil de questions avant affichage de la zone de contact
THRESHOLD_QUESTIONS: int = 4

# URLs des icônes pour les boutons de contact
ICON_MAIL: str = "https://cdn-icons-png.flaticon.com/512/732/732200.png"
ICON_LINKEDIN: str = "https://cdn-icons-png.flaticon.com/512/3536/3536505.png"
ICON_GITHUB: str = "https://cdn-icons-png.flaticon.com/512/733/733553.png"

# ============================================================================
# FONCTIONS UTILITAIRES & BACKEND RAG
# ============================================================================
def run_agent_query(query: str) -> str:
    """
    Exécute une requête via l'agent RAG défini dans agent.py.
    """
    result = Runner.run_sync(
        starting_agent=portfolio_agent,
        input=query,
    )
    return result.final_output

def stream_text(text: str) -> Generator[str, None, None]:
    """
    Génère un flux de mots pour simuler un effet de streaming.

    Cette fonction découpe le texte en mots et les renvoie un par un
    avec un délai, créant un effet visuel d'écriture progressive.

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

def get_cv_button_html() -> str:
    """Génère le code HTML pour le bouton de téléchargement du CV."""
    cv_path = Path("assets/cv_quentin_chabot.pdf")
    
    # Vérifier que le fichier existe
    if not cv_path.exists():
        return "<p style='color: red;'>⚠️ Fichier CV introuvable</p>"
    
    # Lire et encoder le PDF en base64
    with open(cv_path, "rb") as f:
        pdf_bytes = f.read()
    
    b64_pdf = base64.b64encode(pdf_bytes).decode()
    
    # Créer un data URI
    href = f"data:application/pdf;base64,{b64_pdf}"
    
    btn_style = (
        "display: inline-flex; align-items: center; justify-content: center; "
        "background-color: #eee8d1ff; color: #141413; border: 1px solid #E8E6DC; "
        "border-radius: 8px; padding: 0.6rem 1.2rem; text-decoration: none; "
        "font-weight: 600; margin-top: 10px;"
    )
    
    icon_url = "https://cdn-icons-png.flaticon.com/512/337/337946.png"
    
    return f"""
    <br>
    <a href="{href}" download="CV_Quentin_Chabot.pdf" style="{btn_style}">
        <img src="{icon_url}" style="width: 20px; height: 20px; margin-right: 10px;">
        Télécharger mon CV
    </a>
    """

# ============================================================================
# APPLICATION PRINCIPALE
# ============================================================================

def main() -> None:
    """
    Point d'entrée principal de l'application Streamlit.

    Orchestre le flux complet de l'interface :
        1. Initialisation de l'historique des messages
        2. Affichage des messages existants
        3. Gestion des suggestions et de la zone de contact
        4. Traitement des nouvelles questions
        5. Appel à l'agent et affichage de la réponse

    Returns:
        None
    """

    st.title("Échangez avec Quentin !")
    st.write("Posez moi des questions sur mon parcours académique et mes expériences.")

    # --- Initialisation de l'historique ---
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Bonjour. Je maîtrise l'ensemble du parcours de Quentin. Souhaitez-vous explorer ses compétences techniques, ses expériences ou ses projets ?"
            }
        ]

    # --- Affichage de l'historique des messages ---
    for msg in st.session_state.messages:
        avatar = (BOT_AVATAR if msg["role"] == "assistant" and os.path.exists(BOT_AVATAR) else "🤖") if msg["role"] == "assistant" else USER_AVATAR

        with st.chat_message(msg["role"], avatar=avatar):
            if msg["role"] == "assistant":
                st.markdown(msg["content"], unsafe_allow_html=True)  # autorise le bouton CV
            else:
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
        st.info("L'IA c'est bien, l'humain c'est mieux, Retrouvez-moi sur mes canaux professionnels.")

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
    if not show_contact:
        user_input: Optional[str] = st.chat_input("Posez vos questions ici...", key="chat_input")
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
            
            # Variables temporaires
            text_response: str = ""
            button_html: str = ""
            full_res: str = ""

            with st.spinner("L'agent réfléchit..."):
                try:
                    # On récupère SEULEMENT le texte de l'agent d'abord
                    text_response = run_agent_query(prompt_to_process)
                    
                    # On prépare le bouton séparément, sans le coller tout de suite
                    keywords_cv = ["cv", "curriculum", "resume", "télécharger"]
                    if any(k in prompt_to_process.lower() for k in keywords_cv):
                        button_html = get_cv_button_html()

                except Exception as e:
                    text_response = f"Une erreur est survenue : {e}"

            # 3. Affichage progressif (simulation de streaming UNIQUEMENT sur le texte)
            temp_text: str = ""
            for chunk in stream_text(text_response):
                temp_text += chunk
                # On affiche le texte en cours + curseur
                placeholder.markdown(temp_text + "▌")
            
            # 4. Assemblage Final : Texte + Bouton (s'il existe)
            full_res = text_response + button_html
            
            # On met à jour le placeholder une dernière fois avec le rendu HTML complet
            placeholder.markdown(full_res, unsafe_allow_html=True)

            # 5. Sauvegarde dans l'historique
            st.session_state.messages.append({"role": "assistant", "content": full_res})

        # Délai pour fluidité avant le refresh
        time.sleep(0.2)
        st.rerun()

if __name__ == "__main__":
    main()
