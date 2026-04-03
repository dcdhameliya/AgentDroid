import subprocess
import re
import json
import time
from typing import List, Dict, Any

class ActionRecorder:
    def __init__(self, device):
        self.device = device
        self.recording = False
        self.actions = []

    def start(self):
        self.recording = True
        self.actions = []
        print("Recording started. Press Ctrl+C to stop.")
        
        # We use 'getevent -lt' which shows human-readable events
        # We'll parse this to detect taps and swipes
        cmd = ['adb', '-s', self.device.serial, 'shell', 'getevent', '-lt']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        try:
            current_tap = None
            last_event_time = 0
            
            for line in process.stdout:
                if not self.recording:
                    break
                
                # Sample output line:
                # [    1234.5678] /dev/input/event2: EV_ABS       ABS_MT_POSITION_X    000001a4
                match = re.search(r'\[\s*([\d.]+)\].*ABS_MT_POSITION_(X|Y)\s+([0-9a-f]+)', line)
                if match:
                    timestamp = float(match.group(1))
                    coord_type = match.group(2)
                    value = int(match.group(3), 16)
                    
                    if coord_type == 'X':
                        x = value
                        # Detect start of new interaction
                        if timestamp - last_event_time > 0.5:
                            print(f"Recorded movement at X: {x}")
                            self.actions.append({"type": "tap", "x": x, "y": 0, "time": timestamp})
                        else:
                            self.actions[-1]["x"] = x
                    else:
                        y = value
                        if self.actions:
                            self.actions[-1]["y"] = y
                    
                    last_event_time = timestamp

        except KeyboardInterrupt:
            self.stop()
        finally:
            process.terminate()

    def stop(self):
        self.recording = False
        print(f"Recording stopped. Captured {len(self.actions)} actions.")

    def save_skill(self, name: str):
        filename = f"skills/{name}.json"
        import os
        os.makedirs("skills", exist_ok=True)
        with open(filename, "w") as f:
            json.dump(self.actions, f, indent=2)
        print(f"Skill saved to {filename}")
        return filename

def replay_skill(device, skill_name: str):
    filename = f"skills/{skill_name}.json"
    if not os.path.exists(filename):
        print(f"Skill {skill_name} not found.")
        return
    
    with open(filename, "r") as f:
        actions = json.load(f)
    
    print(f"Replaying skill: {skill_name}")
    for action in actions:
        if action["type"] == "tap":
            print(f"Replaying tap: {action['x']}, {action['y']}")
            device.tap(action["x"], action["y"])
            time.sleep(1) # Wait for UI to react
