import pytest

from kophinos.exceptions import InvalidTransaction, InvalidWallet
from kophinos.services.transaction_create import TransactionCreate
from kophinos.services.user_create import UserCreate
from kophinos.services.wallet_create import WalletCreate
from kophinos.models.currency import Currency
from kophinos.models.transaction import Transaction, TransactionType
from kophinos.models.user import User
from kophinos.models.user_authentication_detail import UserAuthenticationDetail
from kophinos.models.wallet import Wallet

@pytest.mark.usefixtures('database')
class TestTransactionCreate:
    user_details = {
        'first_name': 'test',
        'last_name': 'test',
        'email': 'test.test@reallycool.test',
        'password': 'somepswd',
    }

    wallet_details = {
        'currency': Currency.SGD.name
    }

    @pytest.mark.parametrize('details', [
        { 'amount_cents': 100000, 'type': TransactionType.CREDIT.name, 'expected_output': 100000 },
        { 'amount_cents': 100000, 'type': TransactionType.DEBIT.name, 'expected_output': -100000 }
    ])
    def test_creates_transaction_modifying_wallet_when_all_details_correct(self, database, details):
        user_authentication_details = UserCreate.call(self.user_details)
        user = User.find_by_id(user_authentication_details.user_id)
        user_authentication_details.generate_token()
        wallet = WalletCreate.call(user_authentication_details.token, self.wallet_details)

        assert wallet.balance_cents == 0
        assert Transaction.query.count() == 0

        transaction = TransactionCreate.call(wallet, details)

        assert Transaction.query.first() == transaction
        assert wallet.balance_cents == details['expected_output']

    @pytest.mark.parametrize('invalid_details', [
        { 'amount_cents': None, 'type': TransactionType.CREDIT.name },
        { 'amount_cents': '', 'type': TransactionType.CREDIT.name },
        { 'amount_cents': '100000', 'type': TransactionType.CREDIT.name },
        { 'amount_cents': 100000, 'type': None },
        { 'amount_cents': 100000, 'type': '' },
        { 'amount_cents': 100000, 'type': 'SOMETHING' }
    ])
    def test_does_not_create_transaction_when_details_invalid(self, database, invalid_details):
        user_authentication_details = UserCreate.call(self.user_details)
        user = User.find_by_id(user_authentication_details.user_id)
        user_authentication_details.generate_token()
        wallet = WalletCreate.call(user_authentication_details.token, self.wallet_details)

        prev_count = Transaction.query.count()

        with pytest.raises(InvalidTransaction):
            transaction = TransactionCreate.call(wallet, invalid_details)

        assert Transaction.query.count() == prev_count
        assert wallet.balance_cents == 0

    @pytest.mark.parametrize('details', [
        { 'amount_cents': 100000, 'type': TransactionType.CREDIT.name }
    ])
    def test_does_not_create_transaction_when_wallet_invalid(self, database, details):
        user_authentication_details = UserCreate.call(self.user_details)
        user = User.find_by_id(user_authentication_details.user_id)
        wallet = Wallet(user_id = user.id, currency = self.wallet_details['currency'])

        prev_count = Transaction.query.count()

        with pytest.raises(InvalidWallet):
            transaction = TransactionCreate.call(wallet, details)

        assert Transaction.query.count() == prev_count

