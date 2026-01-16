import os
from dotenv import load_dotenv
from upstash_vector import Index
from agents import Agent, Runner, function_tool

# Chargement des variables d'environnement
load_dotenv()

# ================================
# 1. CONFIGURATION
# ================================

# Récupération des variables exactes du .env
UPSTASH_URL = os.getenv("UPSTASH_VECTOR_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
CUSTOM_API_KEY = os.getenv("openAI_API_KEY") 
MODEL_NAME = os.getenv("MODEL") 
TOP_K_STR = os.getenv("TOP_K")

# Conversion de TOP_K en entier
try:
    TOP_K = int(TOP_K_STR)
except ValueError:
    TOP_K = 3 # Valeur par défaut si erreur

# Initialisation du client Upstash
try:
    if UPSTASH_URL and UPSTASH_TOKEN:
        index = Index(url=UPSTASH_URL, token=UPSTASH_TOKEN)
    else:
        index = None
        print("Erreur: Identifiants Upstash manquants dans le .env")
except Exception as e:
    print(f"Erreur lors de l'initialisation Upstash : {e}")
    index = None

# ================================
# 2. OUTILS (TOOLS)
# ================================

def check_upstash_connection():
    """
    Vérifie la connexion à la base de données vectorielle.
    Utilisé par app.py pour l'affichage du statut.
    """
    if not index:
        return False
    try:
        index.info()
        return True
    except Exception:
        return False

@function_tool
def retrieve_context(query: str) -> str:
    """
    Recherche des informations sur Quentin Chabot dans sa base de connaissances (Portfolio, CV).
    À utiliser obligatoirement pour toute question factuelle sur son profil.
    
    Args:
        query: La question ou les mots-clés pour la recherche vectorielle.
    Returns:
        Les extraits de texte pertinents trouvés dans la base.
    """
    if not index:
        return "Erreur: Base de données vectorielle non connectée."
    
    try:
        # Recherche hybride (Keyword + Semantic) utilisant le TOP_K du .env
        results = index.query(
            data=query, 
            top_k=TOP_K, 
            include_metadata=True,
            include_data=True
        )
        
        context_parts = []
        for res in results:
            text = res.data if res.data else res.metadata.get("text", "")
            if text:
                context_parts.append(f"---\n{text}\n---")
        
        if not context_parts:
            return "Aucune information trouvée dans la documentation."
            
        return "\n".join(context_parts)

    except Exception as e:
        return f"Erreur lors de la recherche : {e}"

# ================================
# 3. DÉFINITION DE L'AGENT
# ================================

# Création de l'agent
quentin_agent = Agent(
    name="Assistant Quentin",
    model=MODEL_NAME,
    instructions=(
        "Tu es l'assistant virtuel professionnel de Quentin Chabot. "
        "Ton rôle est de répondre aux questions sur son profil (Expériences, Études, Compétences). "
        "Règles : "
        "1. Utilise TOUJOURS l'outil 'retrieve_context' pour vérifier les faits avant de répondre. "
        "2. Si l'info n'est pas dans le contexte, dis que tu ne sais pas. "
        "3. Sois professionnel et courtois dans tes réponses, donne des réponses complètes et précises."
    ),
    tools=[retrieve_context]
)

# ================================
# 4. EXÉCUTION (RUNNER)
# ================================

def run_agent_query(user_query: str) -> str:
    """
    Exécute l'agent via le Runner de openai-agents.
    """
    try:
        # Lancement synchrone de l'agent
        result = Runner.run_sync(
            starting_agent=quentin_agent,
            input=user_query
        )
        
        # On retourne la sortie finale
        return str(result.final_output)

    except Exception as e:
        return f"Erreur lors de l'exécution de l'agent : {e}"