#!/usr/bin/env python3

import argparse
import json
import os
import sys
import time
import getpass
from typing import Optional, List, Dict, Any
import urllib.request
import urllib.error
import urllib.parse

class ReplitAPIClient:
    """Client for interacting with the Replit API"""

    BASE_URL = "https://replit.com/api"
    SESSION_URL = f"{BASE_URL}/v0/auth/login"

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session_token = self._get_session_token()

    def _get_session_token(self) -> str:
        """Authenticate with Replit and get a session token"""
        data = {
            "username": self.username,
            "password": self.password
        }

        try:
            request_data = json.dumps(data).encode('utf-8')
            request = urllib.request.Request(
                self.SESSION_URL,
                data=request_data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(request) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('sessionToken')

        except urllib.error.HTTPError as e:
            error_message = e.read().decode('utf-8')
            print(f"Authentication failed: {error_message}")
            sys.exit(1)
        except urllib.error.URLError as e:
            print(f"Failed to reach Replit: {e.reason}")
            sys.exit(1)

    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[dict] = None) -> dict:
        """Make an HTTP request to the Replit API"""
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "X-Replit-Session-Token": self.session_token,
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

        return self._make_request("v0/repls", method="POST", data=data)

def get_credentials() -> tuple:
    """Get Replit username and password"""
    username = input("Enter your Replit username: ").strip()
    if not username:
        print("Error: Username is required")
        sys.exit(1)

    password = getpass.getpass("Enter your Replit password: ").strip()
    if not password:
        print("Error: Password is required")
        sys.exit(1)

    return username, password

def main():
    parser = argparse.ArgumentParser(description="Create Repls using your Replit account")
    parser.add_argument("--title", help="Title of the new Repl")
    parser.add_argument("--language", help="Programming language for the Repl")
    parser.add_argument("--private", action="store_true", help="Make the Repl private")
    parser.add_argument("--username", help="Your Replit username")
    parser.add_argument("--password", help="Your Replit password (not recommended, use prompt instead)")

    args = parser.parse_args()

    # Get credentials
    username = args.username
    password = args.password

    if not (username and password):
        username, password = get_credentials()

    # Create API client
    client = ReplitAPIClient(username, password)

    try:
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