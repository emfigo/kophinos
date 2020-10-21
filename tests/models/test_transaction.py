import pytest
import uuid

from kophinos.exceptions import InvalidWallet
from kophinos.models.user import User
from kophinos.models.currency import Currency
from kophinos.models.wallet import Wallet
from kophinos.models.transaction import Transaction, TransactionType

@pytest.mark.usefixtures('database')
class TestTransaction:
    first_name = 'Test'
    last_name = 'Test'
    email = 'test.test@reallycool.test'
    currency = Currency.SGD
    amount_cents = 1000000
    type = TransactionType.CREDIT

    @pytest.mark.parametrize('transaction_type', [
        TransactionType.CREDIT,
        TransactionType.DEBIT
    ])
    def test_creates_transaction_with_all_expected_attributes(self, database, transaction_type):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        wallet = Wallet.create(
            user,
            self.currency
        )

        transaction = Transaction.create(
            wallet,
            self.amount_cents,
            transaction_type

        )

        assert Transaction.query.filter_by(
            wallet_id = wallet.id
        ).count() == 1

        assert Transaction.query.filter_by(
            wallet_id = wallet.id
        ).first().id == transaction.id
        assert transaction.id is not None

        assert Transaction.query.filter_by(
            wallet_id = wallet.id
        ).first().created_at == transaction.created_at
        assert transaction.created_at is not None

        assert transaction.type == transaction_type.name
        assert transaction.amount_cents == self.amount_cents


    def test_does_not_create_transaction_when_wallet_not_valid(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        wallet = Wallet(
            id = uuid.uuid4(),
            user_id = user.id,
            currency = self.currency
        )

        prev_count = Transaction.query.count()

        with pytest.raises(InvalidWallet):
            transaction = Transaction.create(
                wallet,
                self.amount_cents,
                self.type

            )

        assert Transaction.query.count() == prev_count
