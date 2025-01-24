#!/usr/bin/env python3

import argparse
import json
import os
import sys
import requests
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    message: str
    path: Optional[str] = None

class ConfigValidator:
    """Validates configuration files and their contents"""

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> None:
        """Validate configuration structure and contents"""
        required_fields = ["default_language", "templates", "default_privacy"]

        for field in required_fields:
            if field not in config:
                raise ConfigurationError(f"Missing required field: {field}")

        if not isinstance(config["default_language"], str):
            raise ConfigurationError("default_language must be a string")

        if not isinstance(config["templates"], dict):
            raise ConfigurationError("templates must be a dictionary")

        if not isinstance(config["default_privacy"], bool):
            raise ConfigurationError("default_privacy must be a boolean")

class ReplConfig:
    """Handles configuration loading, validation, and merging"""

    def __init__(self, config_path: Union[str, Path]):
        self.config_path = Path(config_path)
        self.config = self.load()

    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                ConfigValidator.validate_config(config)
                return config
            return self.get_default_config()
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in config file: {e}", str(self.config_path))

    def save(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        try:
            ConfigValidator.validate_config(config)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            raise ConfigurationError(f"Failed to save config: {e}", str(self.config_path))

    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "default_language": "python",
            "templates": {},
            "team_id": None,
            "default_privacy": False,
            "create_remote": False,
            "config_version": "1.0.0",
            "last_updated": datetime.now().isoformat()
        }

class ReplitAPI:
    """Handles interactions with Replit's API"""

    BASE_URL = "https://replit.com/graphql"
    API_URL = "https://replit.com/api/v1"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get('REPLIT_TOKEN')
        self._is_remote_enabled = bool(self.token)

        if not self.token:
            print("\nRemote API Operations Status:")
            print("-----------------------------")
            print("× Remote features are currently disabled")
            print("× Running in local-only mode")
            print("\nAuthentication Update:")
            print("--------------------")
            print("Replit's API authentication system is being updated.")
            print("Currently, all operations will run in local-only mode.")
            print("We're actively working to support the latest authentication methods.")
            print("\nAvailable Features:")
            print("-----------------")
            print("✓ Local Repl configuration creation")
            print("✓ Template-based file generation")
            print("✓ Local development environment setup\n")

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "ReplCreator/1.0",
            "X-Requested-With": "XMLHttpRequest",
            "Connect-Src": "replit.com",
            "Authorization": f"Bearer {self.token}" if self.token else ""
        }

    @property
    def is_remote_enabled(self) -> bool:
        """Check if remote operations are enabled"""
        return self._is_remote_enabled

    def _handle_api_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and provide meaningful error messages"""
        try:
            if response.status_code == 200:
                json_response = response.json()
                if json_response is None:
                    raise ValueError("API returned null response")

                if 'errors' in json_response:
                    error_messages = [error.get('message', 'Unknown error') 
                                   for error in json_response['errors']]
                    raise ValueError(f"API errors: {'; '.join(error_messages)}")

                return json_response
            elif response.status_code == 401:
                raise ValueError(
                    "Authentication failed. Please ensure you're using a valid token. "
                    "Note: Replit's authentication system is being updated."
                )
            elif response.status_code == 403:
                raise ValueError(
                    "Access forbidden. Please check your token permissions. "
                    "You might need to request additional access rights."
                )
            elif response.status_code == 429:
                raise ValueError(
                    "Rate limit exceeded. Please wait before making more requests. "
                    "Consider implementing rate limiting in your application."
                )
            else:
                raise ValueError(
                    f"API request failed with status {response.status_code}. "
                    f"Response: {response.text}"
                )
        except requests.exceptions.JSONDecodeError:
            raise ValueError(
                f"Invalid JSON response from API. Status: {response.status_code}, "
                f"Content: {response.text[:200]}..."
            )

    def get_templates(self) -> List[Dict[str, Any]]:
        """Fetch available Repl templates"""
        if not self.is_remote_enabled:
            print("\nTemplate Operation Status:")
            print("------------------------")
            print("× Remote template fetching is unavailable")
            print("✓ Using local templates only")
            print("✓ Basic template generation available\n")
            return []

        query = """
        query TemplateSearch {
          templateSearch {
            items {
              id
              title
              description
              language
              tags
            }
          }
        }
        """
        response = self._graphql_request(query)
        if response and 'data' in response:
            return response['data'].get('templateSearch', {}).get('items', [])
        return []

    def create_remote_repl(self, title: str, language: str, is_private: bool = False,
                          template_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new Repl on Replit.com"""
        if not self.is_remote_enabled:
            print("\nRemote Creation Status:")
            print("---------------------")
            print("× Remote Repl creation is currently unavailable")
            print("✓ Creating local configuration only")
            print("✓ All local features are fully functional\n")
            raise ValueError("Remote Repl creation is temporarily unavailable while we update our API integration.")

        mutation = """
        mutation CreateRepl($input: CreateReplInput!) {
          createRepl(input: $input) {
            repl {
              id
              url
              title
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
                "isPrivate": is_private,
                "templateId": template_id
            }
        }

        response = self._graphql_request(mutation, variables)
        if response and 'data' in response:
            return response['data'].get('createRepl', {}).get('repl', {})
        raise Exception("Failed to create remote Repl")

    def _graphql_request(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GraphQL request to Replit API with improved error handling"""
        payload: Dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            response = requests.post(
                self.BASE_URL, 
                headers=self.headers, 
                json=payload,
                timeout=30  # Add timeout to prevent hanging
            )
            return self._handle_api_response(response)
        except requests.exceptions.ConnectionError:
            raise ValueError(
                "Failed to connect to Replit API. Please check your internet connection "
                "and ensure api.replit.com is accessible."
            )
        except requests.exceptions.Timeout:
            raise ValueError(
                "Request to Replit API timed out. Please try again later or check "
                "your network connection."
            )
        except requests.exceptions.RequestException as e:
            raise ValueError(f"API request failed: {str(e)}")


class ReplWizard:
    """Interactive wizard for Repl configuration"""

    def __init__(self, config_manager: ReplConfig):
        self.config_manager = config_manager
        self.config = config_manager.load()

    def start_wizard(self) -> Dict[str, Any]:
        """Start the interactive configuration wizard"""
        try:
            print("\nWelcome to the Repl Configuration Wizard!")
            print("Please answer the following questions to configure your Repl.\n")

            title = self._prompt_string("Enter Repl title", required=True, default="MyRepl")
            if not title:
                raise ConfigurationError("Title is required for Repl creation")

            language = self._prompt_choice(
                "Select programming language",
                choices=["python", "nodejs"],
                default="python"
            )
            if not language:
                language = "python"  # Fallback to default

            is_private = self._prompt_boolean("Make Repl private?", default=self.config.get("default_privacy", False))

            # Template selection
            templates = self.config.get("templates", {})
            template_file = None
            if templates:
                print("\nAvailable templates:")
                for name, details in templates.items():
                    print(f"- {name}: {details.get('description', 'No description')}")
                template_name = self._prompt_string("Enter template name (or leave empty to skip)", required=False)
                if template_name:
                    template_file = templates.get(template_name, {}).get("path")

            create_remote = self._prompt_boolean(
                "Create Repl on Replit.com? (requires API token)",
                default=self.config.get("create_remote", False)
            )

            return {
                "title": title,
                "language": language,
                "is_private": is_private,
                "template": template_file,
                "create_remote": create_remote
            }
        except (EOFError, KeyboardInterrupt):
            print("\nWizard cancelled. Using default values.")
            return {
                "title": "MyRepl",
                "language": "python",
                "is_private": self.config.get("default_privacy", False),
                "template": None,
                "create_remote": self.config.get("create_remote", False)
            }
        except Exception as e:
            print(f"\nAn error occurred in the wizard: {str(e)}")
            raise

    def _prompt_string(self, prompt: str, required: bool = False, default: Optional[str] = None) -> str:
        """Prompt for string input with error handling for non-interactive environments"""
        try:
            while True:
                value = input(f"{prompt}{' (required)' if required else ''}"
                             f"{f' [default: {default}]' if default else ''}: ").strip()

                if not value:
                    if default is not None:
                        return default
                    if not required:
                        return ""
                    print("This field is required. Please enter a value.")
                    continue
                return value
        except (EOFError, KeyboardInterrupt):
            if default is not None:
                return default
            raise

    def _prompt_boolean(self, prompt: str, default: bool = False) -> bool:
        """Prompt for boolean input with error handling for non-interactive environments"""
        try:
            while True:
                response = input(f"{prompt} (y/n) [{('y' if default else 'n')}]: ").strip().lower()
                if not response:
                    return default
                if response in ('y', 'yes'):
                    return True
                if response in ('n', 'no'):
                    return False
                print("Please enter 'y' or 'n'")
        except (EOFError, KeyboardInterrupt):
            return default

    def _prompt_choice(self, prompt: str, choices: List[str], default: Optional[str] = None) -> str:
        """Prompt for choice from list with error handling for non-interactive environments"""
        if not choices:
            raise ValueError("No choices provided")

        if default is not None and default not in choices:
            default = choices[0]

        try:
            while True:
                print(f"\n{prompt}:")
                for i, choice in enumerate(choices, 1):
                    print(f"{i}. {choice}{' (default)' if choice == default else ''}")

                response = input(f"Enter number [1-{len(choices)}]"
                               f"{f' [{choices.index(default) + 1}]' if default else ''}: ").strip()

                if not response and default is not None:
                    return default

                try:
                    index = int(response) - 1
                    if 0 <= index < len(choices):
                        return choices[index]
                except ValueError:
                    pass

                print(f"Please enter a number between 1 and {len(choices)}")
        except (EOFError, KeyboardInterrupt):
            if default is not None:
                return default
            return choices[0]

class ReplCreator:
    """Creates and manages Repls both locally and on Replit.com"""

    def __init__(self, config_dir: str = ".repl-configs", 
                 config_file: str = "repl_creator_config.json",
                 custom_config_path: Optional[str] = None):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / config_file if not custom_config_path else Path(custom_config_path)
        self.api = ReplitAPI()

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)

        # Initialize configuration
        self.config_manager = ReplConfig(self.config_file)
        self.config = self.config_manager.load()

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration using the config manager"""
        self.config_manager.save(config)
        self.config = config

    def load_config(self) -> Dict[str, Any]:
        """Load configuration using the config manager"""
        return self.config_manager.load()

    def create_repl(self, title: str, language: str, is_private: bool = False, 
                   template_file: Optional[str] = None, team_id: Optional[str] = None,
                   create_remote: Optional[bool] = None) -> Dict[str, Any]:
        """Create a new Repl configuration and optionally on Replit.com"""
        if create_remote is None:
            create_remote = False

        if create_remote:
            if not self.api.is_remote_enabled:
                print("Warning: Remote creation requested but API token not available.")
                print("To enable remote creation, please set your REPLIT_TOKEN environment variable.")
                print("You can get your token from https://replit.com/account#api")
                print("Creating local configuration only.")
                create_remote = False
            else:
                print("Attempting remote Repl creation...")

        # Create local configuration
        config = {
            "run": "",
            "language": language,
            "entrypoint": "",
            "onBoot": "",
            "packager": {
                "language": language,
                "ignoredPaths": [".git"]
            },
            "template": template_file,
            "team_id": team_id or self.config.get("team_id"),
            "is_private": is_private
        }

        # Set language-specific configurations
        if language == "python":
            config["run"] = "python main.py"
            config["entrypoint"] = "main.py"
        elif language == "nodejs":
            config["run"] = "node index.js"
            config["entrypoint"] = "index.js"

        # Save local configuration
        config_file = os.path.join(self.config_dir, f"{title.lower().replace(' ', '_')}.json")
        try:
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
            print(f"\nRepl configuration created at: {config_file}")
        except IOError as e:
            print(f"Error saving local configuration: {str(e)}")
            raise ConfigurationError(f"Failed to save configuration: {str(e)}", config_file)

        # Create entry point file
        if template_file:
            self._create_from_template(config["entrypoint"], template_file)
        else:
            self._create_entry_point(config["entrypoint"])

        # Try remote creation only if explicitly requested and available
        create_remote = create_remote if create_remote is not None else self.config.get("create_remote", False)
        if create_remote and self.api.is_remote_enabled:
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    remote_config = self.api.create_remote_repl(
                        title=title,
                        language=language,
                        is_private=is_private
                    )
                    config["remote"] = remote_config
                    # Update the config file with remote information
                    with open(config_file, "w") as f:
                        json.dump(config, f, indent=2)
                    print("\nRemote Repl created successfully!")
                    print(f"Remote URL: {remote_config['url']}")
                    break
                except requests.exceptions.RequestException as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"Network error occurred, retrying... (Attempt {retry_count + 1}/{max_retries})")
                    else:
                        print(f"Warning: Failed to create remote Repl after {max_retries} attempts: {str(e)}")
                        print("Network error: Please check your internet connection.")
                        print("Local configuration was created successfully.")
                except Exception as e:
                    print(f"Warning: Failed to create remote Repl: {str(e)}")
                    print("Local configuration was created successfully.")
                    break

        return config

    def bulk_create_repls(self, config_file: str) -> List[Dict[str, Any]]:
        """Create multiple Repls from a configuration file"""
        with open(config_file, 'r') as f:
            configs = json.load(f)

        results = []
        for repl_config in configs:
            try:
                config = self.create_repl(
                    title=repl_config["title"],
                    language=repl_config.get("language", self.config["default_language"]),
                    is_private=repl_config.get("is_private", self.config["default_privacy"]),
                    template_file=repl_config.get("template"),
                    team_id=repl_config.get("team_id"),
                    create_remote=repl_config.get("create_remote")
                )
                results.append({"title": repl_config["title"], "status": "success", "config": config})
            except Exception as e:
                results.append({"title": repl_config["title"], "status": "error", "error": str(e)})

        return results

    def _create_entry_point(self, entrypoint: str):
        """Create a basic entry point file"""
        if not os.path.exists(entrypoint):
            with open(entrypoint, "w") as f:
                if entrypoint.endswith(".py"):
                    f.write('print("Hello from your new Repl!")\n')
                elif entrypoint.endswith(".js"):
                    f.write('console.log("Hello from your new Repl!");\n')

    def _create_from_template(self, entrypoint: str, template_file: str):
        """Create entry point file from template commands"""
        try:
            with open(template_file, 'r') as f:
                commands = json.load(f)

            if entrypoint.endswith('.py'):
                content = []
                for cmd in commands:
                    if cmd["context"].lower() == "python" or "flask" in cmd["context"].lower():
                        if "Flask application" in cmd["command"]:
                            content.extend([
                                "from flask import Flask",
                                "app = Flask(__name__)",
                                "",
                                "@app.route('/')",
                                "def hello_world():",
                                "    return 'Hello World'",
                                ""
                            ])
                        elif "current time" in cmd["command"].lower():
                            content.extend([
                                "from datetime import datetime",
                                "",
                                "@app.route('/time')",
                                "def get_time():",
                                "    return {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                ""
                            ])
                        elif "error handling" in cmd["command"].lower():
                            content.extend([
                                "@app.errorhandler(404)",
                                "def not_found(error):",
                                "    return {'error': 'Not found'}, 404",
                                "",
                                "if __name__ == '__main__':",
                                "    app.run(host='0.0.0.0', port=5000, debug=True)",
                                ""
                            ])

                with open(entrypoint, 'w') as f:
                    f.write('\n'.join(content))

        except Exception as e:
            print(f"Error creating from template: {str(e)}")
            self._create_entry_point(entrypoint)

    def create_from_wizard(self) -> Dict[str, Any]:
        """Create a new Repl using the interactive wizard"""
        wizard = ReplWizard(self.config_manager)
        config = wizard.start_wizard()

        return self.create_repl(
            title=config["title"],
            language=config["language"],
            is_private=config["is_private"],
            template_file=config["template"],
            create_remote=config["create_remote"]
        )

    def create_from_local_config(self, config_file_path: str) -> Dict[str, Any]:
        """Create a Repl from a local configuration file"""
        try:
            with open(config_file_path, 'r') as f:
                local_config = json.load(f)

            # Validate required fields
            required_fields = ["language", "entrypoint", "run"]
            missing_fields = [field for field in required_fields if field not in local_config]
            if missing_fields:
                raise ConfigurationError(f"Missing required fields in config: {', '.join(missing_fields)}")

            # Create Repl using local configuration
            return self.create_repl(
                title=os.path.splitext(os.path.basename(config_file_path))[0].replace('_', ' ').title(),
                language=local_config["language"],
                is_private=local_config.get("is_private", self.config.get("default_privacy", False)),
                template_file=local_config.get("template"),
                team_id=local_config.get("team_id"),
                create_remote=local_config.get("create_remote", False)
            )
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in config file: {str(e)}", config_file_path)
        except IOError as e:
            raise ConfigurationError(f"Error reading config file: {str(e)}", config_file_path)

    def list_local_configs(self) -> List[Dict[str, Any]]:
        """List all available local Repl configurations"""
        configs = []
        try:
            for file_path in self.config_dir.glob('*.json'):
                try:
                    with open(file_path, 'r') as f:
                        config = json.load(f)
                    configs.append({
                        'name': file_path.stem,
                        'path': str(file_path),
                        'language': config.get('language', 'unknown'),
                        'is_private': config.get('is_private', False),
                        'template': config.get('template')
                    })
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Warning: Could not read config file {file_path}: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error listing configurations: {str(e)}")
        return configs

def main():
    parser = argparse.ArgumentParser(description="Create and manage Repls locally and on Replit.com")
    parser.add_argument("--wizard", action="store_true", help="Start interactive configuration wizard")
    parser.add_argument("--title", help="Title of the new Repl")
    parser.add_argument("--language", choices=["python", "nodejs"], 
                      help="Programming language for the Repl")
    parser.add_argument("--private", action="store_true", help="Make the Repl private")
    parser.add_argument("--template", help="Path to template commands file")
    parser.add_argument("--bulk-config", help="Path to bulk creation configuration file")
    parser.add_argument("--team-id", help="Team ID for creating team Repls")
    parser.add_argument("--create-remote", action="store_true", help="Create Repl on Replit.com")
    parser.add_argument("--config-path", help="Path to custom config file")
    parser.add_argument("--from-config", help="Create Repl from local configuration file")
    parser.add_argument("--list-configs", action="store_true", help="List available local configurations")

    args = parser.parse_args()

    try:
        creator = ReplCreator(custom_config_path=args.config_path)

        if args.list_configs:
            configs = creator.list_local_configs()
            print("\nAvailable local configurations:")
            print("-----------------------------")
            for config in configs:
                print(f"Name: {config['name']}")
                print(f"Language: {config['language']}")
                print(f"Private: {config['is_private']}")
                if config['template']:
                    print(f"Template: {config['template']}")
                print("-----------------------------")
        elif args.from_config:
            config = creator.create_from_local_config(args.from_config)
            print("\nRepl created from local configuration!")
            print(f"Title: {config['title']}")
            print(f"Language: {config['language']}")
            print(f"Entry point: {config['entrypoint']}")
            if "remote" in config:
                print(f"Remote URL: {config['remote']['url']}")
        elif args.wizard:
            config = creator.create_from_wizard()
            print("\nRepl created successfully through wizard!")
            print(f"Title: {config['title']}")
            print(f"Language: {config['language']}")
            print(f"Entry point: {config['entrypoint']}")
            if "remote" in config:
                print(f"Remote URL: {config['remote']['url']}")
        elif args.bulk_config:
            results = creator.bulk_create_repls(args.bulk_config)
            print("\nBulk creation results:")
            for result in results:
                status = "✓" if result["status"] == "success" else "✗"
                print(f"{status} {result['title']}")
                if result["status"] == "error":
                    print(f"  Error: {result['error']}")
        elif args.title:
            config = creator.create_repl(
                args.title, 
                args.language, 
                args.private, 
                args.template,
                args.team_id,
                args.create_remote
            )

            print("\nRepl created successfully!")
            print(f"Title: {args.title}")
            print(f"Language: {args.language}")
            print(f"Entry point: {config['entrypoint']}")
            if "remote" in config:
                print(f"Remote URL: {config['remote']['url']}")
        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()