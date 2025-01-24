#!/usr/bin/env python3

import argparse
import json
import os
import sys
from typing import Dict, Any

class ReplCreator:
    """Creates local Repl configurations"""

    def __init__(self, config_dir: str = ".repl-configs"):
        self.config_dir = config_dir
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

    def create_repl(self, title: str, language: str, is_private: bool = False) -> Dict[str, Any]:
        """Create a new Repl configuration"""
        config = {
            "run": "",
            "language": language,
            "entrypoint": "",
            "onBoot": "",
            "packager": {
                "language": language,
                "ignoredPaths": [".git"]
            }
        }

        # Set language-specific configurations
        if language == "python":
            config["run"] = "python main.py"
            config["entrypoint"] = "main.py"
        elif language == "nodejs":
            config["run"] = "node index.js"
            config["entrypoint"] = "index.js"

        # Save configuration
        config_file = os.path.join(self.config_dir, f"{title.lower().replace(' ', '_')}.json")
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        print(f"\nRepl configuration created at: {config_file}")

        # Create the entry point file
        self._create_entry_point(config["entrypoint"])

        return config

    def _create_entry_point(self, entrypoint: str):
        """Create a basic entry point file"""
        if not os.path.exists(entrypoint):
            with open(entrypoint, "w") as f:
                if entrypoint.endswith(".py"):
                    f.write('print("Hello from your new Repl!")\n')
                elif entrypoint.endswith(".js"):
                    f.write('console.log("Hello from your new Repl!");\n')

def main():
    parser = argparse.ArgumentParser(description="Create local Repl configurations")
    parser.add_argument("--title", required=True, help="Title of the new Repl")
    parser.add_argument("--language", required=True, choices=["python", "nodejs"], 
                      help="Programming language for the Repl")
    parser.add_argument("--private", action="store_true", help="Make the Repl private")

    args = parser.parse_args()

    try:
        creator = ReplCreator()
        config = creator.create_repl(args.title, args.language, args.private)

        print("\nRepl created successfully!")
        print(f"Title: {args.title}")
        print(f"Language: {args.language}")
        print(f"Entry point: {config['entrypoint']}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()