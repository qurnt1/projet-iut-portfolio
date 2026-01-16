"""
Backend RAG (Retrieval Augmented Generation) pour l'assistant virtuel.

Ce module implémente le cœur du système RAG :
    - Connexion à la base de données vectorielle Upstash
    - Tool de récupération de contexte pour l'agent
    - Configuration et exécution de l'agent OpenAI

L'agent utilise la bibliothèque `openai-agents` et interroge Upstash Vector
via une recherche hybride (sémantique + keywords) pour répondre aux questions
sur le profil de Quentin Chabot.

Exports:
    - run_agent_query: Fonction principale pour exécuter une requête utilisateur.
    - check_upstash_connection: Vérifie l'état de la connexion à Upstash.
"""

import os
from typing import Optional, List

from dotenv import load_dotenv
from upstash_vector import Index
from agents import Agent, Runner, function_tool

# Chargement des variables d'environnement depuis .env
load_dotenv()


# ============================================================================
# CONFIGURATION
# ============================================================================

# Récupération des credentials et paramètres depuis les variables d'environnement
UPSTASH_URL: Optional[str] = os.getenv("UPSTASH_VECTOR_REST_URL")
UPSTASH_TOKEN: Optional[str] = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
CUSTOM_API_KEY: Optional[str] = os.getenv("openAI_API_KEY")
MODEL_NAME: Optional[str] = os.getenv("MODEL")
TOP_K_STR: Optional[str] = os.getenv("TOP_K")

# Conversion sécurisée de TOP_K avec valeur par défaut
try:
    TOP_K: int = int(TOP_K_STR) if TOP_K_STR else 3
except ValueError:
    TOP_K = 3  # Fallback si la valeur n'est pas un entier valide

# Initialisation du client Upstash Vector (singleton au niveau module)
index: Optional[Index] = None
try:
    if UPSTASH_URL and UPSTASH_TOKEN:
        index = Index(url=UPSTASH_URL, token=UPSTASH_TOKEN)
    else:
        print("Erreur: Identifiants Upstash manquants dans le .env")
except Exception as e:
    print(f"Erreur lors de l'initialisation Upstash : {e}")


# ============================================================================
# OUTILS (TOOLS) POUR L'AGENT
# ============================================================================

def check_upstash_connection() -> bool:
    """
    Vérifie la connexion à la base de données vectorielle Upstash.

    Cette fonction est utilisée par l'interface Streamlit pour afficher
    le statut de la connexion dans la sidebar.

    Returns:
        True si la connexion est établie et fonctionnelle, False sinon.

    Example:
        >>> if check_upstash_connection():
        ...     print("Base de données connectée")
    """
    if not index:
        return False
    try:
        index.info()  # Appel léger pour vérifier la connectivité
        return True
    except Exception:
        return False


@function_tool
def retrieve_context(query: str) -> str:
    """
    Recherche des informations sur Quentin Chabot dans sa base de connaissances.

    Cette fonction est exposée comme Tool à l'agent OpenAI. Elle effectue
    une recherche hybride (sémantique + BM25) dans Upstash Vector pour
    retrouver les extraits de portfolio les plus pertinents.

    Args:
        query: La question ou les mots-clés pour la recherche vectorielle.
               Peut être une phrase complète ou des termes isolés.

    Returns:
        Les extraits de texte pertinents trouvés, séparés par des délimiteurs.
        En cas d'erreur, retourne un message explicatif.

    Note:
        L'agent doit utiliser cette fonction pour toute question factuelle
        sur le profil, les compétences ou les expériences de Quentin.
    """
    if not index:
        return "Erreur: Base de données vectorielle non connectée."

    try:
        # Recherche hybride : combine embedding dense (sémantique) et sparse (BM25)
        results = index.query(
            data=query,
            top_k=TOP_K,
            include_metadata=True,
            include_data=True
        )

        # Extraction et formatage des résultats
        context_parts: List[str] = []
        for res in results:
            # Priorité au champ data, fallback sur metadata.text
            text = res.data if res.data else res.metadata.get("text", "")
            if text:
                context_parts.append(f"---\n{text}\n---")

        if not context_parts:
            return "Aucune information trouvée dans la documentation."

        return "\n".join(context_parts)

    except Exception as e:
        return f"Erreur lors de la recherche : {e}"


# ============================================================================
# DÉFINITION DE L'AGENT
# ============================================================================

# Instructions système définissant le comportement de l'agent
_AGENT_INSTRUCTIONS: str = (
    "Tu es l'assistant virtuel professionnel de Quentin Chabot. "
    "Ton rôle est de répondre aux questions sur son profil (Expériences, Études, Compétences). "
    "Règles : "
    "1. Utilise TOUJOURS l'outil 'retrieve_context' pour vérifier les faits avant de répondre. "
    "2. Si l'info n'est pas dans le contexte, dis que tu ne sais pas. "
    "3. Sois professionnel et courtois dans tes réponses, donne des réponses complètes et précises."
)

# Instanciation de l'agent avec sa configuration
quentin_agent: Agent = Agent(
    name="Assistant Quentin",
    model=MODEL_NAME,
    instructions=_AGENT_INSTRUCTIONS,
    tools=[retrieve_context]
)


# ============================================================================
# EXÉCUTION (RUNNER)
# ============================================================================

def run_agent_query(user_query: str) -> str:
    """
    Exécute une requête utilisateur via l'agent OpenAI.

    Cette fonction est le point d'entrée principal appelé par l'interface
    Streamlit. Elle gère l'exécution synchrone de l'agent et retourne
    sa réponse finale.

    Args:
        user_query: La question posée par l'utilisateur dans le chat.

    Returns:
        La réponse générée par l'agent sous forme de chaîne de caractères.
        En cas d'erreur, retourne un message d'erreur formaté.

    Raises:
        Aucune exception levée directement ; les erreurs sont capturées
        et retournées sous forme de message.

    Example:
        >>> response = run_agent_query("Quelles sont tes compétences en Python ?")
        >>> print(response)
    """
    try:
        # Exécution synchrone : bloque jusqu'à obtention de la réponse complète
        result = Runner.run_sync(
            starting_agent=quentin_agent,
            input=user_query
        )

        return str(result.final_output)

    except Exception as e:
        return f"Erreur lors de l'exécution de l'agent : {e}"