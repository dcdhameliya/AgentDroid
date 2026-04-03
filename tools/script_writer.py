import json
from typing import List, Dict, Any

def generate_appium_script(actions: List[Dict[str, Any]], package_name: str = "com.example.app") -> str:
    """Converts a sequence of AgentDroid actions into a runnable Appium Python script."""
    
    header = f"""
import unittest
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
import time

class TestAgentDroidGenerated(unittest.TestCase):
    def setUp(self):
        options = UiAutomator2Options()
        options.platform_name = 'Android'
        options.automation_name = 'UiAutomator2'
        options.app_package = '{package_name}'
        options.no_reset = True
        
        self.driver = webdriver.Remote('http://localhost:4723', options=options)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_flow(self):
"""
    
    body = ""
    for action in actions:
        name = action.get("name")
        args = action.get("arguments", {})
        
        if name == "tap":
            body += f"        self.driver.tap([({args.get('x')}, {args.get('y')})])\n"
        elif name == "swipe":
            body += f"        self.driver.swipe({args.get('x1')}, {args.get('y1')}, {args.get('x2')}, {args.get('y2')}, {args.get('duration', 300)})\n"
        elif name == "input_text":
            body += f"        self.driver.press_keycode(66) # Enter to ensure focus if needed\n"
            body += f"        # Note: Generic input usually requires finding an element first.\n"
            body += f"        # For generated scripts, we use adb shell input as a fallback.\n"
            body += f"        self.driver.execute_script('mobile: shell', {{'command': 'input', 'args': ['text', '{args.get('text')}']}})\n"
        elif name == "launch_app":
            body += f"        self.driver.activate_app('{args.get('package_name')}')\n"
        
        body += "        time.sleep(1)\n"

    footer = """
if __name__ == '__main__':
    unittest.main()
"""
    return header + body + footer
