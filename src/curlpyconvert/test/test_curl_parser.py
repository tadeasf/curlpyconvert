import pytest
from ..lib.curl_parser import CurlParser

def test_parse_simple_get():
    curl = """curl 'https://api.example.com/data'"""
    result = CurlParser.parse_curl(curl)
    
    assert result['method'] == 'get'
    assert result['url'] == 'https://api.example.com/data'
    assert not result['data']
    assert not result['headers']
    assert not result['cookies']

def test_parse_with_headers():
    curl = """curl 'https://api.example.com/data' -H 'accept: application/json' -H 'user-agent: Mozilla/5.0'"""
    result = CurlParser.parse_curl(curl)
    
    assert result['headers'] == {
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0'
    }

def test_parse_with_cookies():
    curl = """curl 'https://api.example.com/data' -H 'cookie: session=abc123; user=john'"""
    result = CurlParser.parse_curl(curl)
    
    assert result['cookies'] == {
        'session': 'abc123',
        'user': 'john'
    }

def test_parse_post_data():
    curl = """curl 'https://api.example.com/data' -d '{"key":"value"}'"""
    result = CurlParser.parse_curl(curl)
    
    assert result['method'] == 'post'
    assert result['data'] == {'key': 'value'}
    assert result['data_as_json'] == True

def test_invalid_curl():
    with pytest.raises(ValueError):
        CurlParser.parse_curl("not a curl command")

def test_empty_curl():
    with pytest.raises(ValueError, match="Empty curl command"):
        CurlParser.parse_curl("")
        
def test_missing_url():
    with pytest.raises(ValueError, match="URL is required"):
        CurlParser.parse_curl("curl")

def test_complex_post_data():
    curl = """curl 'https://api.example.com/data' -d 'key1=value1&key2=value2'"""
    result = CurlParser.parse_curl(curl)
    
    assert result['method'] == 'post'
    assert result['data'] == {'key1': 'value1', 'key2': 'value2'}
    assert not result['data_as_json']

def test_array_in_json():
    curl = """curl 'https://api.example.com/data' -d '{"items": ["a", "b"]}'"""
    result = CurlParser.parse_curl(curl)
    
    assert result['data'] == {'items': ['a', 'b']}
    assert result['data_as_json']

def test_data_raw():
    curl = """curl 'https://api.example.com/data' --data-raw '{"key":"value"}'"""
    result = CurlParser.parse_curl(curl)
    
    assert result['method'] == 'post'
    assert result['data'] == {'key': 'value'}
    assert result['data_as_json'] == True

def test_complex_data_raw():
    curl = """curl 'https://api.example.com/data' --data-raw '{"items":["a","b"],"nested":{"key":"value"}}'"""
    result = CurlParser.parse_curl(curl)
    
    assert result['method'] == 'post'
    assert result['data'] == {
        'items': ['a', 'b'],
        'nested': {'key': 'value'}
    }
    assert result['data_as_json'] == True
