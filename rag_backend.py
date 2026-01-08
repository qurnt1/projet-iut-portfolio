import json
import inspect
from openai import OpenAI

# ==========================================
# MOTEUR RAG SIMPLIFIÉ (rag_backend.py)
# ==========================================

class OpenAIProvider:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

class Tool:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.func = None

    def __call__(self, func):
        self.func = func
        return self

    def execute(self, **kwargs):
        return self.func(**kwargs)

    def to_schema(self):
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
    def __init__(self, text):
        self.text = text
    
    def get_text(self):
        return self.text
    
    def __str__(self):
        return self.text

class Agent:
    def __init__(self, name, instructions, tools, provider, model="gpt-4.1-nano"):
        self.name = name
        self.instructions = instructions
        self.tools = {t.name: t for t in tools} if tools else {}
        self.client = provider.client
        self.model = model
        self.messages = [{"role": "system", "content": instructions}]

    def run(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        
        api_tools = [t.to_schema() for t in self.tools.values()] if self.tools else None

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=api_tools,
            tool_choice="auto" if api_tools else None
        )

        message = response.choices[0].message
        final_text = ""

        if message.tool_calls:
            self.messages.append(message)
            
            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                if fn_name in self.tools:
                    try:
                        tool_result = self.tools[fn_name].execute(**args)
                    except Exception as e:
                        tool_result = f"Error executing tool: {e}"
                    
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result)
                    })
            
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages
            )
            final_text = final_response.choices[0].message.content
        else:
            final_text = message.content

        self.messages.append({"role": "assistant", "content": final_text})
        return AgentResponse(final_text)