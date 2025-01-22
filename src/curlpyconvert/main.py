import typer
import pyperclip
from rich import print
from rich.panel import Panel
from rich.syntax import Syntax
from rich.traceback import install
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from typing import Optional
from enum import Enum
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from catppuccin.extras.pygments import MochaStyle
import importlib.metadata
import time
import re
from pathlib import Path
from urllib.parse import urlparse

# Install rich traceback handler
install(show_locals=True)

from .lib.curl_parser import CurlParser
from .lib.grab import GrabCodeWriter
from .lib.context import ContextCodeWriter
from .lib.dogman import DogmanCodeWriter

app = typer.Typer(
    help="""Convert cURL commands to Python code for Grab/Context frameworks

Available command aliases:
    curlpyconvert  - Main command
    curl2py        - Quick convert command
    c2py          - Shortest alias
    curl2ctx      - Context framework specific
    curl2grab     - Grab framework specific
    curl2dog      - Dogman framework specific""",
    add_completion=True,
    no_args_is_help=False
)

def get_version():
    """Get package version from pyproject.toml."""
    try:
        return importlib.metadata.version("curlpyconvert")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"

class Framework(str, Enum):
    GRAB = "grab"
    CONTEXT = "context"
    DOGMAN = "dogman"

def get_framework(test_mode=False) -> Framework:
    """Interactive framework selection with autocomplete and syntax highlighting."""
    if test_mode:
        return Framework.GRAB  # Default for testing
        
    frameworks = [f.value for f in Framework]
    style = Style.from_dict({
        'completion-menu.completion': 'bg:#1e1e2e #cdd6f4',
        'completion-menu.completion.current': 'bg:#313244 #cdd6f4',
        'completion-menu.meta.completion': 'bg:#1e1e2e #cdd6f4',
        'completion-menu.meta.completion.current': 'bg:#313244 #cdd6f4',
        'completion.grab': 'bg:#1e1e2e #89b4fa',  # Catppuccin Blue
        'completion.context': 'bg:#1e1e2e #f9e2af',  # Catppuccin Yellow
        'completion.dogman': 'bg:#1e1e2e #f5c2e7',  # Catppuccin Pink
    })
    
    completer = WordCompleter(frameworks, meta_dict={
        'grab': 'Grab framework (Python)',
        'context': 'Context framework (Python)',
        'dogman': 'Dogman framework (Python)'
    })
    
    framework = prompt(
        'Select framework (grab/context/dogman): ',
        completer=completer,
        style=style
    )
    
    return Framework(framework.lower())

def display_code(code: str, language: str = "python"):
    """Display code with syntax highlighting using Catppuccin theme."""
    syntax = Syntax(
        code,
        language,
        theme=MochaStyle,
        line_numbers=True,
        word_wrap=True,
    )
    panel = Panel(
        syntax,
        expand=False,
        border_style="#89dceb",  # Catppuccin Sky
        title=f"Generated {language.capitalize()} Code",
        title_align="left",
    )
    print(panel)

def get_curl_command(test_mode=False) -> str:
    """Get curl command from clipboard and confirm."""
    curl_command = pyperclip.paste().strip()
    
    if not curl_command:
        raise ValueError("No curl command in clipboard")
        
    # Clean up the curl command
    curl_command = curl_command.replace('\\\n', ' ').replace('\\', '')
    
    if test_mode:
        return curl_command
        
    print("Copy curl command to clipboard and press Enter...")
    input()  # Wait for user confirmation
    return pyperclip.paste().strip()

def form_code(parsed_curl: dict, framework: Framework) -> str:
    """Generate framework-specific code from parsed curl command."""
    if framework == Framework.GRAB:
        writer = GrabCodeWriter(parsed_curl)
    elif framework == Framework.DOGMAN:
        writer = DogmanCodeWriter(parsed_curl)
    else:
        writer = ContextCodeWriter(parsed_curl)
    
    return writer.generate_code()

def version_callback(value: bool):
    """Callback for --version flag."""
    if value:
        version = get_version()
        print(f"curl-to-context version: {version}")
        raise typer.Exit()

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        help="Show the application's version and exit.",
        callback=version_callback,
        is_eager=True,
    )
):
    """Convert cURL commands to Python code for Grab/Context frameworks."""
    if ctx.invoked_subcommand is None:
        # If no subcommand provided, run convert without args
        ctx.invoke(convert)

def sanitize_filename(url: str) -> str:
    """Generate a safe filename from URL."""
    # Parse the URL
    parsed = urlparse(url)
    
    # Get the domain without www. prefix
    domain = parsed.netloc.replace('www.', '')
    
    # Remove everything after first forward slash
    domain = domain.split('/')[0]
    
    # Convert to snake case and remove special characters
    filename = re.sub(r'[^\w\s-]', '', domain)
    filename = re.sub(r'[-\s]+', '_', filename).strip('-_')
    
    return f"{filename.lower()}.py"

@app.command()
def convert(
    framework: Optional[Framework] = typer.Option(
        None,
        "--framework",
        "-f",
        help="Framework to use (grab or context)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v", 
        help="Display the converted code in terminal"
    ),
    output: bool = typer.Option(
        False,
        "--output",
        "-o",
        help="Save the generated code to a .py file in current directory"
    ),
    test_mode: bool = typer.Option(
        False,
        hidden=True
    )
):
    """Convert a cURL command from clipboard to Python code."""
    try:
        if not framework:
            framework = get_framework(test_mode)
            print()  # Add spacing
        
        curl_command = get_curl_command(test_mode)
        parsed_curl = CurlParser.parse_curl(curl_command)
        python_code = form_code(parsed_curl, framework=framework)
        
        # Copy plain text to clipboard
        pyperclip.copy(python_code)
        print(f"[green]✓[/green] Converted code has been copied to clipboard!")
        
        # If verbose, display with syntax highlighting
        if verbose:
            display_code(python_code)
            
        # If output flag is set, save to file
        if output:
            filename = sanitize_filename(parsed_curl['url'])
            file_path = Path.cwd() / filename
            
            # Check if file exists and handle accordingly
            if file_path.exists():
                count = 1
                while file_path.exists():
                    base = filename.rsplit('.', 1)[0]
                    file_path = Path.cwd() / f"{base}_{count}.py"
                    count += 1
            
            # Write the code to file
            file_path.write_text(python_code)
            print(f"[green]✓[/green] Code saved to {file_path}")
            
    except Exception as e:
        print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

def curl2py():
    """Main entry point for curlpyconvert."""
    import sys
    args = sys.argv[1:]
    if not args or args[0] in ['-h', '--help']:
        # If no args or help requested, pass them directly
        app(["convert", "--help"])
    else:
        # Otherwise, prepend "convert" and pass all other args
        app(["convert"] + args)

def curl2ctx():
    """Main entry point for context framework."""
    app(["convert", "-f", "context"])

def curl2grab():
    """Main entry point for grab framework."""
    app(["convert", "-f", "grab"])

def curl2dog():
    """Main entry point for dogman framework."""
    app(["convert", "-f", "dogman"])

if __name__ == "__main__":
    app()