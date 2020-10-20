import hashlib

def hash(word: str) -> str:
    hashed_version = None

    if word is not None:
        hashed_version = str(hashlib.sha256(word.encode()).hexdigest())

    return hashed_version
