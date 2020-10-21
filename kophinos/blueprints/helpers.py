from kophinos.exceptions import InvalidCurrency
from kophinos.models.currency import Currency
from kophinos.models.wallet import Wallet

def get_currency(currency_name):
    currency = None

    try:
        currency = Currency.get(currency_name)
    except InvalidCurrency:
        currency = 'Invalid currency. Please select specify another one.'

    return currency


def get_wallet(user, currency_name):
    output = None
    currency = get_currency(currency_name)

    if type(currency) is str:
        output = currency
    else:
        wallet = Wallet.find_by_user_and_currency(user, currency)

        if wallet is None:
            output = 'Invalid account. Account does not exist for user.'
        else:
            output = wallet

    return output
