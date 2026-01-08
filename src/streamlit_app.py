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
MEMORY_WINDOW = 6

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
# Injection CSS : Polices Google, Taille Avatars, Style Claude
st.markdown("""<style>
    /* --- IMPORT POLICES --- */
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Lato:wght@300;400;700&display=swap');

    /* --- GLOBAL PALETTE --- */
    :root {
        --primary-color: #D97757;              /* Orange */
        --background-color: "#eee8d1ff"         /* Light */
        --secondary-background-color: #eee8d1ff; /* White */
        --text-color: #141413;                 /* Dark */
        --text-muted-color: #B0AEA5;           /* Gray */
        --border-color: #E8E6DC;               /* Border Gray */
        --hover-tint: #FFF8F5;                 /* Warm Hover */
    }

    h1, h2, h3, h4, .stHeader {
        font-family: 'Merriweather', serif !important;
        color: var(--text-color) !important;
    }

    .stApp, .stMarkdown, .stChatMessage, p, div {
        font-family: 'Lato', sans-serif !important;
        color: var(--text-color) !important;
    }

    .stApp {
        background-color: var(--background-color) !important;
    }

    /* --- BARRE DU BAS (INPUT) --- */
    div[data-testid="stBottom"] {
        background-color: var(--background-color) !important;
        border-top: 1px solid var(--border-color);
    }

    /* --- MODIFICATION : ZONE DE SAISIE (CAPSULE) --- */
    div[data-testid="stChatInput"] > div {
        border-color: var(--primary-color) !important;
        border-width: 2px !important;
        border-radius: 25px !important;
        background-color: var(--secondary-background-color) !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    }

    .stChatInput textarea {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: var(--text-color) !important;
        padding-top: 0.5rem !important;
    }

    div[data-testid="stChatInput"] > div:focus-within {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 1px var(--primary-color) !important;
    }

    .stChatInput textarea::placeholder {
        color: var(--text-muted-color) !important;
    }

    /* --- BOUTON SIDEBAR (CHEVRON) --- */
    div[data-testid="stHeader"] button {
        color: var(--primary-color) !important;
        border: none !important;
        background-color: transparent !important;
    }
    div[data-testid="stHeader"] button:hover {
        color: var(--primary-color) !important;
        background-color: var(--hover-tint) !important;
    }

    /* --- BOUTONS SUGGESTIONS (CUSTOM) --- */
    a.custom-img-btn {
        display: flex !important;
        align-items: center;
        justify-content: center;
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 2px solid var(--primary-color);
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        text-decoration: none;
        font-weight: 600;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        transition: all 0.2s;
        width: 100%;
        box-sizing: border-box;
    }

    a.custom-img-btn:hover {
        border-color: var(--primary-color);
        color: var(--primary-color) !important;
        background-color: var(--hover-tint);
    }

    a.custom-img-btn img {
        width: 20px;
        height: 20px;
        margin-right: 10px;
        object-fit: contain;
    }

    /* --- LIENS STDLIB --- */
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

    /* --- ALIGNEMENT COLONNES --- */
    div[data-testid="column"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
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
    description="Moteur de recherche indispensable pour répondre aux questions sur Quentin (CV, email, expériences, études). L'argument 'query' est la question posée."
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

def prune_agent_memory(agent, limit=6):
    """
    Nettoie la mémoire en s'assurant de ne pas casser les paires question/outil.
    """
    try:
        # 1. Récupération des messages
        messages = None
        if hasattr(agent, "messages"):
            messages = agent.messages
        elif hasattr(agent, "memory") and hasattr(agent.memory, "messages"):
            messages = agent.memory.messages
            
        if not messages:
            return

        # 2. On isole le System Prompt (toujours index 0)
        sys_msg = messages[0] if messages and messages[0].get("role") == "system" else None
        
        # 3. On prend les 'limit' derniers messages du reste
        # On exclut le system prompt du slicing pour le remettre après
        history = messages[1:] if sys_msg else messages
        kept_msgs = history[-limit:]

        # --- CORRECTION CRITIQUE (SANITIZATION) ---
        # Si le premier message conservé est une réponse d'outil ("tool") ou un résultat,
        # mais qu'on a effacé la demande de l'assistant juste avant, Groq va planter.
        # Donc, si le premier message est un "tool", on le vire.
        while kept_msgs and kept_msgs[0].get("role") == "tool":
            kept_msgs.pop(0)
            
        # Idem, si le premier message est un assistant qui appelle un outil, 
        # mais qu'on a pas l'outil précédent (cas rare mais possible), on nettoie.
        # Pour Llama 3, on s'assure juste que le premier message n'est pas orphelin.
        
        # 4. Reconstitution
        new_history = [sys_msg] + kept_msgs if sys_msg else kept_msgs
        
        # 5. Application
        if hasattr(agent, "messages"):
            agent.messages = new_history
        elif hasattr(agent, "memory"):
            agent.memory.messages = new_history
            
    except Exception as e:
        print(f"Warning prune: {e}")

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

                RÈGLES D'AFFICHAGE :
                - Ne cite JAMAIS les sources, noms d'outils ou numéros de lignes dans ta réponse finale (ex: ne mets pas [search_portfolio], [L12-14]).
                - Intègre les informations naturellement dans le texte sans balises techniques.

                INSTRUCTIONS :
                - Si la question porte sur le parcours, les études ou les compétences, utilise l'outil search_portfolio pour trouver la réponse.
                - Ne réponds jamais "de tête" sur son parcours. Utilise l'outil.
                - Sois synthétique et professionnel."""
                
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
        st.markdown("<h2 style='text-align: center; margin-top:0;'>Quentin Chabot</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #555 !important;'>Développeur / Data Scientist</p>", unsafe_allow_html=True)
        
        st.divider()

        if st.button("🗑️ Nouvelle conversation", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": "Bonjour ! Je suis l'IA de Quentin. Comment puis-je vous renseigner sur son profil ?"}]
            st.rerun()
            
        st.divider()

        st.markdown("### État du système")

        # Récupération de l'état
        groq_ok = st.session_state.get("groq_status", False)
        upstash_ok = st.session_state.get("upstash_status", False)
        
        # Fonction interne corrigée pour l'affichage HTML
        def status_row(label, is_ok):
            if is_ok:
                icon_url = ICON_CHECK
                bg_color = "#e8f5e9"    # Vert pâle
                border_color = "#a5d6a7"
                text_color = "#2e7d32"
                status_text = "Connecté"
            else:
                icon_url = ICON_ERROR
                bg_color = "#ffebee"    # Rouge pâle
                border_color = "#ef9a9a"
                text_color = "#c62828"
                status_text = "Déconnecté"
            
            # HTML compacté pour éviter les erreurs d'indentation Python
            html_code = f"""
            <div style="display:flex; align-items:center; margin-bottom:10px; background-color:{bg_color}; border:1px solid {border_color}; padding:10px; border-radius:8px;">
                <img src="{icon_url}" style="width:24px; height:24px; margin-right:12px; object-fit:contain;">
                <div style="line-height: 1.2;">
                    <div style="font-weight:bold; font-size:0.9rem; color:{text_color};">{label}</div>
                    <div style="font-size:0.8rem; color:{text_color}; opacity:0.9;">{status_text}</div>
                </div>
            </div>
            """
            
            # C'est cette ligne qui fait la magie : unsafe_allow_html=True
            st.markdown(html_code, unsafe_allow_html=True)

        status_row("Intelligence Artificielle (LLM)", groq_ok)
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
        st.markdown("<h4 style='text-align: center;'>Passons au réel,</h4>", unsafe_allow_html=True)
        st.info("L'IA c'est bien, l'humain c'est mieux. Retrouvez-moi sur mes canaux professionnels.")
        
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
    # ---------------------------------------------------------
    # TRAITEMENT DE LA RÉPONSE (AVEC RETRY AUTOMATIQUE)
    # ---------------------------------------------------------
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
            
            # Vérification des services
            if not st.session_state.get("groq_status"):
                full_res = "⚠️ Le service d'intelligence artificielle (Groq) n'est pas connecté."
            elif not st.session_state.get("upstash_status"):
                full_res = "⚠️ La base de connaissances (Upstash) est inaccessible."
            else:
                # --- LOGIQUE DE RETRY ---
                max_retries = 3
                success = False
                
                with st.spinner("Analyse en cours..."):
                    for attempt in range(max_retries):
                        try:
                            # 1. Nettoyage préventif de l'historique
                            prune_agent_memory(st.session_state.agent, MEMORY_WINDOW)
                            
                            # 2. Tentative d'exécution
                            raw_res = st.session_state.agent.run(prompt_to_process).get_text()
                            success = True
                            break # Si ça passe, on sort de la boucle
                            
                        except Exception as e:
                            error_msg = str(e)
                            print(f"⚠️ Tentative {attempt+1}/{max_retries} échouée : {error_msg}")
                            
                            # Si c'est l'erreur spécifique de Groq sur les Tools ou le templating
                            if "Tools should have a name" in error_msg or "HarmonyError" in error_msg:
                                # STRATÉGIE DE RÉPARATION : On reset la mémoire de l'agent pour cette requête
                                # On garde le prompt système, mais on vide l'historique corrompu
                                if hasattr(st.session_state.agent, "memory"):
                                    st.session_state.agent.memory.messages = [] 
                                elif hasattr(st.session_state.agent, "messages"):
                                    # On garde juste le system prompt s'il existe
                                    sys_msg = st.session_state.agent.messages[0] if st.session_state.agent.messages else None
                                    st.session_state.agent.messages = [sys_msg] if sys_msg else []
                                
                                # On attend un peu avant de réessayer
                                time.sleep(1)
                            else:
                                # Pour les autres erreurs, on attend juste
                                time.sleep(1)

                    if not success:
                        full_res = "Une erreur technique persistante empêche la réponse. Veuillez reformuler ou rafraîchir la page."
                    else:
                        full_res = raw_res

            # Affichage du résultat final (ou de l'erreur)
            # Streaming simulé pour l'effet visuel si succès
            if success:
                temp_text = ""
                for chunk in stream_text(full_res):
                    temp_text += chunk
                    placeholder.markdown(temp_text + "▌")
                placeholder.markdown(full_res)
            else:
                placeholder.error(full_res)
            
            st.session_state.messages.append({"role": "assistant", "content": full_res})
        
        # Petit délai pour laisser l'UI se mettre à jour avant le rerun
        time.sleep(0.5)
        st.rerun()

if __name__ == "__main__":
    main()