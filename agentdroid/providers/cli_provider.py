import subprocess
import json
import re
from typing import List, Dict, Any, Optional
from agentdroid.providers.base import BaseProvider, Message, ProviderResponse, ToolCall

class CLIProvider(BaseProvider):
    """
    A provider that wraps external CLI tools (e.g., claude, gemini, qwen, omx, omo).
    It expects the CLI to take a prompt and return a response, ideally in a parsable format.
    """
    def __init__(self, cli_name: str, base_command: List[str]):
        self.cli_name = cli_name
        self.base_command = base_command

    def generate(self, messages: List[Message], tools: List[Dict[str, Any]]) -> ProviderResponse:
        # Construct the prompt for the CLI
        # We need to tell the CLI to return JSON if possible, or we'll have to parse its output.
        
        system_instructions = (
            "You are an AI assistant controlling an Android device. "
            "Available tools: " + json.dumps(tools) + "\n"
            "Respond ONLY with a JSON object in this format: "
            '{"message": "your reasoning", "tool_calls": [{"name": "tool_name", "arguments": {"arg1": "val1"}}]}'
        )
        
        # Combine messages into a single prompt for the CLI
        full_prompt = system_instructions + "\n\n"
        for msg in messages:
            full_prompt += f"{msg.role.upper()}: {msg.content}\n"
        
        # Execute the CLI command
        try:
            # Example: ["claude", "-p", full_prompt]
            cmd = self.base_command + [full_prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = result.stdout.strip()
            
            return self._parse_output(output)
        except subprocess.CalledProcessError as e:
            return ProviderResponse(message=f"CLI {self.cli_name} failed: {e.stderr or str(e)}")
        except Exception as e:
            return ProviderResponse(message=f"Error running {self.cli_name}: {str(e)}")

    def _parse_output(self, output: str) -> ProviderResponse:
        provider_response = ProviderResponse()
        
        # Try to find JSON in the output
        json_match = re.search(r'\{.*\}', output, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                provider_response.message = data.get("message")
                tool_calls_data = data.get("tool_calls", [])
                for tc in tool_calls_data:
                    provider_response.tool_calls.append(ToolCall(
                        name=tc.get("name"),
                        arguments=tc.get("arguments", {})
                    ))
                return provider_response
            except json.JSONDecodeError:
                pass
        
        # If no JSON found, treat the whole output as a message
        provider_response.message = output
        return provider_response
