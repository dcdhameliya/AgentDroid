from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str
    image_path: Optional[str] = None

class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

class ProviderResponse(BaseModel):
    message: Optional[str] = None
    tool_calls: List[ToolCall] = []

class BaseProvider(ABC):
    @abstractmethod
    def generate(self, messages: List[Message], tools: List[Dict[str, Any]]) -> ProviderResponse:
        pass
