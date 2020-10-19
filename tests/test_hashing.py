import hashlib
import pytest
import secrets
from string import ascii_letters, digits, punctuation

from kophinos.hashing import hash

class TestHashing:
    PASSWORD_SIZE = 256

    @pytest.mark.parametrize('word', [
        ''.join(secrets.choice(ascii_letters) for i in range(PASSWORD_SIZE)),
        ''.join(secrets.choice(digits) for i in range(PASSWORD_SIZE)),
        ''.join(secrets.choice(punctuation) for i in range(PASSWORD_SIZE)),
        ''.join(secrets.choice(ascii_letters + digits + punctuation) for i in range(PASSWORD_SIZE))
    ])
    def test_hash_word(self, word):
        assert hash(word) == str(hashlib.sha256(word.encode()))

