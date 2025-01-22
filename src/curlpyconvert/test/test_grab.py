import pytest
from ..lib.grab import GrabCodeWriter

def test_simple_get():
    parsed = {
        'method': 'get',
        'url': 'https://api.example.com/data',
        'data': {},
        'headers': {},
        'cookies': {}
    }
    
    writer = GrabCodeWriter(parsed)
    code = writer.generate_code()
    
    assert "self.g.go('https://api.example.com/data')" in code

def test_with_headers():
    parsed = {
        'method': 'get',
        'url': 'https://api.example.com/data',
        'data': {},
        'headers': {'accept': 'application/json'},
        'cookies': {}
    }
    
    writer = GrabCodeWriter(parsed)
    code = writer.generate_code()
    
    assert 'self.g.setup(headers=' in code
    assert '"accept": "application/json # should not be necessary"' in code

def test_with_cookies():
    parsed = {
        'method': 'get',
        'url': 'https://api.example.com/data',
        'data': {},
        'headers': {},
        'cookies': {'session': 'abc123'}
    }
    
    writer = GrabCodeWriter(parsed)
    code = writer.generate_code()
    
    assert 'self.g.setup(cookies=' in code
    assert '"session": "abc123"' in code

def test_post_request():
    parsed = {
        'method': 'post',
        'url': 'https://api.example.com/data',
        'data': {},
        'headers': {},
        'cookies': {}
    }
    
    writer = GrabCodeWriter(parsed)
    code = writer.generate_code()
    
    assert "self.g.go('https://api.example.com/data')" in code
