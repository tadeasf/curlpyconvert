import pytest
from ..lib.dogman import DogmanCodeWriter

def test_simple_get():
    parsed = {
        'method': 'get',
        'url': 'https://api.example.com/data',
        'data': {},
        'headers': {},
        'cookies': {}
    }
    
    writer = DogmanCodeWriter(parsed)
    code = writer.generate_code()
    
    assert 'dogman_config = {' in code
    assert 'self.context.setup(dogman_config=dogman_config)' in code
    assert 'self.context.dogman.get_cookies("https://api.example.com/data", spoofing="akamai")' in code
    assert 'response = self.context.GET("https://api.example.com/data")' in code

def test_with_headers():
    parsed = {
        'method': 'get',
        'url': 'https://api.example.com/data',
        'data': {},
        'headers': {'accept': 'application/json'},
        'cookies': {}
    }
    
    writer = DogmanCodeWriter(parsed)
    code = writer.generate_code()
    
    assert 'self.context.headers.update(' in code
    assert '"accept": "application/json # should not be necessary"' in code

def test_post_request():
    parsed = {
        'method': 'post',
        'url': 'https://api.example.com/data',
        'data': {},
        'headers': {},
        'cookies': {}
    }
    
    writer = DogmanCodeWriter(parsed)
    code = writer.generate_code()
    
    assert 'response = self.context.POST("https://api.example.com/data")' in code
