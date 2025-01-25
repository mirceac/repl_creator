# Repl Creator

A simple command-line tool to create local Repl configurations.

## Prerequisites

- Python 3.6 or higher
- A Replit account for remote operations

## Authentication

For remote operations (creating Repls on Replit.com), you need to authenticate:

1. Go to https://replit.com/account/api
   - Note: If you don't see an API section, make sure you're logged in
   - The API section might be under development or restricted
2. Copy your API token
3. Create a `.env` file in the project root (copy from `.env.example`)
4. Add your token: `REPLIT_TOKEN=your_token_here`

Note: You can also set the token as an environment variable directly.

## Usage

### Creating a Local Repl

```bash
python create_repl.py --title "My New Repl" --language python
```

The script will:
1. Create a configuration file in the `.repl-configs` directory
2. Generate a basic entry point file (e.g., main.py for Python)
3. Set up language-specific configurations

### Using Templates

You can create a Repl using predefined templates. For example, `sample_commands.json` provides a template for creating a Flask application with:
- Basic Flask app with "Hello World" endpoint
- Time display endpoint
- Error handling

To use a template:
```bash
python create_repl.py --title "My Flask App" --language python --template sample_commands.json
```

### Interactive Wizard

For a guided setup experience, use the wizard:
```bash
python create_repl.py --wizard
```

The wizard will:
1. Guide you through Repl configuration
2. Allow template selection
3. Set privacy and other options
4. Create the Repl based on your choices

### Command-line Arguments

- `--title`: Title of the new Repl (required)
- `--language`: Programming language for the Repl (required, choices: python, nodejs)
- `--private`: Make the Repl private (optional)
- `--template`: Specify a template file to use (optional)
- `--create-remote`: [Currently Limited] Attempt to create Repl on Replit.com (requires authentication)
- `--wizard`: Start the interactive configuration wizard

## Local Development

The tool supports local-only mode by default. This means you can:
1. Create and manage Repl configurations locally
2. Generate entry point files and basic templates
3. Test your Repls locally before deploying

## Output

The script creates:
1. A JSON configuration file in `.repl-configs/`
2. An entry point file in the current directory
3. Basic "Hello World" code in the entry point file

## Example

```bash
# Create a Python Repl locally
python create_repl.py --title "My Python App" --language python

# Create a Node.js Repl locally
python create_repl.py --title "My Node App" --language nodejs

# Create a Flask API using template
python create_repl.py --title "Flask API" --language python --template sample_commands.json

# Use the interactive wizard
python create_repl.py --wizard
```

## Directory Structure

```
your-project/
├── .repl-configs/
│   └── my_python_app.json
├── main.py (or index.js)
└── create_repl.py
```

For additional help, use the `--help` flag:
```bash
python create_repl.py --help