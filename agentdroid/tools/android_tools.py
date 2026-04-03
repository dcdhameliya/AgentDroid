from agentdroid.tools.base import AndroidTool, ToolResult
import os

class TapTool(AndroidTool):
    name = "tap"
    description = "Tap at specific coordinates (x, y) on the screen."
    parameters = {
        "x": {"type": "integer", "description": "X coordinate"},
        "y": {"type": "integer", "description": "Y coordinate"}
    }

    def execute(self, x: int, y: int) -> ToolResult:
        try:
            self.device.tap(x, y)
            return ToolResult(success=True, output=f"Tapped at ({x}, {y})")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

class SwipeTool(AndroidTool):
    name = "swipe"
    description = "Swipe from (x1, y1) to (x2, y2) on the screen."
    parameters = {
        "x1": {"type": "integer", "description": "Starting X coordinate"},
        "y1": {"type": "integer", "description": "Starting Y coordinate"},
        "x2": {"type": "integer", "description": "Ending X coordinate"},
        "y2": {"type": "integer", "description": "Ending Y coordinate"},
        "duration": {"type": "integer", "description": "Duration in ms", "default": 300}
    }

    def execute(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> ToolResult:
        try:
            self.device.swipe(x1, y1, x2, y2, duration)
            return ToolResult(success=True, output=f"Swiped from ({x1}, {y1}) to ({x2}, {y2})")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

class InputTextTool(AndroidTool):
    name = "input_text"
    description = "Type text into the focused UI element."
    parameters = {
        "text": {"type": "string", "description": "Text to type"}
    }

    def execute(self, text: str) -> ToolResult:
        try:
            self.device.input_text(text)
            return ToolResult(success=True, output=f"Typed text: {text}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

class ScreenshotTool(AndroidTool):
    name = "screenshot"
    description = "Take a screenshot of the current screen."
    parameters = {
        "output_path": {"type": "string", "description": "Path to save the screenshot", "default": "screenshot.png"}
    }

    def execute(self, output_path: str = "screenshot.png") -> ToolResult:
        try:
            self.device.screenshot(output_path)
            return ToolResult(success=True, output=f"Screenshot saved to {output_path}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

class UIDumpTool(AndroidTool):
    name = "dump_ui"
    description = "Dump the UI hierarchy (XML) of the current screen."
    parameters = {
        "output_path": {"type": "string", "description": "Path to save the UI dump", "default": "ui_dump.xml"}
    }

    def execute(self, output_path: str = "ui_dump.xml") -> ToolResult:
        try:
            self.device.dump_ui(output_path)
            with open(output_path, "r") as f:
                dump = f.read()
            return ToolResult(success=True, output=dump)
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

class LaunchAppTool(AndroidTool):
    name = "launch_app"
    description = "Launch an application by its package name."
    parameters = {
        "package_name": {"type": "string", "description": "Package name of the app (e.g., com.android.settings)"}
    }

    def execute(self, package_name: str) -> ToolResult:
        try:
            self.device.launch_app(package_name)
            return ToolResult(success=True, output=f"Launched {package_name}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
