from agentdroid.tools.base import AndroidTool, ToolResult
import subprocess

class TeleportTool(AndroidTool):
    name = "teleport"
    description = "Instantly jump to a specific screen using a deep link URL."
    parameters = {
        "url": {"type": "string", "description": "The deep link URL (e.g., 'myapp://settings')"}
    }

    def execute(self, url: str) -> ToolResult:
        try:
            # -W: wait for launch to complete
            # -a: action
            # -d: data (the URL)
            cmd = ['adb', '-s', self.device.serial, 'shell', 'am', 'start', '-W', '-a', 'android.intent.action.VIEW', '-d', url]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return ToolResult(success=True, output=f"Teleported to {url}\n{result.stdout}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
