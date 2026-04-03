import click
import asyncio
from android.device import list_devices, ADBDevice
from providers.gemini import GeminiProvider
from providers.ollama import OllamaProvider
from providers.cli_provider import CLIProvider
from agent.runtime import AgentRuntime
from tools.android_tools import (
    TapTool, SwipeTool, InputTextTool, ScreenshotTool, UIDumpTool, LaunchAppTool
)
from agent.claw_agent import ClawAgent
from tools.recorder import ActionRecorder, replay_skill
from tools.teleport import TeleportTool
from tools.script_writer import generate_appium_script
from agent.self_healing import SelfHealingAgent

@click.group()
@click.option('--serial', help='Target a specific device by its serial number.')
@click.pass_context
def cli(ctx, serial):
    """AgentDroid: Android-first AI agent framework."""
    ctx.ensure_object(dict)
    ctx.obj['serial'] = serial

def get_device(serial: str = None) -> ADBDevice:
    """Get an ADBDevice instance for the specified serial or the default device."""
    devices = list_devices()
    if not devices:
        raise click.ClickException("No devices connected.")
    
    if serial:
        for d in devices:
            if d.serial == serial:
                return d
        raise click.ClickException(f"Device with serial '{serial}' not found.")
    
    # If no serial provided, use the first device
    return devices[0]

def get_provider(provider_name: str, model: str = None):
    """Initialize and return the appropriate provider."""
    provider_name = provider_name.lower()
    
    if provider_name == "gemini":
        try:
            return GeminiProvider(model_name=model or "gemini-2.0-flash")
        except ValueError as e:
            raise click.ClickException(f"Gemini initialization failed: {e}. Try using --provider ollama if you don't have an API key.")
    
    elif provider_name == "ollama":
        model = model or "llama3"
        click.echo(f"Using Ollama provider with model: {model}")
        return OllamaProvider(model_name=model)
    
    elif provider_name == "claude":
        click.echo("Using Claude CLI provider")
        return CLIProvider("claude", ["claude", "-p"])
    
    elif provider_name == "qwen":
        click.echo("Using Qwen CLI provider")
        return CLIProvider("qwen", ["qwen", "chat", "--prompt"])

    elif provider_name == "omx" or provider_name == "codex":
        click.echo("Using OMX (Oh-My-Codex) CLI provider")
        return CLIProvider("omx", ["omx", "chat"])

    elif provider_name == "omo" or provider_name == "opencode":
        click.echo("Using OMO (Oh-My-OpenAgent) CLI provider")
        return CLIProvider("omo", ["omo", "chat"])
    
    elif provider_name == "gemini-cli":
        click.echo("Using Gemini CLI provider")
        return CLIProvider("gemini-cli", ["gemini", "chat"])

    else:
        raise click.ClickException(f"Unknown provider: {provider_name}")

@cli.command()
def devices():
    """List connected Android devices."""
    devices = list_devices()
    if not devices:
        click.echo("No devices found.")
        return
    
    click.echo(f"{'Serial':<20} {'Status':<10}")
    click.echo("-" * 30)
    for device in devices:
        click.echo(f"{device.serial:<20} {device.status:<10}")

@cli.command()
@click.option('--output', default='screenshot.png', help='Output file path for the screenshot.')
@click.pass_context
def screenshot(ctx, output):
    """Capture a screenshot from the device."""
    device = get_device(ctx.obj.get('serial'))
    click.echo(f"Capturing screenshot for {device.serial}...")
    device.screenshot(output)
    click.echo(f"Screenshot saved to {output}")

@cli.command()
@click.option('--output', default='ui_dump.xml', help='Output file path for the UI dump.')
@click.pass_context
def dump_ui(ctx, output):
    """Dump the UI hierarchy of the current screen."""
    device = get_device(ctx.obj.get('serial'))
    click.echo(f"Dumping UI for {device.serial}...")
    device.dump_ui(output)
    click.echo(f"UI dump saved to {output}")

@cli.command()
@click.argument('x', type=int)
@click.argument('y', type=int)
@click.pass_context
def tap(ctx, x, y):
    """Tap at the specified (x, y) coordinates."""
    device = get_device(ctx.obj.get('serial'))
    click.echo(f"Tapping at ({x}, {y}) on {device.serial}...")
    device.tap(x, y)

@cli.command()
@click.argument('x1', type=int)
@click.argument('y1', type=int)
@click.argument('x2', type=int)
@click.argument('y2', type=int)
@click.option('--duration', default=300, type=int, help='Duration of the swipe in ms.')
@click.pass_context
def swipe(ctx, x1, y1, x2, y2, duration):
    """Swipe from (x1, y1) to (x2, y2)."""
    device = get_device(ctx.obj.get('serial'))
    click.echo(f"Swiping from ({x1}, {y1}) to ({x2}, {y2}) on {device.serial}...")
    device.swipe(x1, y1, x2, y2, duration)

@cli.command()
@click.argument('text')
@click.pass_context
def input(ctx, text):
    """Input text into the device."""
    device = get_device(ctx.obj.get('serial'))
    click.echo(f"Inputting text '{text}' on {device.serial}...")
    device.input_text(text)

@cli.command()
@click.argument('package_name')
@click.pass_context
def launch(ctx, package_name):
    """Launch an app by its package name."""
    device = get_device(ctx.obj.get('serial'))
    click.echo(f"Launching {package_name} on {device.serial}...")
    device.launch_app(package_name)

@cli.command()
@click.argument('task')
@click.option('--provider', default='gemini', help='Provider to use (gemini, ollama, claude, qwen, omx, omo, gemini-cli).')
@click.option('--local', is_flag=True, help='Shortcut for --provider ollama.')
@click.option('--model', help='Specify the model name to use.')
@click.option('--export', help='Export the successful task flow to an Appium script file.')
@click.pass_context
def run(ctx, task, provider, local, model, export):
    """Execute a natural language task on the device."""
    device = get_device(ctx.obj.get('serial'))
    if local:
        provider = "ollama"
        
    tools = [
        TapTool(device),
        SwipeTool(device),
        InputTextTool(device),
        ScreenshotTool(device),
        UIDumpTool(device),
        LaunchAppTool(device),
        TeleportTool(device)
    ]
    provider_inst = get_provider(provider, model)
    runtime = AgentRuntime(provider_inst, tools, device)
    
    click.echo(f"Starting task with {provider}...")
    result = runtime.run(task)
    click.echo(f"Result: {result}")

    if export and runtime.action_history:
        script = generate_appium_script(runtime.action_history)
        with open(export, "w") as f:
            f.write(script)
        click.echo(f"Flow exported to {export}")

@cli.command()
@click.argument('task')
@click.option('--provider', default='gemini', help='Provider to use (gemini, ollama, claude, qwen, omx, omo, gemini-cli).')
@click.option('--local', is_flag=True, help='Shortcut for --provider ollama.')
@click.option('--model', help='Specify the model name to use.')
@click.pass_context
def claw_run(ctx, task, provider, local, model):
    """Execute a natural language task on the device, integrated with Claw-Code."""
    device = get_device(ctx.obj.get('serial'))
    if local:
        provider = "ollama"
        
    provider_inst = get_provider(provider, model)
    agent = ClawAgent(device, provider=provider_inst)
    
    click.echo(f"Starting claw-integrated task with {provider}...")
    result = agent.execute(task)
    click.echo(f"Result: {result}")

@cli.command()
@click.pass_context
def mirror(ctx):
    """Mirror the device screen to your computer using scrcpy."""
    device = get_device(ctx.obj.get('serial'))
    device.mirror()

@cli.command()
@click.pass_context
def inspect(ctx):
    """Enable layout bounds and mirror screen for UI inspection."""
    device = get_device(ctx.obj.get('serial'))
    click.echo("Enabling layout bounds...")
    device.set_layout_inspector(True)
    device.mirror()
    click.prompt("\nLayout Inspector active. Press Enter to disable and exit", default="", show_default=False)
    click.echo("Disabling layout bounds...")
    device.set_layout_inspector(False)

@cli.command()
@click.argument('name')
@click.pass_context
def record(ctx, name):
    """Record a manual sequence of actions into a new skill."""
    device = get_device(ctx.obj.get('serial'))
    recorder = ActionRecorder(device)
    try:
        recorder.start()
    except KeyboardInterrupt:
        recorder.stop()
        recorder.save_skill(name)

@cli.command()
@click.argument('name')
@click.pass_context
def replay(ctx, name):
    """Replay a recorded skill."""
    device = get_device(ctx.obj.get('serial'))
    replay_skill(device, name)

@cli.command()
@click.argument('script_path')
@click.option('--provider', default='gemini')
@click.pass_context
def heal(ctx, script_path, provider):
    """Analyze and fix a broken test script."""
    device = get_device(ctx.obj.get('serial'))
    provider_inst = get_provider(provider)
    healer = SelfHealingAgent(provider_inst, device)
    click.echo(f"Attempting to heal script: {script_path}")
    fix = healer.heal(script_path)
    click.echo(f"\nProposed Fix:\n{fix}")

if __name__ == "__main__":
    cli()
