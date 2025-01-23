#!/usr/bin/env python3

import argparse
import json
import os
import sys
from typing import Optional
import urllib.request
import urllib.error
import urllib.parse

class ReplitAPIClient:
    """Client for interacting with the Replit API"""
    
    BASE_URL = "https://repl.it/api/v0"
    
    def __init__(self, api_token: str):
        self.api_token = api_token
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[dict] = None) -> dict:
        """Make an HTTP request to the Replit API"""
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            if data:
                data = json.dumps(data).encode('utf-8')
            
            request = urllib.request.Request(
                url,
                data=data,
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
    parser = argparse.ArgumentParser(description="Create a new Repl using the Replit API")
    parser.add_argument("--title", required=True, help="Title of the new Repl")
    parser.add_argument("--language", required=True, help="Programming language for the Repl")
    parser.add_argument("--private", action="store_true", help="Make the Repl private")
    parser.add_argument("--token", help="Replit API token (optional, can use REPLIT_API_TOKEN env var)")
    
    args = parser.parse_args()
    
    # Get API token from args or environment
    api_token = args.token or get_api_token()
    
    # Create API client
    client = ReplitAPIClient(api_token)
    
    try:
        print(f"Creating new Repl: {args.title}")
        result = client.create_repl(args.title, args.language, args.private)
        
        print("\nRepl created successfully!")
        print(f"Title: {result['title']}")
        print(f"Language: {result['language']}")
        print(f"URL: {result.get('url', 'Not available')}")
        
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
