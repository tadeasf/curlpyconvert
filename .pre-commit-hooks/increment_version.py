#!/usr/bin/env python3
import re
import subprocess
from pathlib import Path

def increment_version(version_str: str) -> str:
    """Increment version following semantic versioning rules."""
    major, minor, patch = map(int, version_str.split('.'))
    
    # Increment patch version
    patch += 1
    
    # If patch reaches 10, increment minor and reset patch
    if patch == 10:
        minor += 1
        patch = 0
    
    # If minor reaches 10, it should be manually handled as it might be a major version bump
    if minor == 10:
        print("Warning: Minor version has reached 10. Consider a major version bump!")
    
    return f"{major}.{minor}.{patch}"

def stage_file(file_path: str):
    """Stage the modified file."""
    try:
        subprocess.run(["git", "add", file_path], check=True)
    except subprocess.CalledProcessError:
        print(f"Warning: Could not stage {file_path}")

def update_version_in_file(file_path: str) -> int:
    """Update version in pyproject.toml file."""
    content = Path(file_path).read_text()
    
    # Find current version
    version_match = re.search(r'version\s*=\s*"(\d+\.\d+\.\d+)"', content)
    if not version_match:
        print(f"Error: Could not find version in {file_path}")
        return 1
    
    current_version = version_match.group(1)
    new_version = increment_version(current_version)
    
    # Replace version in file
    new_content = content.replace(
        f'version = "{current_version}"',
        f'version = "{new_version}"'
    )
    
    # Write back to file
    Path(file_path).write_text(new_content)
    print(f"Version bumped: {current_version} -> {new_version}")
    
    # Stage the modified file
    stage_file(file_path)
    return 0

def main():
    """Main function."""
    pyproject_path = "pyproject.toml"
    return update_version_in_file(pyproject_path)

if __name__ == "__main__":
    raise SystemExit(main()) 