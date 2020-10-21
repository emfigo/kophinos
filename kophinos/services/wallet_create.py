from kophinos.exceptions import InvalidUser, InvalidWallet
from kophinos.models.currency import Currency
from kophinos.models.user import User
from kophinos.models.user_authentication_detail import UserAuthenticationDetail
from kophinos.models.wallet import Wallet

class WalletCreate:
    MANDATORY_FIELDS = [
        'currency'
    ]

    def __init__(self, user_token: str, currency: str):
        self.user = self._get_user(user_token)
        self.currency = self._get_currency(currency)

    def _get_user(self, user_token: str):
        user_authentication_detail = UserAuthenticationDetail.find_by_token(user_token)

        if user_authentication_detail is None:
            raise InvalidUser

        return User.find_by_id(user_authentication_detail.user_id)

    def _get_currency(self, currency):
        return Currency.get(currency)

    def create_wallet(self):
        wallet = Wallet.find_by_user_and_currency(self.user, self.currency)

        if wallet is None:
            wallet = Wallet.create(
                self.user,
                self.currency
            )

        return wallet

    @classmethod
    def call(kls, user_token: str, details: dict):
        service = kls(user_token, **kls._slice(details))

        return service.create_wallet()

    @classmethod
    def _slice(kls, details: dict) -> dict:
        sliced_details = {}

        for k in kls.MANDATORY_FIELDS:
            if details.get(k) is not None:
                sliced_details[k] = details[k]
            else:
                raise InvalidWallet

        return sliced_details
