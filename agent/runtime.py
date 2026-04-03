import os
import base64
from typing import List, Dict, Any, Optional
from providers.base import BaseProvider, Message, ToolCall
from tools.base import BaseTool, ToolResult
from android.device import ADBDevice

class AgentRuntime:
    def __init__(self, provider: BaseProvider, tools: List[BaseTool], device: ADBDevice):
        self.provider = provider
        self.tools = {tool.name: tool for tool in tools}
        self.device = device
        self.messages: List[Message] = []
        self.action_history: List[Dict[str, Any]] = [] # For script generation
        self.system_prompt = (
            "You are an AI assistant controlling an Android device. "
            "You have access to a screenshot and a UI hierarchy dump (XML) for each step. "
            "Use the UI hierarchy to find precise coordinates, but rely on the screenshot "
            "to understand visual context and identify custom UI elements that might not "
            "be labeled in the XML. "
            "If an app crashes or doesn't respond, analyze the logcat output provided."
        )

    def run(self, task: str, max_steps: int = 15) -> str:
        self.messages = [Message(role="system", content=self.system_prompt)]
        self.messages.append(Message(role="user", content=task))
        self.action_history = []
        
        tool_decls = []
        for tool in self.tools.values():
            tool_decls.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": tool.parameters,
                    "required": [k for k, v in tool.parameters.items() if "default" not in v]
                }
            })

        for step in range(max_steps):
            screenshot_path = f"step_{step}.png"
            ui_dump_path = f"step_{step}.xml"
            self.device.screenshot(screenshot_path)
            self.device.dump_ui(ui_dump_path)
            
            with open(ui_dump_path, "r") as f:
                ui_content = f.read()

            crash_info = self.check_crashes()
            state_msg = f"Current State (Step {step}):\nUI Hierarchy:\n{ui_content}"
            if crash_info:
                state_msg += f"\n\nCRASH DETECTED:\n{crash_info}"

            self.messages.append(Message(role="user", content=state_msg, image_path=screenshot_path))
            response = self.provider.generate(self.messages, tool_decls)
            
            if response.message:
                self.messages.append(Message(role="assistant", content=response.message))
                print(f"Assistant: {response.message}")

            if not response.tool_calls:
                return response.message or "Task completed."

            for tool_call in response.tool_calls:
                print(f"Executing tool: {tool_call.name}({tool_call.arguments})")
                tool = self.tools.get(tool_call.name)
                if not tool:
                    result = ToolResult(success=False, output="", error=f"Tool {tool_call.name} not found.")
                else:
                    result = tool.execute(**tool_call.arguments)
                    if result.success:
                        # Record successful actions
                        self.action_history.append({
                            "name": tool_call.name,
                            "arguments": tool_call.arguments
                        })
                
                result_msg = f"Tool '{tool_call.name}' returned: {result.output}"
                if result.error:
                    result_msg += f" (Error: {result.error})"
                
                self.messages.append(Message(role="user", content=result_msg))
                print(f"Result: {result_msg}")

            if os.path.exists(ui_dump_path):
                os.remove(ui_dump_path)

        return "Reached maximum steps without completion."

    def check_crashes(self) -> Optional[str]:
        try:
            logs = self.device.get_logs(limit=200)
            critical_patterns = ["FATAL EXCEPTION", "ANR in", "Process: com.", "ShortMsg:"]
            lines = logs.split("\n")
            crash_lines = []
            for line in lines:
                if any(pattern in line for pattern in critical_patterns):
                    crash_lines.append(line)
            if crash_lines:
                return "\n".join(crash_lines)
        except Exception:
            pass
        return None
