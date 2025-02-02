# curlpyconvert

A command-line tool to convert cURL commands into Python code for Grab, Context, or Dogman frameworks.

## Installation

- from pypi: `pip install curlpyconvert`
- from source: `rye sync && rye build && pip install -e .`

## Usage

### Command Line

`curl2py --help` shall guide you, tarnished

1. Copy your cURL command to clipboard
2. Default behaviour:

    - *pick framework: default - interactive prompt input via WordCompleter*

    ```bash
    curl2py convert
    ```

3. Flag options:

    - *-f/--framework flag*

    ```bash
    curl2py -f grab
    curl2py -f context
    curl2py -f dogman
    ```

    - *-v/--verbose flag: syntax highlighted code output in terminal prompt*

    ```bash
    curl2py -f grab -v
    ```

    - *-o/--output flag: save output code to autogenerated python script file in working directory*

    ```bash
    curl2py -f grab -o
    ```

4. The converted Python code will be automatically copied to your clipboard

### Command Aliases

The tool provides several convenient aliases:

- `curlpyconvert` - Main command
- `curl2py` - Quick convert command
- `c2py` - Shortest alias
- `curl2ctx` - Context framework specific
- `curl2grab` - Grab framework specific
- `curl2dog` - Dogman framework specific

### Example

Input (in clipboard):

```bash
curl 'https://api.example.com/data' \
-H 'accept: application/json' \
-H 'cookie: session=abc123' \
-H 'user-agent: Mozilla/5.0'
```

Output (for Grab framework):

```python
self.g.setup(common_headers={})  # remove this line if possible

self.g.setup(cookies={
    "session": "abc123"
})

self.g.setup(headers={
    "accept": "application/json # should not be necessary",
    "user-agent": "Mozilla/5.0 # should not be necessary"
})

self.g.go('https://api.example.com/data')
```

Output (for Context framework):

```python
self.context.headers.update({
    "accept": "application/json",
    "user-agent": "Mozilla/5.0"
})

self.context.cookies.update({
    "session": "abc123"
})

response = self.context.GET("https://api.example.com/data")
```

Output (for Dogman framework):

```python
dogman_config = {
    "setup": {}
}

self.context.setup(dogman_config=dogman_config)

self.context.dogman.get_cookies("https://api.example.com/data", spoofing="akamai")

self.context.headers.update({
    "accept": "application/json # should not be necessary",
    "user-agent": "Mozilla/5.0 # should not be necessary"
})

response = self.context.GET("https://api.example.com/data")
```

## Features

- Converts cURL commands to Python code
- Supports Grab, Context, and Dogman frameworks
- Extracts and formats:
    - Cookies
    - Headers
    - URL
    - POST data (if present)
- Uses clipboard for easy copy-paste workflow
- Interactive framework selection with autocompletion
- Rich terminal output with syntax highlighting
- Option to save output to file
- Multiple command aliases for convenience

## Requirements

- Python 3.10 or higher
- Dependencies (automatically installed):
    - pyperclip
    - typer
    - rich
    - six
    - prompt-toolkit
    - catppuccin[pygments]
    - pygments

## Development

1. Clone the repository:

    ```bash
    git clone https://gitlab.skypicker.com/tadeas.fort/curlpyconvert
    cd curlpyconvert
    ```

2. Install development dependencies:

    ```bash
    rye sync  # or: pip install -e ".[dev]"
    ```

3. Run tests:

    ```bash
    rye run pytest  # or: pytest
    ```

4. Build the package:

    ```bash
    rye build  # Creates dist/ directory with wheel and tar.gz
    ```

5. Publish to PyPI:

    ```bash
    rye publish  # Uploads to PyPI
    ```

## Testing

Run tests from project root:

```bash
rye run pytest  # If using Rye
pytest          # If installed in development mode with pip

# With coverage:
rye run pytest --cov=curlpyconvert

# Specific test file:
pytest src/curlpyconvert/test/test_curl_parser.py
```
