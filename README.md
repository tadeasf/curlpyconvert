# curlpyconvert

A command-line tool to convert cURL commands into Python code for Grab or Context frameworks.

## Installation

Install using pip:

```bash
pip install curlpyconvert
```

Or install from source:

```bash
git clone https://github.com/tadeasf/curlpyconvert.git
cd curlpyconvert
rye sync
```

## Usage

### Command Line

1. Copy your cURL command to clipboard
2. Run one of these commands:

    ```bash
    # Interactive mode - will ask you to choose framework
    curlpyconvert

    # Or specify framework directly
    curlpyconvert -f grab    # For Grab framework
    curlpyconvert -f context # For Context framework

    # Show output instead of copying to clipboard
    curlpyconvert -f grab -s
    ```

3. The converted Python code will be automatically copied to your clipboard (unless -s flag is used)

### Example

Input (in clipboard):

```bash
bash
curl 'https://api.example.com/data' \
-H 'accept: application/json' \
-H 'cookie: session=abc123' \
-H 'user-agent: Mozilla/5.0'
```

Output (for Grab framework):

```python
def method_name(self):
self.g.setup(cookies={
'session': 'abc123',
})
self.g.setup(headers={
'accept': 'application/json',
'user-agent': 'Mozilla/5.0',
})
# URL: https://api.example.com/data
```

Output (for Context framework):

```python
def method_name(self):
self.context.cookies.update({
'session': 'abc123',
})
self.context.headers.update({
'accept': 'application/json',
'user-agent': 'Mozilla/5.0',
})
# URL: https://api.example.com/data
```

## Features

- Converts cURL commands to Python code
- Supports both Grab and Context frameworks
- Extracts and formats:
    - Cookies
    - Headers
    - URL
    - POST data (if present)
- Uses clipboard for easy copy-paste workflow
- Interactive framework selection
- Rich terminal output with syntax highlighting

## Requirements

- Python 3.10 or higher
- Dependencies (automatically installed):
    - pyperclip
    - typer
    - rich
    - six

## Development

1. Clone the repository:

    ```bash
    git clone https://github.com/tadeasf/curlpyconvert.git
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

## License

GPL 3.0

## Author

tadeasf <business@tadeasfort.com>

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Issues

If you find any bugs or have feature requests, please create an issue on GitHub.

## Test

From project root:
rye run pytest  # If using Rye
pytest          # If installed in development mode with pip

- With coverage:

rye run pytest --cov=curlpyconvert

- Specific test file:
pytest src/curlpyconvert/test/test_curl_parser.py

- Build
rye build  # Creates dist/ directory with wheel and tar.gz

- Publish to PyPI
rye publish
