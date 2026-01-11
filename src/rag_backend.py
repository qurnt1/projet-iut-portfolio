# rag_backend.py
import os
from dotenv import load_dotenv

# Librairie "agents" (openai-agents)
from agents import Agent as OpenAIAgent, Runner, Tool as AgentTool

load_dotenv()

# Groq = endpoint OpenAI-compatible
os.environ.setdefault("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
if os.getenv("GROQ_API_KEY") and not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY")


class AgentResponse:
    def __init__(self, text: str):
        self.text = text

    def get_text(self) -> str:
        return self.text


class Tool:
    """Décorateur simplifié: @Tool(name=..., description=...)"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.func = None

    def __call__(self, func):
        self.func = func
        if not func.__doc__:
            func.__doc__ = self.description
        return self

    def execute(self, **kwargs):
        return self.func(**kwargs)


class Agent:
    """Wrapper qui neutralise les annotations (fix typing.Union) avant de créer les tools."""

    def __init__(self, name: str, instructions: str, tools: list, provider=None, model: str = ""):
        native_tools = []

        for t in tools:
            fn = t.func

            # FIX: empêcher l'analyse pydantic/openai-agents sur des Union / types problématiques
            try:
                fn.__annotations__ = {}
            except Exception:
                pass

            native_tools.append(
                AgentTool(
                    name=t.name,
                    fn=fn,
                    description=t.description,
                )
            )

        self.native_agent = OpenAIAgent(
            name=name,
            instructions=instructions,
            tools=native_tools,
            model=model,
        )

    def run(self, user_input: str) -> AgentResponse:
        result = Runner.run_sync(self.native_agent, user_input)
        return AgentResponse(result.final_output)
