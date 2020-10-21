from enum import Enum, unique

from kophinos.exceptions import InvalidCurrency

@unique
class Currency(Enum):
    SGD = 1

    @classmethod
    def get(kls, name: str):
        try:
            return getattr(kls, name)
        except:
            raise InvalidCurrency
