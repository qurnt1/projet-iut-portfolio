import os
import time
import streamlit as st
from dotenv import load_dotenv
from upstash_vector import Index

# Import backend
from rag_backend import Agent, GroqProvider, Tool
import base64

load_dotenv()

# ================================
# 1. CONFIGURATION & STYLE AVANCÉ
# ================================

USER_AVATAR = "👤"
BOT_AVATAR = "assets/profile.png"
THRESHOLD_QUESTIONS = 4 

# Nouveautés : URLs directes pour les icônes (Plus fiable que les emojis)
ICON_BRAIN = "https://cdn-icons-png.flaticon.com/512/2942/2942946.png"
ICON_GRADUATION = "https://cdn-icons-png.flaticon.com/512/3135/3135810.png"
ICON_WORK = "https://cdn-icons-png.flaticon.com/512/2910/2910791.png"
ICON_TECH = "https://cdn-icons-png.flaticon.com/512/1055/1055666.png"
ICON_CHECK = "https://cdn-icons-png.flaticon.com/512/14600/14600323.png"
ICON_ERROR = "https://cdn-icons-png.flaticon.com/512/10336/10336214.png"
ICON_MAIL = "https://cdn-icons-png.flaticon.com/512/732/732200.png"
ICON_LINKEDIN = "https://cdn-icons-png.flaticon.com/512/3536/3536505.png"

st.set_page_config(
    page_title="Quentin Chabot - Assistant IA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injection CSS : Polices Google, Taille Avatars, Style Claude
st.markdown("""<style>
    /* --- IMPORT POLICES --- */
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Lato:wght@300;400;700&display=swap');

    /* --- GLOBAL (CLAUDE-LIKE PALETTE) --- */
    :root {
        --primary-color: #D97757;              /* Orange (accent principal) */
        --background-color: #FAF9F5;           /* Light (fond principal) */
        --secondary-background-color: #FFFFFF; /* Surfaces blanches (cards/panneaux) */
        --text-color: #141413;                /* Dark (texte principal) */
        --text-muted-color: #B0AEA5;          /* Mid Gray (texte secondaire/placeholder) */
        --border-color: #E8E6DC;              /* Light Gray (bordures/séparateurs) */
        --hover-tint: #FFF8F5;                /* Teinte hover chaude (déjà utilisée) */
    }

    h1,
    h2,
    h3,
    h4,
    .stHeader {
        font-family: 'Merriweather', serif !important;
        color: var(--text-color) !important;
    }

    .stApp,
    .stMarkdown,
    .stChatMessage,
    p,
    div {
        font-family: 'Lato', sans-serif !important;
        color: var(--text-color) !important;
    }

    .stApp {
        background-color: var(--background-color) !important;
    }

    /* --- CORRECTIF BARRE DU BAS (INPUT) --- */
    div[data-testid="stBottom"] {
        background-color: var(--background-color) !important;
        border-top: 1px solid var(--border-color);
    }

    .stChatInput textarea {
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
    }

    .stChatInput textarea::placeholder {
        color: var(--text-muted-color) !important;
    }

    /* --- CORRECTIF BOUTONS DE LIEN (LINKEDIN / MAIL) --- */
    div[data-testid="stLinkButton"] > a {
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        display: flex;
        justify-content: center;
        align-items: center;
    }

    div[data-testid="stLinkButton"] > a:hover {
        border-color: var(--primary-color) !important;
        color: var(--primary-color) !important;
        background-color: var(--hover-tint) !important;
    }

    /* --- BOUTONS CLASSIQUES (SUGGESTIONS) --- */
    div.stButton > button {
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px;
    }

    div.stButton > button:hover {
        border-color: var(--primary-color) !important;
        color: var(--primary-color) !important;
    }

    /* --- BOUTONS PERSONNALISÉS AVEC IMAGES --- */
    a.custom-img-btn {
        display: flex !important;
        align-items: center;
        justify-content: center;
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 0.5rem 0.75rem; /* Ajustez selon la hauteur désirée */
        text-decoration: none;
        font-weight: 600;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        transition: all 0.2s;
        width: 100%; /* Prend toute la largeur de la colonne */
        box-sizing: border-box;
    }

    a.custom-img-btn:hover {
        border-color: var(--primary-color);
        color: var(--primary-color);
        background-color: var(--hover-tint);
    }

    a.custom-img-btn img {
        width: 20px; /* Taille de l'icône */
        height: 20px;
        margin-right: 10px; /* Espace entre icône et texte */
        object-fit: contain;
    }
    
    /* --- AVATARS --- */
    div[data-testid="stChatMessage"] .stImage,
    div[data-testid="stChatMessage"] .stImage > img {
        width: 85px !important;
        height: 85px !important;
        border-radius: 50%;
        object-fit: cover;
    }

    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color) !important;
        border-right: 1px solid var(--border-color);
    }

    [data-testid="stSidebar"] * {
        color: var(--text-color) !important;
    }

    /* --- CSS POUR ALIGNER IMAGE + BOUTON --- */
    div[data-testid="column"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }

    div[data-testid="column"] img {
        margin-bottom: 8px !important;
        object-fit: contain;
    }

    div[data-testid="column"] button {
        width: 100%;
        margin-top: 0px;
    }
    
    div[data-testid="stChatInput"] button {
        color: var(--primary-color) !important;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# 2. LOGIQUE BACKEND & OUTILS
# ================================
@Tool(
    name="search_portfolio",
    description="Cherche dans le CV et le parcours de Quentin."
)
def search_portfolio(query: str) -> str:
    status_container = st.empty()
    try:
        with status_container.status("📚 Consultation de la base...", expanded=True) as status:
            index = st.session_state.get("upstash_index")
            if not index:
                return "Erreur: DB non connectée."
            
            # --- DEBUG : Vérifier la requête ---
            print(f"🔍 DEBUG QUERY: '{query}'")
            
            # Appel Upstash
            res = index.query(
                data=query, 
                top_k=int(os.getenv("UPSTASH_TOP_K", "5")),
                include_metadata=True, 
                include_data=True
            )
            
            # --- DEBUG : Voir le résultat brut ---
            print(f"📦 DEBUG RESULT RAW: {res}")
            
            if not res:
                print("❌ DEBUG: Résultat vide !")
                status.update(label="⚠️ Aucune info trouvée.", state="complete")
                return "Aucune information trouvée dans la base de données pour cette requête."
                
            # Construction du contexte
            context = "\n".join([f"- [{r.metadata.get('source', 'Doc')}] {r.data}" for r in res])
            
            print(f"✅ DEBUG CONTEXT SENT TO LLM:\n{context[:200]}...") # Affiche les 200 premiers chars
            
            status.update(label="✅ Infos récupérées !", state="complete", expanded=False)
            return f"CONTEXTE TROUVÉ :\n{context}"
            
    except Exception as e:
        print(f"🔥 DEBUG ERROR: {e}")
        return f"Erreur technique: {e}"
    finally:
        time.sleep(1)
        status_container.empty()

def initialize_resources():
    # Init Upstash
    if "upstash_index" not in st.session_state:
        url = os.getenv("UPSTASH_VECTOR_REST_URL")
        token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
        if url and token:
            try:
                st.session_state.upstash_index = Index(url=url, token=token)
                # Test de connexion simple
                st.session_state.upstash_index.info()
                st.session_state.upstash_status = True
            except:
                st.session_state.upstash_status = False
        else:
            st.session_state.upstash_status = False

    # Init Groq Agent
    if "agent" not in st.session_state:
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            try:
                sys_prompt = """Tu es l'assistant professionnel de Quentin Chabot.
                Ton objectif : Convaincre le recruteur par des faits précis issus du contexte.
                RÈGLE ABSOLUE : Tu DOIS utiliser l'outil `search_portfolio` si la question porte sur le parcours, les études ou les compétences de Quentin.
                Ne réponds jamais "de tête" sur son parcours. Utilise l'outil.
                Sois synthétique et professionnel."""
                
                st.session_state.agent = Agent(
                    name="QuentinAI",
                    instructions=sys_prompt,
                    tools=[search_portfolio],
                    provider=GroqProvider(api_key),
                    model=os.getenv("GROQ_MODEL")
                )
                st.session_state.groq_status = True
            except:
                st.session_state.groq_status = False
        else:
            st.session_state.groq_status = False

def stream_text(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)

def get_base64_image(image_path):
    """Encode une image locale en base64 pour l'HTML."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

def render_custom_button(url, text, icon_path_or_url):
    """Affiche un bouton HTML avec image."""
    
    # Détection : est-ce une URL web ou un fichier local ?
    if icon_path_or_url.startswith("http"):
        img_src = icon_path_or_url
    else:
        # Gestion fichier local
        b64 = get_base64_image(icon_path_or_url)
        # Détection extension basique
        ext = "png" if icon_path_or_url.endswith("png") else "svg+xml"
        img_src = f"data:image/{ext};base64,{b64}"

    btn_html = f"""
    <a href="{url}" target="_blank" class="custom-img-btn">
        <img src="{img_src}">
        {text}
    </a>
    """
    st.markdown(btn_html, unsafe_allow_html=True)

def render_action_button(text, icon_url, key_param):
    """
    Affiche un bouton style 'Contact' qui recharge la page avec un paramètre URL.
    target="_self" est crucial pour ne pas ouvrir un nouvel onglet.
    """
    btn_html = f"""
    <a href="?topic={key_param}" target="_self" class="custom-img-btn">
        <img src="{icon_url}">
        {text}
    </a>
    """
    st.markdown(btn_html, unsafe_allow_html=True)
# ================================
# 3. INTERFACE UTILISATEUR
# ================================

def render_sidebar():
    with st.sidebar:
        # 1. Nom tout en haut
        st.markdown("<h2 style='text-align: center; margin-top:0;'>Quentin Chabot</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #555 !important;'>Développeur / Data Scientist</p>", unsafe_allow_html=True)
        
        st.divider()

        # 2. Bouton Nouvelle Conv
        if st.button("🗑️ Nouvelle conversation", use_container_width=True):
            # On garde le message de bienvenue !
            st.session_state.messages = [{"role": "assistant", "content": "Bonjour ! Je suis l'IA de Quentin. Comment puis-je vous renseigner sur son profil ?"}]
            st.rerun()
            
        st.divider()

        # 3. Status avec icônes
        groq_ok = st.session_state.get("groq_status", False)
        upstash_ok = st.session_state.get("upstash_status", False)
        
        # Helper interne pour afficher le status proprement
        def status_row(label, is_ok):
            icon = ICON_CHECK if is_ok else ICON_ERROR
            color = "#2e7d32" if is_ok else "#c62828"
            status_text = "Opérationnel" if is_ok else "Erreur"
            
            st.markdown(f"""
            <div style="display:flex; align-items:center; margin-bottom:12px; background:#f9f9f9; padding:8px; border-radius:8px;">
                <img src="{icon}" style="width:24px; height:24px; margin-right:10px;">
                <div>
                    <div style="font-weight:bold; font-size:0.9rem;">{label}</div>
                    <div style="font-size:0.8rem; color:{color} !important;">{status_text}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        status_row("Intelligence (LLM)", groq_ok)
        status_row("Mémoire (Vector DB)", upstash_ok)

def main():
    initialize_resources()
    render_sidebar()

    # Titre et Sous-titre
    st.markdown("<br><h2 style='text-align: center; color: #333;'>Échangez avec Quentin !</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #555; font-size: 1.1rem;'>Posez vos questions sur mon parcours académique et mes expériences.</p><br>", unsafe_allow_html=True)

    # Initialisation historique
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Bonjour. Je suis l'assistant virtuel de Quentin. Quel aspect de son profil souhaitez-vous approfondir aujourd'hui ?"}]

    # Affichage historique
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
             avatar = BOT_AVATAR if os.path.exists(BOT_AVATAR) else "🤖"
        else:
             avatar = USER_AVATAR

        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # ---------------------------------------------------------
    # LOGIQUE D'AFFICHAGE ET D'INPUT
    # ---------------------------------------------------------

    prompt_to_process = None

    # 1. Calcul du seuil pour afficher les contacts (sans bloquer)
    user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
    show_contact = len(user_msgs) >= THRESHOLD_QUESTIONS

    # 2. Gestion des clics via URL (Boutons suggestions)
    if "topic" in st.query_params:
        topic = st.query_params["topic"]
        if topic == "studies": prompt_to_process = "Quel est ton parcours académique ?"
        elif topic == "exp": prompt_to_process = "Détaille tes expériences pro."
        elif topic == "tech": prompt_to_process = "Quelles sont tes compétences techniques ?"
        elif topic == "soft": prompt_to_process = "Quelles sont tes qualités humaines ?"
        st.query_params.clear()

    # 3. Affichage des Suggestions (Seulement au début)
    # On ne les affiche plus si le bloc contact est visible pour ne pas surcharger
    if len(st.session_state.messages) == 1 and not show_contact and not prompt_to_process:
        c1, c2, c3, c4 = st.columns(4)
        with c1: render_action_button("Études", ICON_GRADUATION, "studies")
        with c2: render_action_button("Expériences", ICON_WORK, "exp")
        with c3: render_action_button("Compétences techniques", ICON_TECH, "tech")
        with c4: render_action_button("Soft Skills", ICON_BRAIN, "soft")

    # 4. Affichage du bloc Contact (Si seuil atteint)
    if show_contact:
        st.divider()
        st.markdown("<h4 style='text-align: center;'>Passons au réel</h4>", unsafe_allow_html=True)
        st.info("L'IA c'est bien, l'humain c'est mieux. Retrouvez-moi sur mes canaux professionnels habituels.")
        
        c1, c2 = st.columns(2)
        with c1: render_custom_button("mailto:quentin.chabot@etu.univ-poitiers.fr", "M'envoyer un Email", ICON_MAIL)
        with c2: render_custom_button("https://fr.linkedin.com/in/chabotquentin", "Mon Profil LinkedIn", ICON_LINKEDIN)
        
        st.write("") # Petit espace visuel avant l'input

    # 5. Input Utilisateur (TOUJOURS VISIBLE)
    # C'est ici le changement : pas de 'else', l'input est toujours là.
    user_input = st.chat_input("Posez votre question ici...", key="chat_input")
    if user_input: 
        prompt_to_process = user_input

    # ---------------------------------------------------------
    # TRAITEMENT DE LA RÉPONSE
    # ---------------------------------------------------------
    # On a retiré la condition "and not should_lock"
    if prompt_to_process:
        
        # A. Ajout message user
        st.session_state.messages.append({"role": "user", "content": prompt_to_process})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt_to_process)

        # B. Génération réponse
        avatar_assistant = BOT_AVATAR if os.path.exists(BOT_AVATAR) else "🤖"
        with st.chat_message("assistant", avatar=avatar_assistant):
            placeholder = st.empty()
            full_res = ""
            
            if st.session_state.get("groq_status") and st.session_state.get("upstash_status"):
                with st.spinner("Analyse de la demande en cours..."):
                    try:
                        raw_res = st.session_state.agent.run(prompt_to_process).get_text()
                    except Exception as e:
                        raw_res = f"Une erreur est survenue lors du traitement : {e}"
            elif not st.session_state.get("groq_status"):
                 raw_res = "⚠️ Le service d'intelligence artificielle (Groq) n'est pas connecté. Impossible de répondre."
            elif not st.session_state.get("upstash_status"):
                 raw_res = "⚠️ La base de connaissances (Upstash) est inaccessible. Je ne peux pas accéder à mon parcours."

            # Streaming
            for chunk in stream_text(raw_res):
                full_res += chunk
                placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            
            st.session_state.messages.append({"role": "assistant", "content": full_res})
        
        time.sleep(0.5)
        st.rerun()

if __name__ == "__main__":
    main()