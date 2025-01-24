#!/usr/bin/env python3

import argparse
import json
import os
import sys
import time
from typing import Optional, List, Dict, Any
import urllib.request
import urllib.error
import urllib.parse

class ReplitAPIClient:
    """Client for interacting with the Replit API"""

    BASE_URL = "https://repl.it/api/v0"
    AGENT_URL = "https://replit.com/api/v1/agent"

    def __init__(self, api_token: str):
        self.api_token = api_token

    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[dict] = None, base_url: Optional[str] = None) -> dict:
        """Make an HTTP request to the Replit API"""
        url = f"{base_url or self.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            request_data = None
            if data:
                request_data = json.dumps(data).encode('utf-8')

            request = urllib.request.Request(
                url,
                data=request_data,
                headers=headers,
                method=method
            )

            with urllib.request.urlopen(request) as response:
                return json.loads(response.read().decode('utf-8'))

        except urllib.error.HTTPError as e:
            error_message = e.read().decode('utf-8')
            print(f"Error {e.code}: {error_message}")
            sys.exit(1)
        except urllib.error.URLError as e:
            print(f"Failed to reach Replit API: {e.reason}")
            sys.exit(1)

    def create_repl(self, title: str, language: str, is_private: bool = False) -> dict:
        """Create a new Repl with the given parameters"""
        data = {
            "title": title,
            "language": language,
            "isPrivate": is_private
        }

        return self._make_request("repls", method="POST", data=data)

    def execute_agent_command(self, command: str, context: Optional[str] = None) -> dict:
        """Execute a single agent command"""
        data = {
            "command": command,
            "context": context or ""
        }

        return self._make_request("execute", method="POST", data=data, base_url=self.AGENT_URL)

    def execute_multiple_commands(self, commands: List[Dict[str, str]], wait_time: int = 2) -> List[dict]:
        """Execute multiple agent commands in sequence"""
        results = []
        for cmd in commands:
            result = self.execute_agent_command(cmd["command"], cmd.get("context"))
            results.append(result)
            # Wait between commands to avoid rate limiting
            if wait_time > 0:
                time.sleep(wait_time)
        return results

def get_api_token() -> str:
    """Get the Replit API token from environment variable or prompt user"""
    token = os.environ.get("REPLIT_API_TOKEN")
    if not token:
        print("REPLIT_API_TOKEN not found in environment variables.")
        token = input("Please enter your Replit API token: ").strip()
        if not token:
            print("Error: API token is required")
            sys.exit(1)
    return token

def main():
    parser = argparse.ArgumentParser(description="Create Repls and execute agent commands using the Replit API")
    parser.add_argument("--title", help="Title of the new Repl")
    parser.add_argument("--language", help="Programming language for the Repl")
    parser.add_argument("--private", action="store_true", help="Make the Repl private")
    parser.add_argument("--token", help="Replit API token (optional, can use REPLIT_API_TOKEN env var)")
    parser.add_argument("--agent-command", help="Single agent command to execute")
    parser.add_argument("--agent-context", help="Context for the agent command")
    parser.add_argument("--commands-file", help="JSON file containing multiple commands to execute")

    args = parser.parse_args()

    # Get API token from args or environment
    api_token = args.token or get_api_token()

    # Create API client
    client = ReplitAPIClient(api_token)

    try:
        # Execute agent command if specified
        if args.agent_command:
            print(f"Executing agent command: {args.agent_command}")
            result = client.execute_agent_command(args.agent_command, args.agent_context)
            print("\nCommand executed successfully!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return

        # Execute multiple commands from file if specified
        if args.commands_file:
            try:
                with open(args.commands_file, 'r') as f:
                    commands = json.load(f)
                print(f"Executing {len(commands)} commands from {args.commands_file}")
                results = client.execute_multiple_commands(commands)
                print("\nAll commands executed successfully!")
                print(f"Responses: {json.dumps(results, indent=2)}")
                return
            except FileNotFoundError:
                print(f"Error: Commands file {args.commands_file} not found")
                sys.exit(1)
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in commands file {args.commands_file}")
                sys.exit(1)

        # Create Repl if title and language are provided
        if args.title and args.language:
            print(f"Creating new Repl: {args.title}")
            result = client.create_repl(args.title, args.language, args.private)

            print("\nRepl created successfully!")
            print(f"Title: {result['title']}")
            print(f"Language: {result['language']}")
            print(f"URL: {result.get('url', 'Not available')}")
        else:
            parser.print_help()

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()