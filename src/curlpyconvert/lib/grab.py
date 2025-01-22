from typing import Dict, Any
import json
from collections import OrderedDict

class GrabCodeWriter:
    """Generates Grab framework code from parsed curl commands."""
    
    COMMON_HEADERS = [
        'accept-encoding',
        'accept-language',
        'accept',
        'connection',
        'user-agent'
    ]

    def __init__(self, parsed_command: Dict[str, Any]):
        self.parsed = parsed_command
        
    def generate_code(self) -> str:
        """Generate the grab code."""
        code_parts = []
        
        # Reset headers if needed
        code_parts.append('self.g.setup(common_headers={})  # remove this line if possible')
        
        # Add cookies setup if present
        if self.parsed.get('cookies'):
            code_parts.append(f"self.g.setup(cookies={json.dumps(self.parsed['cookies'], indent=4)})")
            
        # Add headers setup if present
        if self.parsed.get('headers'):
            headers = self.parsed['headers'].copy()
            # Mark common headers
            for header in ['accept', 'accept-language', 'user-agent']:
                if header in headers:
                    headers[header] = f"{headers[header]} # should not be necessary"
            code_parts.append(f"self.g.setup(headers={json.dumps(headers, indent=4)})")
        
        # Generate just the request line without params
        url = self.parsed['url']
        code_parts.append(f"self.g.go('{url}')")
        
        return '\n\n'.join(code_parts)

    def _generate_ordered_params(self) -> str:
        """Generate code for ordered parameters."""
        if not self.parsed.get('ordered_data'):
            return ''
            
        params_name = f"{self.parsed['method']}_params"
        ordered_data = self.parsed['ordered_data']
        
        list_code = '[\n'
        for item in ordered_data:
            list_code += f'    {str(item)},\n'
        list_code += ']'
        
        # Comment out the ordered params
        lines = [f"# {line}" for line in f"{params_name} = {list_code}".split('\n')]
        return '\n'.join(lines)

    def _generate_headers(self) -> str:
        """Generate code for headers setup."""
        if not self.parsed.get('headers'):
            return ''
            
        headers_dict = OrderedDict()
        for key, value in self.parsed['headers'].items():
            headers_dict[key] = value
            if key.lower() in self.COMMON_HEADERS:
                headers_dict[key] = f"{value} # should not be necessary"

        return f'self.g.setup(headers={json.dumps(headers_dict, indent=4)})'

    def _generate_cookies(self) -> str:
        """Generate code for cookies setup."""
        if not self.parsed.get('cookies'):
            return ''
            
        cookies_dict = self._dict_to_python(
            self.parsed['cookies'],
            'cookies'
        )
        return f'self.g.setup({cookies_dict})'

    def _generate_params(self) -> str:
        """Generate code for request parameters."""
        if not self.parsed.get('data'):
            return ''
        
        params_name = f"{self.parsed['method']}_params"
        return self._dict_to_python(
            self.parsed['data'],
            params_name
        )

    def _generate_request(self) -> str:
        """Generate the actual request code."""
        url = self.parsed['url']
        method = self.parsed['method']
        
        if not self.parsed.get('data'):
            return f"self.g.go('{url}')"
        
        params_name = f"{method}_params"
        
        if method == 'get':
            params_type = 'params'
        else:
            params_type = 'json' if self.parsed['data_as_json'] else 'post'
            
        return f"self.g.go('{url}', {params_type}={params_name})"

    def _dict_to_python(self, data: Dict, var_name: str, mark_common: bool = False) -> str:
        """Convert dictionary to Python code string."""
        dict_str = json.dumps(data, indent=4)
        
        if mark_common:
            lines = []
            for line in dict_str.split('\n'):
                if any(h in line.lower() for h in self.COMMON_HEADERS):
                    line += ' # should not be necessary'
                lines.append(line)
            dict_str = '\n'.join(lines)
            
        return f"{var_name}={dict_str}"