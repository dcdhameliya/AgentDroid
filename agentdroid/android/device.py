import subprocess
from pydantic import BaseModel
from typing import List

class ADBDevice(BaseModel):
    serial: str
    status: str

    def shell(self, command: str) -> str:
        """Run a shell command on the device."""
        cmd = ['adb', '-s', self.serial, 'shell'] + command.split()
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def screenshot(self, output_path: str = "screenshot.png"):
        """Capture a screenshot from the device."""
        # Using -p to force PNG format and redirecting stdout to file to avoid temp file on device
        with open(output_path, "wb") as f:
            subprocess.run(['adb', '-s', self.serial, 'exec-out', 'screencap', '-p'], stdout=f, check=True)

    def dump_ui(self, output_path: str = "ui_dump.xml"):
        """Dump UI hierarchy to a file."""
        # First dump to a temporary file on the device
        device_temp = "/sdcard/view.xml"
        self.shell(f"uiautomator dump {device_temp}")
        # Pull the file from the device
        subprocess.run(['adb', '-s', self.serial, 'pull', device_temp, output_path], check=True)
        # Clean up the device temporary file
        self.shell(f"rm {device_temp}")

    def tap(self, x: int, y: int):
        """Tap at specific coordinates."""
        self.shell(f"input tap {x} {y}")

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300):
        """Swipe from (x1, y1) to (x2, y2)."""
        self.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")

    def input_text(self, text: str):
        """Input text into the device."""
        # Escape spaces for the input command
        escaped_text = text.replace(" ", "%s")
        self.shell(f"input text {escaped_text}")

    def launch_app(self, package_name: str):
        """Launch an app by package name."""
        self.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")

    def get_logs(self, limit: int = 100) -> str:
        """Get the last N lines of logcat."""
        cmd = ['adb', '-s', self.serial, 'logcat', '-t', str(limit)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def clear_logs(self):
        """Clear logcat buffer."""
        subprocess.run(['adb', '-s', self.serial, 'logcat', '-c'], check=True)

    def mirror(self):
        """Mirror the device screen using scrcpy."""
        print(f"Launching scrcpy for {self.serial}...")
        try:
            # Run in the background so it doesn't block our CLI
            subprocess.Popen(['scrcpy', '-s', self.serial, '--window-title', f'AgentDroid Mirror: {self.serial}'])
        except FileNotFoundError:
            print("scrcpy not found. Please install it with 'brew install scrcpy'")

    def set_layout_inspector(self, enabled: bool):
        """Toggle the display of layout bounds (engineer mode)."""
        val = "true" if enabled else "false"
        self.shell(f"setprop debug.layout {val}")
        # Trigger a system-wide UI refresh to apply the property
        self.shell("service call activity 1599295538")

def list_devices() -> List[ADBDevice]:
    """List connected Android devices using adb."""
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        devices = []
        for line in lines[1:]: # skip the header "List of devices attached"
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 2:
                devices.append(ADBDevice(serial=parts[0], status=parts[1]))
        return devices
    except subprocess.CalledProcessError as e:
        print(f"Error running adb devices: {e}")
        return []
    except FileNotFoundError:
        print("adb command not found. Ensure Android SDK is installed and in your PATH.")
        return []
