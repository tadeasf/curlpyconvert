import pytest
from ..lib.context import ContextCodeWriter

def test_simple_get():
    parsed = {
        'method': 'get',
        'url': 'https://api.example.com/data',
        'data': {},
        'headers': {},
        'cookies': {}
    }
    
    writer = ContextCodeWriter(parsed)
    code = writer.generate_code()
    
    assert 'response = self.context.GET("https://api.example.com/data")' in code

def test_with_headers():
    parsed = {
        'method': 'get',
        'url': 'https://api.example.com/data',
        'data': {},
        'headers': {'accept': 'application/json'},
        'cookies': {}
    }
    
    writer = ContextCodeWriter(parsed)
    code = writer.generate_code()
    
    assert 'self.context.headers.update(' in code
    assert '"accept": "application/json"' in code

def test_with_cookies():
    parsed = {
        'method': 'get',
        'url': 'https://api.example.com/data',
        'data': {},
        'headers': {},
        'cookies': {'session': 'abc123'}
    }
    
    writer = ContextCodeWriter(parsed)
    code = writer.generate_code()
    
    assert 'self.context.cookies.update(' in code
    assert '"session": "abc123"' in code

def test_post_request():
    parsed = {
        'method': 'post',
        'url': 'https://api.example.com/data',
        'data': {'key': 'value'},
        'data_as_json': True,
        'headers': {},
        'cookies': {}
    }
    
    writer = ContextCodeWriter(parsed)
    code = writer.generate_code()
    
    assert 'response = self.context.POST("https://api.example.com/data")' in code
