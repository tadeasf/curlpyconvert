import re
import json
import shlex
from argparse import ArgumentParser
from collections import OrderedDict
from typing import Dict, Any, List, Tuple, Optional
from urllib.parse import unquote_plus, parse_qsl, urlsplit
from http.cookies import SimpleCookie

class CurlParser:
    """Parser for curl commands with modern Python features."""
    
    @staticmethod
    def parse_curl(curl_command: str) -> Dict[str, Any]:
        """Parse curl command into structured data."""
        if not curl_command or not curl_command.strip():
            raise ValueError("Empty curl command")
        
        # Clean up the curl command - handle multiline and escapes
        curl_command = curl_command.replace('\\\n', ' ').replace('\\', '')
        curl_command = curl_command.strip()
        
        if not curl_command.startswith('curl'):
            raise ValueError("Invalid curl command")
        
        # Parse arguments
        parser = ArgumentParser()
        parser.add_argument('command')
        parser.add_argument('url', nargs='?')
        parser.add_argument('-d', '--data')
        parser.add_argument('-b', '--data-binary', default=None)
        parser.add_argument('--data-raw', default=None)
        parser.add_argument('-X', default='')
        parser.add_argument('-H', '--header', action='append', default=[])
        parser.add_argument('--compressed', action='store_true')
        parser.add_argument('-k', '--insecure', action='store_true')
        
        try:
            args = shlex.split(curl_command, posix=True)
            parsed_args = parser.parse_args(args)
            
            if not parsed_args.url:
                raise ValueError("URL is required")
            
            # Extract data from various possible sources
            post_data = (parsed_args.data or parsed_args.data_binary or 
                        parsed_args.data_raw)
            
            if post_data:
                method = 'post'
                post_data = post_data.lstrip('$')  # Remove leading $ if present
                
                try:
                    ordered_data = parse_qsl(post_data)
                    data_dict = dict(ordered_data)
                    data_as_json = False
                except Exception:
                    data_as_json = True
                    try:
                        data_dict = json.loads(post_data)
                    except ValueError:
                        data_dict = CurlParser._eval_js_object(post_data)
                    ordered_data = None
            else:
                method = 'get'
                data_as_json = False
                parsed_url = urlsplit(parsed_args.url)
                ordered_data = parse_qsl(parsed_url.query)
                data_dict = dict(ordered_data)
                parsed_args.url = f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}'

            return CurlParser._process_parsed_args(parsed_args, post_data)
            
        except Exception as e:
            if isinstance(e, SystemExit):
                # This means ArgumentParser showed help or had an error
                if not curl_command.strip().endswith('curl'):
                    raise ValueError("Invalid curl command format")
                raise ValueError("URL is required")
            raise ValueError(str(e))
    
    @staticmethod
    def _process_parsed_args(parsed_args, post_data=None) -> Dict[str, Any]:
        """Process parsed arguments into structured data."""
        if post_data:
            return CurlParser._handle_post_request(post_data, parsed_args)
        else:
            return CurlParser._handle_get_request(parsed_args)

    @staticmethod
    def _handle_post_request(post_data: str, parsed_args) -> Dict[str, Any]:
        """Handle POST request parsing."""
        post_data = post_data.strip().lstrip('$')
        
        try:
            # First try to parse as JSON
            try:
                post_data_dict = json.loads(post_data)
                data_as_json = True
                ordered_post_data = None
            except json.JSONDecodeError:
                # If not JSON, try query string
                ordered_post_data = parse_qsl(post_data)
                post_data_dict = dict(ordered_post_data)
                data_as_json = False
        except Exception:
            # If both fail, try JavaScript object notation
            data_as_json = True
            post_data_dict = CurlParser._eval_js_object(post_data)
            ordered_post_data = None

        return {
            'method': 'post',
            'url': parsed_args.url,
            'data': post_data_dict,
            'ordered_data': ordered_post_data,
            'data_as_json': data_as_json,
            **CurlParser._parse_headers_and_cookies(parsed_args.header)
        }

    @staticmethod
    def _handle_get_request(parsed_args) -> Dict[str, Any]:
        """Handle GET request parsing."""
        parsed_url = urlsplit(parsed_args.url)
        ordered_data_dict = parse_qsl(parsed_url.query)
        
        return {
            'method': 'get',
            'url': f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}',
            'data': dict(ordered_data_dict),
            'ordered_data': ordered_data_dict,
            'data_as_json': False,
            **CurlParser._parse_headers_and_cookies(parsed_args.header)
        }

    @staticmethod
    def _parse_headers_and_cookies(headers: List[str]) -> Dict[str, Dict[str, str]]:
        """Parse headers and cookies from curl command."""
        cookie_dict = OrderedDict()
        headers_dict = OrderedDict()

        for header in headers:
            key, value = header.split(":", 1)
            
            if key.lower() == 'cookie':
                cookie = SimpleCookie(value)
                for k in cookie:
                    try:
                        cookie_dict[k] = unquote_plus(cookie[k].value)
                    except Exception:
                        cookie_dict[k] = cookie[k].value
            else:
                headers_dict[key] = value.strip()

        return {
            'headers': headers_dict,
            'cookies': cookie_dict
        }

    @staticmethod
    def _eval_js_object(data: str) -> Dict[str, Any]:
        """Evaluate JSON-like JavaScript code object."""
        loops_left = 200
        while 'Array(' in data and loops_left > 0:
            data = re.sub(r'(?:new\s+)?Array\(([^\)]*)\)', r'[\g<1>]', data)
            loops_left -= 1
            
        if 'Array(' in data:
            raise ValueError("Couldn't convert Array()")

        data = re.sub(r"([a-zA-Z]\w+)\s*:", r"'\g<1>':", data)
        data = data.replace("'", '"')

        for apos in re.findall('[a-zA-Z]\"[a-zA-Z]', data):
            data = data.replace(apos, apos.replace('"', "'"))

        return json.loads(data)
