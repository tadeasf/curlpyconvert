import pytest
import pyperclip
from typer.testing import CliRunner
from ..main import app

runner = CliRunner()

def test_convert_grab():
    curl_cmd = """curl 'https://api.example.com/data'"""
    pyperclip.copy(curl_cmd)
    
    result = runner.invoke(app, ["convert", "-f", "grab", "--test-mode"])
    assert result.exit_code == 0
    assert "has been copied to clipboard" in result.stdout

def test_convert_context():
    curl_cmd = """curl 'https://api.example.com/data'"""
    pyperclip.copy(curl_cmd)
    
    result = runner.invoke(app, ["convert", "-f", "context", "--test-mode"])
    assert result.exit_code == 0
    assert "has been copied to clipboard" in result.stdout

def test_show_output():
    curl_cmd = """curl 'https://api.example.com/data'"""
    pyperclip.copy(curl_cmd)
    
    result = runner.invoke(app, ["convert", "-f", "grab", "-v", "--test-mode"])
    assert result.exit_code == 0
    assert "self.g.go('https://api.example.com/data')" in pyperclip.paste()

def test_invalid_curl():
    pyperclip.copy("not a curl command")
    
    result = runner.invoke(app, ["convert", "-f", "grab", "--test-mode"])
    assert result.exit_code == 1
    assert "Invalid curl command" in str(result.stdout)

def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "curl-to-context version:" in result.stdout

def test_convert_interactive(monkeypatch):
    # Mock clipboard content
    curl_cmd = """curl 'https://api.example.com/data'"""
    pyperclip.copy(curl_cmd)
    
    result = runner.invoke(app, ["convert", "--test-mode"])
    assert result.exit_code == 0
    assert "has been copied to clipboard" in result.stdout

def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Convert cURL commands" in result.stdout

def test_convert_help():
    result = runner.invoke(app, ["convert", "--help"])
    assert result.exit_code == 0
    assert "Framework to use" in result.stdout

def test_convert_dogman():
    curl_cmd = """curl 'https://api.example.com/data'"""
    pyperclip.copy(curl_cmd)
    
    result = runner.invoke(app, ["convert", "-f", "dogman", "--test-mode"])
    assert result.exit_code == 0
    assert "has been copied to clipboard" in result.stdout

def test_convert_dogman_output():
    curl_cmd = """curl 'https://api.example.com/data'"""
    pyperclip.copy(curl_cmd)
    
    result = runner.invoke(app, ["convert", "-f", "dogman", "-v", "--test-mode"])
    assert result.exit_code == 0
    output = pyperclip.paste()
    assert 'dogman_config = {' in output
    assert 'self.context.setup(dogman_config=dogman_config)' in output
    assert 'self.context.dogman.get_cookies("https://api.example.com/data", spoofing="akamai")' in output

def test_help_shows_aliases():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Available command aliases:" in result.stdout
    assert "curlpyconvert" in result.stdout
    assert "curl2py" in result.stdout
    assert "c2py" in result.stdout
    assert "curl2ctx" in result.stdout
    assert "curl2grab" in result.stdout
    assert "curl2dog" in result.stdout 