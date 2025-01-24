# Repl Creator

A simple command-line tool to create local Repl configurations.

## Prerequisites

- Python 3.6 or higher

## Usage

### Creating a Repl

```bash
python create_repl.py --title "My New Repl" --language python
```

The script will:
1. Create a configuration file in the `.repl-configs` directory
2. Generate a basic entry point file (e.g., main.py for Python)
3. Set up language-specific configurations

### Command-line Arguments

- `--title`: Title of the new Repl (required)
- `--language`: Programming language for the Repl (required, choices: python, nodejs)
- `--private`: Make the Repl private (optional)

## Output

The script creates:
1. A JSON configuration file in `.repl-configs/`
2. An entry point file in the current directory
3. Basic "Hello World" code in the entry point file

## Example

```bash
# Create a Python Repl
python create_repl.py --title "My Python App" --language python

# Create a Node.js Repl
python create_repl.py --title "My Node App" --language nodejs
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