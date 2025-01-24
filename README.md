# Replit Repl Creator

A command-line tool to create new Repls using the Replit GraphQL API.

## Prerequisites

- Python 3.6 or higher
- Replit API key

## Getting Your API Key

1. Log in to your Replit account
2. Visit https://replit.com/api-keys
3. Generate a new API key with the necessary permissions
4. Copy the key for use with this script

You can provide your API key in one of two ways:
1. Set it as an environment variable: `export REPLIT_CONNECT_TOKEN=your_api_key_here`
2. Pass it directly using the `--token` argument when running the script

## Usage

### Creating a Repl

```bash
python create_repl.py --title "My New Repl" --language python --private
```

When you run the script, it will:
1. Look for your API key in the environment variables
2. If not found, prompt you to enter your key
3. Create the Repl with the specified parameters

Alternatively, you can provide the token via command-line:
```bash
python create_repl.py --title "My New Repl" --language python --private --token "your_api_key"
```

## Command-line Arguments

- `--title`: Title of the new Repl
- `--language`: Programming language for the Repl
- `--private`: Make the Repl private (optional)
- `--token`: Replit API key (optional, can use REPLIT_CONNECT_TOKEN env var)

## Security Note

- Keep your API key secure and never share it publicly
- Use environment variables instead of command-line arguments for the token when possible
- Don't commit your token to version control

## Troubleshooting

If you encounter any issues:

1. Ensure your API key is valid and has the correct permissions
2. Check that you have the necessary permissions for the operations you're trying to perform
3. Verify your internet connection
4. For any authentication issues, try generating a new API key

For additional help, visit the Replit documentation or contact Replit support.