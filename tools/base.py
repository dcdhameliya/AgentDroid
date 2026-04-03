from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

class ToolResult(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None

class BaseTool(ABC):
    name: str
    description: str
    parameters: Dict[str, Any]

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        pass

class AndroidTool(BaseTool):
    def __init__(self, device):
        self.device = device
