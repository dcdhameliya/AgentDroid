import google.generativeai as genai
from typing import List, Dict, Any, Optional
import os
from PIL import Image
from agentdroid.providers.base import BaseProvider, Message, ProviderResponse, ToolCall

class GeminiProvider(BaseProvider):
    def __init__(self, model_name: str = "gemini-2.0-flash", api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY must be set in environment or passed to provider.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate(self, messages: List[Message], tools: List[Dict[str, Any]]) -> ProviderResponse:
        # Prepare tool definitions
        model_tools = []
        if tools:
            model_tools = [{"function_declarations": tools}]

        # Prepare message history
        history = []
        for msg in messages[:-1]:
            role = "user" if msg.role == "user" else "model"
            parts = [msg.content]
            if msg.image_path and os.path.exists(msg.image_path):
                img = Image.open(msg.image_path)
                parts.append(img)
            history.append({"role": role, "parts": parts})
        
        last_msg = messages[-1]
        last_parts = [last_msg.content]
        if last_msg.image_path and os.path.exists(last_msg.image_path):
            img = Image.open(last_msg.image_path)
            last_parts.append(img)
        
        chat = self.model.start_chat(history=history)
        response = chat.send_message(last_parts, tools=model_tools)
        
        provider_response = ProviderResponse()
        
        # Handle response
        if response.candidates[0].content.parts:
            parts = response.candidates[0].content.parts
            text_parts = [p.text for p in parts if hasattr(p, 'text') and p.text]
            if text_parts:
                provider_response.message = "\n".join(text_parts)
            
            # Handle function calls
            for part in parts:
                if fn := part.function_call:
                    tool_call = ToolCall(
                        name=fn.name,
                        arguments=dict(fn.args)
                    )
                    provider_response.tool_calls.append(tool_call)
        
        return provider_response
