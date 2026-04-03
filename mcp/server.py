import asyncio
import os
import signal
import json
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types
from android.device import list_devices
from tools.recorder import ActionRecorder, replay_skill
from tools.teleport import TeleportTool
from android.manifest import get_deep_links

server = Server("agentdroid")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="list_devices",
            description="List connected Android devices",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="screenshot",
            description="Capture a screenshot from an Android device",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {"type": "string", "description": "Device serial number"},
                    "output_path": {"type": "string", "description": "Path to save screenshot", "default": "screenshot.png"},
                },
            },
        ),
        types.Tool(
            name="dump_ui",
            description="Dump UI hierarchy (XML) from an Android device",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {"type": "string", "description": "Device serial number"},
                    "output_path": {"type": "string", "description": "Path to save UI dump", "default": "ui_dump.xml"},
                },
            },
        ),
        types.Tool(
            name="tap",
            description="Tap at specific coordinates on the device",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {"type": "string", "description": "Device serial number"},
                    "x": {"type": "integer", "description": "X coordinate"},
                    "y": {"type": "integer", "description": "Y coordinate"},
                },
                "required": ["x", "y"],
            },
        ),
        types.Tool(
            name="record_skill",
            description="Start recording manual actions on the device to create a new skill.",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {"type": "string", "description": "Device serial number"},
                    "name": {"type": "string", "description": "Name of the skill to save"},
                    "duration": {"type": "integer", "description": "How long to record in seconds", "default": 10}
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="replay_skill",
            description="Replay a previously recorded skill",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {"type": "string", "description": "Device serial number"},
                    "name": {"type": "string", "description": "Name of the skill to replay"}
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="teleport",
            description="Jump to a specific screen using a deep link URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {"type": "string", "description": "Device serial number"},
                    "url": {"type": "string", "description": "Deep link URL"}
                },
                "required": ["url"],
            },
        ),
        types.Tool(
            name="discover_links",
            description="Discover deep links/intent filters for an app package",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {"type": "string", "description": "Device serial number"},
                    "package_name": {"type": "string"}
                },
                "required": ["package_name"],
            },
        ),
        types.Tool(
            name="launch_app",
            description="Launch an app by package name",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {"type": "string", "description": "Device serial number"},
                    "package_name": {"type": "string"},
                },
                "required": ["package_name"],
            },
        ),
        types.Tool(
            name="mirror_screen",
            description="Mirror the device screen using scrcpy",
            inputSchema={
                "type": "object",
                "properties": {"serial": {"type": "string"}},
            },
        ),
        types.Tool(
            name="inspect_layout",
            description="Enable or disable visual layout bounds (Show Layout Bounds) on the device",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {"type": "string", "description": "Device serial number"},
                    "enabled": {"type": "boolean", "description": "True to enable, False to disable"}
                },
                "required": ["enabled"],
            },
        ),
    ]

def get_target_device(serial: str = None):
    devices = list_devices()
    if not devices:
        raise ValueError("No Android devices found.")
    if serial:
        for d in devices:
            if d.serial == serial:
                return d
        raise ValueError(f"Device {serial} not found.")
    return devices[0]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls."""
    if not arguments:
        arguments = {}
        
    try:
        if name == "list_devices":
            devices = list_devices()
            return [types.TextContent(type="text", text=str(devices))]

        device = get_target_device(arguments.get("serial"))

        if name == "screenshot":
            path = arguments.get("output_path", "screenshot.png")
            device.screenshot(path)
            return [types.TextContent(type="text", text=f"Screenshot saved to {path}")]

        elif name == "dump_ui":
            path = arguments.get("output_path", "ui_dump.xml")
            device.dump_ui(path)
            with open(path, "r") as f:
                content = f.read()
            return [types.TextContent(type="text", text=content)]

        elif name == "record_skill":
            skill_name = arguments["name"]
            duration = arguments.get("duration", 10)
            recorder = ActionRecorder(device)
            def run_recording():
                recorder.start()
                import time
                time.sleep(duration)
                recorder.stop()
                recorder.save_skill(skill_name)
            import threading
            threading.Thread(target=run_recording).start()
            return [types.TextContent(type="text", text=f"Recording skill '{skill_name}' for {duration} seconds.")]

        elif name == "replay_skill":
            replay_skill(device, arguments["name"])
            return [types.TextContent(type="text", text=f"Replayed skill: {arguments['name']}")]

        elif name == "teleport":
            tool = TeleportTool(device)
            result = tool.execute(arguments["url"])
            return [types.TextContent(type="text", text=result.output)]

        elif name == "discover_links":
            links = get_deep_links(device.serial, arguments["package_name"])
            return [types.TextContent(type="text", text=f"Discovered links for {arguments['package_name']}:\n" + "\n".join(links))]

        elif name == "tap":
            device.tap(arguments["x"], arguments["y"])
            return [types.TextContent(type="text", text=f"Tapped at {arguments['x']}, {arguments['y']}")]

        elif name == "launch_app":
            device.launch_app(arguments["package_name"])
            return [types.TextContent(type="text", text=f"Launched {arguments['package_name']}")]

        elif name == "mirror_screen":
            device.mirror()
            return [types.TextContent(type="text", text=f"Mirroring started for {device.serial}")]

        elif name == "inspect_layout":
            enabled = arguments["enabled"]
            device.set_layout_inspector(enabled)
            status = "enabled" if enabled else "disabled"
            return [types.TextContent(type="text", text=f"Layout bounds {status} on {device.serial}")]

        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="agentdroid",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
