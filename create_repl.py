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

    BASE_URL = "https://replit.com/graphql"

    def __init__(self, connect_token: str):
        self.connect_token = connect_token

    def _make_request(self, query: str, variables: Optional[dict] = None) -> dict:
        """Make a GraphQL request to the Replit API"""
        headers = {
            "Authorization": f"Bearer {self.connect_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Requested-With": "replit"
        }

        data = {
            "query": query,
            "variables": variables or {}
        }

        try:
            request_data = json.dumps(data).encode('utf-8')
            request = urllib.request.Request(
                self.BASE_URL,
                data=request_data,
                headers=headers,
                method="POST"
            )

            with urllib.request.urlopen(request) as response:
                return json.loads(response.read().decode('utf-8'))

        except urllib.error.HTTPError as e:
            error_message = e.read().decode('utf-8')
            print(f"API Error {e.code}: {error_message}")
            sys.exit(1)
        except urllib.error.URLError as e:
            print(f"Failed to reach Replit API: {e.reason}")
            sys.exit(1)

    def create_repl(self, title: str, language: str, is_private: bool = False) -> dict:
        """Create a new Repl using GraphQL mutation"""
        query = """
        mutation CreateRepl($input: CreateReplInput!) {
          createRepl(input: $input) {
            repl {
              id
              title
              url
              language
              isPrivate
            }
          }
        }
        """

        variables = {
            "input": {
                "title": title,
                "language": language,
                "isPrivate": is_private
            }
        }

        result = self._make_request(query, variables)
        if "errors" in result:
            print("Failed to create Repl:")
            for error in result["errors"]:
                print(f"- {error.get('message', 'Unknown error')}")
            sys.exit(1)

        return result.get("data", {}).get("createRepl", {}).get("repl", {})

def get_connect_token() -> str:
    """Get Replit Connect token from environment or prompt"""
    token = os.environ.get("REPLIT_CONNECT_TOKEN")
    if not token:
        print("REPLIT_CONNECT_TOKEN not found in environment variables.")
        print("Please visit https://replit.com/api-keys to generate an API key.")
        token = input("Enter your Replit API key: ").strip()
        if not token:
            print("Error: API key is required")
            sys.exit(1)
    return token

def main():
    parser = argparse.ArgumentParser(description="Create Repls using your Replit account")
    parser.add_argument("--title", help="Title of the new Repl")
    parser.add_argument("--language", help="Programming language for the Repl")
    parser.add_argument("--private", action="store_true", help="Make the Repl private")
    parser.add_argument("--token", help="Replit API key (optional, can use REPLIT_CONNECT_TOKEN env var)")

    args = parser.parse_args()

    # Get Connect token
    connect_token = args.token or get_connect_token()

    # Create API client
    client = ReplitAPIClient(connect_token)

    try:
        # Create Repl if title and language are provided
        if args.title and args.language:
            print(f"Creating new Repl: {args.title}")
            result = client.create_repl(args.title, args.language, args.private)

            print("\nRepl created successfully!")
            print(f"Title: {result.get('title')}")
            print(f"Language: {result.get('language')}")
            print(f"URL: {result.get('url')}")
        else:
            parser.print_help()

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()