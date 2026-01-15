# rag_backend.py
import os
from dotenv import load_dotenv
from agents import Agent, Runner
from upstash_vector import Index

load_dotenv()

# Configuration Upstash
UPSTASH_URL = os.getenv("UPSTASH_VECTOR_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
index = Index(url=UPSTASH_URL, token=UPSTASH_TOKEN)

def search_portfolio(query: str) -> str:
    """
    Cherche des informations dans le portfolio de Quentin Chabot via la base vectorielle.
    Utilise cet outil pour répondre aux questions sur le parcours, les projets ou les compétences.
    """
    try:
        res = index.query(
            data=query,
            top_k=3,
            include_metadata=True,
            include_data=True,
        )
        if not res:
            return "Aucune information pertinente trouvée."
        
        chunks = [f"- {r.data}" for r in res]
        return "\n".join(chunks)
    except Exception as e:
        return f"Erreur de recherche: {str(e)}"

# Configuration de l'agent
def get_agent():
    return Agent(
        name="Assistant Quentin",
        instructions=(
            "Tu es l'assistant professionnel de Quentin Chabot. "
            "Réponds de manière factuelle et synthétique pour un recruteur. "
            "Utilise l'outil 'search_portfolio' si la question porte sur le parcours de Quentin. "
            "Si l'info n'est pas trouvée, dis-le clairement."
        ),
        tools=[search_portfolio],  # On passe la fonction directement, la lib gère l'introspection
        model="llama-3.3-70b-versatile" # Modèle Groq
    )

def run_agent_query(user_input: str) -> str:
    agent = get_agent()
    result = Runner.run_sync(agent, user_input)
    return result.final_output