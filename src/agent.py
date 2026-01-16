import os
import dotenv
import openai
from upstash_vector import Index
from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

# 1. Charger les variables d'environnement
dotenv.load_dotenv()

# 2. Définition de l'outil de recherche sur le portfolio via upstash
@function_tool
def search_portfolio(query: str) -> str:
    """
    recherche de l'information dans le portfolio de Quentin Chabot basée sur une requête utilisateur.
    Utilise toujours cet outil lorsque l'utilisateur pose des questions sur les projets, compétences ou parcours.
    
    Args:
        query: La question spécifique ou le sujet à rechercher dans la base de données.
    """
    try:
        # Connexion à l'index (mêmes credentials que ingest_data)
        index = Index(
            url=os.getenv("UPSTASH_VECTOR_REST_URL"),
            token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
        )
        
        # Recherche des 3 chunks les plus pertinents
        # On passe 'data' directement car l'index gère l'embedding (mode hybride)
        results = index.query(
            data=query, 
            top_k=int(os.getenv("TOP_K", "3")),
            include_metadata=True,
            include_data=True
        )
        
        if not results:
            return "No relevant information found in the portfolio."

        # Formatage du contexte pour le LLM
        context_parts = []
        for res in results:
            source = res.metadata.get('source', 'unknown')
            title = res.metadata.get('title', 'Untitled')
            content = res.data
            context_parts.append(f"--- Context from {source} (Section: {title}) ---\n{content}")
            
        return "\n\n".join(context_parts)
        
    except Exception as e:
        return f"Error querying database: {str(e)}"

# 3. Définition de l'agent
portfolio_agent = Agent(
    name="Portfolio-Agent",
    instructions=(
        "Tu es un agent qui réponds aux questions sur le portfolio de Quentin Chabot en répondant en sa personne. "
        "Tu te bases strictement sur les informations fournies par l'outil 'search_portfolio'. "
        "Si l'outil ne retourne aucune information, indique clairement que tu ne sais pas."
    ),
    # Ajout de l'outil ici
    tools=[search_portfolio],
    model = OpenAIChatCompletionsModel(
        model="openai/gpt-oss-120b",
        openai_client=AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY")
        )
    )
)