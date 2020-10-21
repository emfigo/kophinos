import pytest

from kophinos.exceptions import InvalidCurrency
from kophinos.models.currency import Currency

class TestCurrency:
    @pytest.mark.parametrize('valid_currency', [
        ('SGD', 1)
    ])
    def test_enum_valid_values(self, valid_currency):
        currency = getattr(Currency, valid_currency[0])

        assert currency.name == valid_currency[0]
        assert currency.value == valid_currency[1]

    @pytest.mark.parametrize('valid_currency', [
        'SGD'
    ])
    def test_get_valid_values(self, valid_currency):
        Currency.get(valid_currency) == getattr(Currency, valid_currency)

    @pytest.mark.parametrize('invalid_currency', [
        'NOTEXISTING',
        None,
        '',
        1,
        '1'
    ])
    def test_get_invalid_value(self, invalid_currency):
        with pytest.raises(InvalidCurrency):
            Currency.get(invalid_currency)
