
import pytest

from kophinos.exceptions import InvalidUser, InvalidCurrency, InvalidWallet
from kophinos.services.user_create import UserCreate
from kophinos.services.wallet_create import WalletCreate
from kophinos.models.currency import Currency
from kophinos.models.user import User
from kophinos.models.user_authentication_detail import UserAuthenticationDetail
from kophinos.models.wallet import Wallet

@pytest.mark.usefixtures('database')
class TestWalletCreate:
    user_details = {
        'first_name': 'test',
        'last_name': 'test',
        'email': 'test.test@reallycool.test',
        'password': 'somepswd',
    }

    currency = Currency.SGD

    details = {
        'currency': currency.name
    }

    def test_creates_wallet_when_all_details_correct(self, database):
        user_authentication_details = UserCreate.call(self.user_details)
        user = User.find_by_id(user_authentication_details.user_id)

        assert Wallet.find_by_user_and_currency(user, self.currency) is None
        user_authentication_details.generate_token()

        wallet = WalletCreate.call(user_authentication_details.token, self.details)

        assert Wallet.find_by_user_and_currency(user, self.currency) == wallet

    def test_returns_existing_wallet_when_already_created(self, database):
        user_authentication_details = UserCreate.call(self.user_details)
        user = User.find_by_id(user_authentication_details.user_id)
        user_authentication_details.generate_token()

        existing_wallet = WalletCreate.call(user_authentication_details.token, self.details)

        wallet = WalletCreate.call(user_authentication_details.token, self.details)

        assert existing_wallet == wallet

    @pytest.mark.parametrize('invalid_token', [
        None,
        'somenonexistingtoken',
        ''
    ])
    def test_does_not_create_wallet_when_not_valid_token_provided(self, database, invalid_token):
        user_authentication_details = UserCreate.call(self.user_details)
        user = User.find_by_id(user_authentication_details.user_id)

        prev_count = Wallet.query.count()

        with pytest.raises(InvalidUser):
            wallet = WalletCreate.call(invalid_token, self.details)

        assert Wallet.query.count() == prev_count

    @pytest.mark.parametrize('invalid_details', [
        { 'currency': '' },
        { 'currency': 'USD' }
    ])
    def test_does_not_create_wallet_when_not_valid_details_provided(self, database, invalid_details):
        user_authentication_details = UserCreate.call(self.user_details)
        user = User.find_by_id(user_authentication_details.user_id)
        user_authentication_details.generate_token()

        prev_count = Wallet.query.count()

        with pytest.raises(InvalidCurrency):
            wallet = WalletCreate.call(user_authentication_details.token, { **self.details, **invalid_details } )

        assert Wallet.query.count() == prev_count

    @pytest.mark.parametrize('invalid_details', [
        { 'currency': None },
        {}
    ])
    def test_does_not_create_wallet_when_no_details_provided(self, database, invalid_details):
        user_authentication_details = UserCreate.call(self.user_details)
        user = User.find_by_id(user_authentication_details.user_id)
        user_authentication_details.generate_token()

        prev_count = Wallet.query.count()

        with pytest.raises(InvalidWallet):
            wallet = WalletCreate.call(user_authentication_details.token, invalid_details)

        assert Wallet.query.count() == prev_count
