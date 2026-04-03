import sys
import os
from typing import List, Optional

# Add vendor/claw_code to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAW_CODE_PATH = os.path.join(BASE_DIR, "vendor", "claw_code")
sys.path.append(CLAW_CODE_PATH)

from src.runtime import PortRuntime
from agentdroid.android.device import ADBDevice
from agentdroid.agent.runtime import AgentRuntime
from agentdroid.providers.gemini import GeminiProvider
from agentdroid.tools.android_tools import (
    TapTool, SwipeTool, InputTextTool, ScreenshotTool, UIDumpTool, LaunchAppTool
)

from agentdroid.providers.base import BaseProvider

class ClawAgent:
    def __init__(self, device: ADBDevice, provider: Optional[BaseProvider] = None):
        self.device = device
        self.claw_runtime = PortRuntime()
        
        # Initialize AgentDroid components
        self.tools = [
            TapTool(device),
            SwipeTool(device),
            InputTextTool(device),
            ScreenshotTool(device),
            UIDumpTool(device),
            LaunchAppTool(device)
        ]
        
        self.provider = provider
        if not self.provider:
            try:
                self.provider = GeminiProvider()
            except ValueError as e:
                print(f"Warning: GeminiProvider initialization failed: {e}")
                self.provider = None
        
        if self.provider:
            self.agent_runtime = AgentRuntime(self.provider, self.tools, device)
        else:
            self.agent_runtime = None

    def execute(self, task: str):
        print(f"Routing task through Claw-Code: {task}")
        matches = self.claw_runtime.route_prompt(task)
        
        if matches:
            print("Claw-Code routed matches:")
            for match in matches:
                print(f"  - {match.kind}: {match.name} (Score: {match.score})")
        
        if not self.agent_runtime:
            return "AgentRuntime not available (check GOOGLE_API_KEY)."

        print("\nExecuting task with AgentDroid Runtime...")
        return self.agent_runtime.run(task)
