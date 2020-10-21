import pytest
import uuid

from kophinos.exceptions import InvalidUser, InvalidCurrency
from kophinos.models.currency import Currency
from kophinos.models.transaction import TransactionType
from kophinos.models.user import User
from kophinos.models.wallet import Wallet

@pytest.mark.usefixtures('database')
class TestUser:
    first_name = 'Test'
    last_name = 'Test'
    email = 'test.test@reallycool.test'
    currency = Currency.SGD

    def test_creates_wallet_with_all_expected_attributes(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        wallet = Wallet.create(
            user,
            self.currency
        )

        assert Wallet.query.filter_by(
            user_id = user.id
        ).count() == 1

        assert Wallet.query.filter_by(
            user_id = user.id
        ).first().id == wallet.id
        assert wallet.id is not None

        assert Wallet.query.filter_by(
            user_id = user.id
        ).first().created_at == wallet.created_at
        assert wallet.created_at is not None

        assert Wallet.query.filter_by(
            user_id = user.id
        ).first().updated_at == wallet.updated_at
        assert wallet.updated_at is not None

        assert wallet.currency == self.currency.name
        assert wallet.balance_cents == 0

    def test_does_not_create_wallet_with_duplicated_currency(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        wallet = Wallet.create(
            user,
            self.currency
        )

        prev_count = Wallet.query.filter_by(
            user_id = user.id
        ).count()


        with pytest.raises(InvalidCurrency):
            wallet = Wallet.create(
                user,
                self.currency
            )

        assert Wallet.query.filter_by(
            user_id = user.id
        ).count() == prev_count

    def test_does_not_create_wallet_with_non_existing_user(self, database):
        user = User(
            id = uuid.uuid4(),
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        prev_count = Wallet.query.count()

        with pytest.raises(InvalidUser):
            wallet = Wallet.create(
                user,
                self.currency
            )

        assert Wallet.query.count() == prev_count

    def test_finds_by_id_returns_the_expected_user(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        user2 = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = 'someotheremail@test.test'
        )

        wallet = Wallet.create(
            user,
            self.currency
        )

        assert Wallet.query.count() == 1
        assert Wallet.find_by_user_and_currency(user2, self.currency) is None
        assert Wallet.find_by_user_and_currency(user, self.currency) == wallet

    def test_find_all_by_user_returns_all_expected_wallets(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        user2 = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = 'someotheremail@test.test'
        )

        wallet = Wallet.create(
            user,
            self.currency
        )

        assert Wallet.query.count() == 1
        assert Wallet.find_all_by_user(user2) == []
        assert Wallet.find_all_by_user(user) == [wallet]

    def test_as_dict_converts_wallet_into_expected_dict(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        wallet = Wallet.create(
            user,
            self.currency
        )

        expected_dict = {
            'id': wallet.id,
            'currency': wallet.currency,
            'balance_cents': wallet.balance_cents,
            'updated_at': int(wallet.updated_at.timestamp()),
            'created_at': int(wallet.created_at.timestamp())
        }

        assert wallet.as_dict() == expected_dict

    @pytest.mark.parametrize('operation', [
        (100000, TransactionType.CREDIT, 100000),
        (100000, TransactionType.DEBIT, -100000)
    ])
    def test_add_operation_modifies_wallet_balance_accordingly(self, database, operation):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        wallet = Wallet.create(
            user,
            self.currency
        )

        assert wallet.balance_cents == 0

        wallet.add_operation(operation[0], operation[1])

        assert wallet.balance_cents == operation[2]

