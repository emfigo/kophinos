import secrets

class Tokenizer:
    """
    This class is heavily based on the core library used in python called secrets. This
    library already contains basics for what is required for constructing good tokenization.
    Anything more complex can be analysed individually based on requirements.
    For more information read:
    https://docs.python.org/3/library/secrets.html
    https://www.python.org/dev/peps/pep-0506/

    """

    TOKEN_SIZE = 256 // 8 # 256 chars, and approx 8 bytes to represent each char

    @classmethod
    def random_token(kls) -> str:
        return secrets.token_urlsafe(kls.TOKEN_SIZE)
