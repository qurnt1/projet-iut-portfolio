import os
import dotenv
from upstash_vector import Index
from agents import Agent, function_tool, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

dotenv.load_dotenv()

@function_tool
def search_portfolio(query: str) -> str:
    """
    recherche de l'information dans le portfolio de Quentin Chabot basée sur une requête utilisateur.
    Utilise toujours cet outil lorsque l'utilisateur pose des questions sur les projets, compétences ou parcours.
    Args:

        query: La question spécifique ou le sujet à rechercher dans la base de données.

    """ 
    try:
        index = Index(
            url=os.getenv("UPSTASH_VECTOR_REST_URL"),
            token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
        )
        
        results = index.query(
            data=query, 
            top_k=6, 
            include_metadata=True, 
            include_data=True
        )
        
        if not results:
            return "Aucune information trouvée."

        # Construction d'un contexte plus propre
        context = []
        for res in results:
            meta = res.metadata
            # Ajout explicite du type de section pour aider le LLM à structurer
            context.append(f"### Source: {meta.get('source')} | Titre: {meta.get('title')}\n{res.data}")
            
        return "\n\n".join(context)
        
    except Exception as e:
        return f"Erreur technique: {str(e)}"

portfolio_agent = Agent(
    name="Portfolio-Agent",
    instructions=(
        "Tu es Quentin Chabot (via son assistant IA). Ton rôle est d'informer les recruteurs et pairs techniques. "
        "Ton ton est professionnel, direct, analytique et concis. Pas de politesse excessive. "
        "Tu as accès à des fragments de mon portfolio via l'outil 'search_portfolio'. "
        
        "RÈGLES D'ANALYSE :"
        "1. Synthétise les informations : Si l'utilisateur demande un CV ou un résumé, combine les chunks (Formation, Expériences, Tech) pour faire une réponse structurée."
        "2. Ne dis jamais 'D'après les extraits...' ou 'Je ne trouve pas...'. Si une info manque (ex: lycée), ignore-la, concentre-toi sur ce que tu as (Master/Ingénieur)."
        "3. Si l'information est totalement absente, dis simplement : 'Cette information n'est pas disponible dans ma base actuelle'."
        "4. Mets en avant la valeur ajoutée (Impact, Stack technique, Résultats)."
    ),
    tools=[search_portfolio],
    model = OpenAIChatCompletionsModel(
        model="openai/gpt-oss-120b",
        openai_client=AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY")
        )
    )
)