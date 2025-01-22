from typing import Dict, Any
import json

class DogmanCodeWriter:
    """Generates Dogman framework code from parsed curl commands."""
    
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
        """Generate Dogman framework code from parsed curl command."""
        code_parts = []
        
        # Add dogman config setup
        code_parts.append('dogman_config = {\n    "setup": {}\n}')
        code_parts.append('self.context.setup(dogman_config=dogman_config)')
        
        # Get cookies using dogman
        url = self.parsed['url']
        code_parts.append(f'self.context.dogman.get_cookies("{url}", spoofing="akamai")')
        
        # Add headers setup if present
        if self.parsed.get('headers'):
            headers = self.parsed['headers'].copy()
            # Mark common headers
            for header in ['accept', 'accept-language', 'user-agent']:
                if header in headers:
                    headers[header] = f"{headers[header]} # should not be necessary"
            code_parts.append(f'self.context.headers.update({json.dumps(headers, indent=4)})')
        
        # Generate just the request line without params
        method = self.parsed['method'].upper()
        code_parts.append(f'response = self.context.{method}("{url}")')
        
        return '\n\n'.join([p for p in code_parts if p])
