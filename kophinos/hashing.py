import hashlib

def hash(word: str) -> str:
    return str(hashlib.sha256(word.encode()))
