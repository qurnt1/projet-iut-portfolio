import json
import inspect
from typing import Any, Callable, List, Dict, Optional
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage

# ==========================================
# MOTEUR RAG (Backend Optimisé)
# ==========================================

class OpenAIProvider:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

class Tool:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.func: Optional[Callable] = None

    def __call__(self, func: Callable):
        self.func = func
        return self

    def execute(self, **kwargs) -> Any:
        if not self.func:
            raise ValueError(f"Tool {self.name} has no function attached.")
        # Logs pour le développeur (apparaîtront dans le terminal)
        print(f"🔧 [TOOL EXEC] {self.name} called with: {kwargs}")
        return self.func(**kwargs)

    def to_schema(self) -> Dict[str, Any]:
        sig = inspect.signature(self.func)
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        for param_name, param in sig.parameters.items():
            parameters["properties"][param_name] = {
                "type": "string",
                "description": f"Parameter {param_name}"
            }
            parameters["required"].append(param_name)
            
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": parameters
            }
        }

class AgentResponse:
    def __init__(self, text: str):
        self.text = text
    
    def get_text(self) -> str:
        return self.text

class Agent:
    # CORRECTION : Utilisation de gpt-4o-mini (rapide/pas cher) ou gpt-4-turbo
    def __init__(self, name: str, instructions: str, tools: List[Tool], provider: OpenAIProvider, model: str = "gpt-4.1-nano"):
        self.name = name
        self.tools = {t.name: t for t in tools} if tools else {}
        self.client = provider.client
        self.model = model
        self.messages = [{"role": "system", "content": instructions}]

    def run(self, user_input: str) -> AgentResponse:
        self.messages.append({"role": "user", "content": user_input})
        
        api_tools = [t.to_schema() for t in self.tools.values()] if self.tools else None

        # 1. Premier appel LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=api_tools,
                tool_choice="auto" if api_tools else None
            )
        except Exception as e:
            return AgentResponse(f"Erreur API OpenAI: {e}")

        message = response.choices[0].message
        final_text = ""

        # 2. Gestion des Tools
        if message.tool_calls:
            self.messages.append(message.model_dump())
            
            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                if fn_name in self.tools:
                    try:
                        tool_result = self.tools[fn_name].execute(**args)
                    except Exception as e:
                        tool_result = f"Error: {e}"
                    
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result)
                    })
            
            # 3. Second appel LLM (Synthèse)
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages
            )
            final_text = final_response.choices[0].message.content
        else:
            final_text = message.content

        self.messages.append({"role": "assistant", "content": final_text})
        return AgentResponse(final_text)