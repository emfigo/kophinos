import pytest
import uuid

from kophinos.exceptions import InvalidUser
from kophinos.models.user import User
from kophinos.models.currency import Currency
from kophinos.models.transfer import Transfer

@pytest.mark.usefixtures('database')
class TestTransaction:
    sender = {
        'first_name': 'Sender',
        'last_name': 'Test',
        'email': 'sender.test@reallycool.test'
    }

    receiver = {
        'first_name': 'Receiver',
        'last_name': 'Test',
        'email': 'receiver.test@reallycool.test'
    }

    currency = Currency.SGD
    amount_cents = 1000000

    def test_creates_transfer_with_all_expected_attributes(self, database):
        sender = User.create(
            first_name = self.sender['first_name'],
            last_name = self.sender['last_name'],
            email = self.sender['email']
        )

        receiver = User.create(
            first_name = self.receiver['first_name'],
            last_name = self.receiver['last_name'],
            email = self.receiver['email']
        )

        transfer = Transfer.create(
            sender,
            receiver,
            self.amount_cents,
            self.currency

        )

        assert Transfer.query.filter_by(
            sender_user_id = sender.id,
            receiver_user_id = receiver.id
        ).count() == 1

        assert Transfer.query.filter_by(
            sender_user_id = sender.id,
            receiver_user_id = receiver.id
        ).first().id == transfer.id
        assert transfer.id is not None

        assert Transfer.query.filter_by(
            sender_user_id = sender.id,
            receiver_user_id = receiver.id
        ).first().created_at == transfer.created_at
        assert transfer.created_at is not None

        assert transfer.currency == self.currency.name
        assert transfer.amount_cents == self.amount_cents


    def test_does_not_create_transfer_when_sender_not_valid(self, database):
        sender = User(
            id = uuid.uuid4(),
            first_name = self.sender['first_name'],
            last_name = self.sender['last_name'],
            email = self.sender['email']
        )

        receiver = User.create(
            first_name = self.receiver['first_name'],
            last_name = self.receiver['last_name'],
            email = self.receiver['email']
        )

        prev_count = Transfer.query.count()

        with pytest.raises(InvalidUser):
            transfer = Transfer.create(
                sender,
                receiver,
                self.amount_cents,
                self.currency

            )

        assert Transfer.query.count() == prev_count

    def test_does_not_create_transfer_when_receiver_not_valid(self, database):
        sender = User.create(
            first_name = self.sender['first_name'],
            last_name = self.sender['last_name'],
            email = self.sender['email']
        )

        receiver = User(
            id = uuid.uuid4(),
            first_name = self.receiver['first_name'],
            last_name = self.receiver['last_name'],
            email = self.receiver['email']
        )

        prev_count = Transfer.query.count()

        with pytest.raises(InvalidUser):
            transfer = Transfer.create(
                sender,
                receiver,
                self.amount_cents,
                self.currency

            )

        assert Transfer.query.count() == prev_count
