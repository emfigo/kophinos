import pytest
import uuid

from kophinos.exceptions import InvalidUser, InvalidCurrency
from kophinos.models.user import User
from kophinos.models.wallet import Wallet
from kophinos.models.currency import Currency

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

        assert wallet.query.filter_by(
            user_id = user.id
        ).first().created_at == wallet.created_at
        assert wallet.created_at is not None

        assert wallet.query.filter_by(
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
