# Replit Repl Creator

A command-line tool to create new Repls using your Replit account credentials.

## Prerequisites

- Python 3.6 or higher
- Replit account

## Usage

### Creating a Repl

```bash
python create_repl.py --title "My New Repl" --language python --private
```

When you run the script, it will prompt you for:
1. Your Replit username
2. Your Replit password (entered securely)

Alternatively, you can provide credentials via command-line arguments (not recommended for security):
```bash
python create_repl.py --title "My New Repl" --language python --private --username "your_username" --password "your_password"
```

## Command-line Arguments

- `--title`: Title of the new Repl
- `--language`: Programming language for the Repl
- `--private`: Make the Repl private (optional)
- `--username`: Your Replit username (optional, will prompt if not provided)
- `--password`: Your Replit password (optional and not recommended, will prompt if not provided)

## Security Note

- The script will prompt for your password securely without displaying it
- We recommend using the interactive prompt rather than command-line arguments for credentials
- Your credentials are only used to authenticate with Replit and are not stored

## Troubleshooting

If you encounter any issues:

1. Ensure your Replit credentials are correct
2. Check that you have the correct permissions for the operations you're trying to perform
3. Verify your internet connection
4. For any authentication issues, try logging in to Replit website first

For additional help, visit the Replit documentation or contact Replit support.