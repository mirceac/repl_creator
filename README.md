# Replit Repl Creator

A command-line tool to create new Repls and execute agent commands via the Replit API.

## Prerequisites

- Python 3.6 or higher
- Replit API token (see "Getting Your API Token" section below)

## Getting Your API Token

1. Log in to your Replit account
2. Go to https://replit.com/account#tokens
3. Click on "Generate new token"
4. Give your token a name (e.g., "Repl Creator")
5. Copy the token for use with this script

You can provide your API token in one of two ways:
1. Set it as an environment variable: `export REPLIT_API_TOKEN=your_token_here`
2. Pass it directly using the `--token` argument when running the script

## Usage

### Creating a Repl

```bash
python create_repl.py --title "My New Repl" --language python --private
```

### Executing a Single Agent Command

```bash
python create_repl.py --agent-command "Create a simple Flask application" --agent-context "python"
```

### Executing Multiple Commands

Create a JSON file with your commands (see `sample_commands.json` for example):

```bash
python create_repl.py --commands-file sample_commands.json
```

## Command-line Arguments

- `--title`: Title of the new Repl
- `--language`: Programming language for the Repl
- `--private`: Make the Repl private (optional)
- `--token`: Replit API token (optional, can use REPLIT_API_TOKEN env var)
- `--agent-command`: Single agent command to execute
- `--agent-context`: Context for the agent command
- `--commands-file`: JSON file containing multiple commands to execute

## Example Commands File

```json
[
  {
    "command": "Create a simple Flask application",
    "context": "python"
  },
  {
    "command": "Add a new route",
    "context": "Add to the Flask application"
  }
]
```

## Environment Variables

- `REPLIT_API_TOKEN`: Your Replit API token (can be set instead of using --token)

## Troubleshooting

If you encounter any issues:

1. Ensure your API token is valid and hasn't expired
2. Check that you have the correct permissions for the operations you're trying to perform
3. Verify your internet connection
4. For any authentication issues, generate a new token at https://replit.com/account#tokens

For additional help, visit the Replit documentation or contact Replit support.