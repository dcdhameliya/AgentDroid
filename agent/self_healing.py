import subprocess
import os
from typing import Optional, Dict, Any
from providers.base import BaseProvider, Message
from android.device import ADBDevice

class SelfHealingAgent:
    def __init__(self, provider: BaseProvider, device: ADBDevice):
        self.provider = provider
        self.device = device

    def heal(self, script_path: str) -> str:
        """Runs a script, captures failure, and suggests a fix using Vision."""
        if not os.path.exists(script_path):
            return f"Script {script_path} not found."

        print(f"Running script to capture failure: {script_path}")
        result = subprocess.run(['python3', script_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            return "Script passed! No healing needed."

        error_output = result.stderr
        print(f"Detected failure:\n{error_output}")

        # Capture visual state at point of failure
        screenshot_path = "failure_state.png"
        self.device.screenshot(screenshot_path)
        
        # Capture structural state
        ui_dump_path = "failure_state.xml"
        self.device.dump_ui(ui_dump_path)
        with open(ui_dump_path, "r") as f:
            ui_content = f.read()

        with open(script_path, "r") as f:
            script_content = f.read()

        prompt = f"""
The following Python test script failed:
```python
{script_content}
```

Error details:
{error_output}

I have captured the current screen state (UI Hierarchy below and Screenshot attached).
Analyze why the script failed (e.g., a button ID changed or an element moved).
Suggest the EXACT code change needed to fix the script.

UI Hierarchy:
{ui_content}
"""
        
        print("Analyzing failure with Vision...")
        messages = [
            Message(role="system", content="You are an expert Android QA engineer specializing in self-healing test automation."),
            Message(role="user", content=prompt, image_path=screenshot_path)
        ]
        
        response = self.provider.generate(messages, tools=[])
        return response.message or "Could not determine a fix."
