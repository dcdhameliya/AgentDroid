import re
import subprocess
from typing import List

def get_deep_links(device_serial: str, package_name: str) -> List[str]:
    """Scans the app's manifest via dumpsys to discover intent-filter deep links."""
    try:
        cmd = ['adb', '-s', device_serial, 'shell', 'dumpsys', 'package', package_name]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout
        
        # Look for android.intent.action.VIEW with data schemes
        # This is a heuristic parser for dumpsys output
        links = []
        
        # Find sections containing 'action.VIEW'
        view_sections = re.split(r'action\.VIEW', output)
        for section in view_sections[1:]:
            # Extract schemes and hosts from the filter
            schemes = re.findall(r'scheme="([^"]+)"', section)
            hosts = re.findall(r'host="([^"]+)"', section)
            paths = re.findall(r'path="([^"]+)"', section)
            
            for scheme in schemes:
                if hosts:
                    for host in hosts:
                        path = paths[0] if paths else ""
                        links.append(f"{scheme}://{host}{path}")
                else:
                    links.append(f"{scheme}://")
                    
        return list(set(links)) # Unique links
    except Exception as e:
        print(f"Error scanning for deep links: {e}")
        return []
