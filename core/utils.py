import re

def safe_filename(name: str) -> str:
    name = name.strip().replace(' ', '_')
    return re.sub(r'[^a-zA-Z0-9_.-]', '', name)