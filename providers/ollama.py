import ollama
from typing import List, Dict, Any, Optional
from providers.base import BaseProvider, Message, ProviderResponse, ToolCall

class OllamaProvider(BaseProvider):
    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name

    def generate(self, messages: List[Message], tools: List[Dict[str, Any]]) -> ProviderResponse:
        # Convert messages to Ollama format
        ollama_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        # Call Ollama chat
        # Note: Ollama supports tool calling in recent versions (0.3.0+)
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=ollama_messages,
                tools=tools if tools else None
            )
        except Exception as e:
            # Fallback for older Ollama or misconfigured tools
            print(f"Warning: Ollama tool calling failed, falling back to basic chat: {e}")
            response = ollama.chat(
                model=self.model_name,
                messages=ollama_messages
            )

        provider_response = ProviderResponse()
        
        if 'message' in response:
            msg_content = response['message'].get('content', "")
            if msg_content:
                provider_response.message = msg_content
            
            if 'tool_calls' in response['message']:
                for tc in response['message']['tool_calls']:
                    provider_response.tool_calls.append(ToolCall(
                        name=tc['function']['name'],
                        arguments=tc['function']['arguments']
                    ))
        
        return provider_response
