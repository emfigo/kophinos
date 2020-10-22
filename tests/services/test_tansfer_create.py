import pytest

from kophinos.exceptions import InvalidTransaction, InvalidTransfer, InvalidUser, InvalidWallet
from kophinos.models.currency import Currency
from kophinos.models.transaction import Transaction, TransactionType
from kophinos.models.transfer import Transfer
from kophinos.models.user import User
from kophinos.models.user_authentication_detail import UserAuthenticationDetail
from kophinos.models.wallet import Wallet
from kophinos.services.transfer_create import TransferCreate
from kophinos.services.transaction_create import TransactionCreate
from kophinos.services.user_create import UserCreate
from kophinos.services.wallet_create import WalletCreate

@pytest.mark.usefixtures('database')
class TestTransactionCreate:
    sender_details = {
        'first_name': 'sender',
        'last_name': 'test',
        'email': 'sender.test@reallycool.test',
        'password': 'somepswd',
    }

    receiver_email = 'receiver.test@reallycool.test'

    receiver_details = {
        'first_name': 'receiver',
        'last_name': 'test',
        'email': receiver_email,
        'password': 'somepswd',
    }

    currency = Currency.SGD

    wallet_details = {
        'currency': currency.name
    }

    transfer_amount = 100000

    transfer_details = {
        'receiver_email':  receiver_email,
        'currency': currency.name,
        'amount_cents': transfer_amount
    }

    def test_generates_transfer_modifying_wallets_when_all_details_correct(self, database):
        sender_authentication_details = UserCreate.call(self.sender_details)
        sender = User.find_by_id(sender_authentication_details.user_id)
        sender_authentication_details.generate_token()
        sender_wallet = WalletCreate.call(sender_authentication_details.token, self.wallet_details)

        receiver_authentication_details = UserCreate.call(self.receiver_details)
        receiver = User.find_by_id(receiver_authentication_details.user_id)
        receiver_authentication_details.generate_token()
        receiver_wallet = WalletCreate.call(receiver_authentication_details.token, self.wallet_details)
        TransactionCreate.call(sender_wallet, { 'amount_cents': self.transfer_amount, 'type': TransactionType.CREDIT.name })

        assert sender_wallet.balance_cents == self.transfer_amount
        assert receiver_wallet.balance_cents == 0

        TransferCreate.call(sender, sender_wallet, self.transfer_details)

        assert Transaction.query.count() == 3
        assert sender_wallet.balance_cents == 0
        assert receiver_wallet.balance_cents == self.transfer_amount

        sender_transactions =[ (transaction.amount_cents, transaction.type) for transaction in Transaction.find_all_by_wallet(sender_wallet) ]

        assert sender_transactions == [
            (self.transfer_amount, TransactionType.CREDIT.name),
            (self.transfer_amount, TransactionType.DEBIT.name)
        ]

        receiver_transactions =[ (transaction.amount_cents, transaction.type) for transaction in Transaction.find_all_by_wallet(receiver_wallet) ]

        assert receiver_transactions == [
            (self.transfer_amount, TransactionType.CREDIT.name),
        ]

        assert Transfer.query.count() == 1
        transfer = Transfer.query.first()

        assert transfer.sender_user_id == sender.id
        assert transfer.receiver_user_id == receiver.id
        assert transfer.amount_cents == self.transfer_amount
        assert transfer.currency == self.currency.name


    def test_generates_transfer_modifying_wallets_when_all_details_correct_and_zero_balance(self, database):
        sender_authentication_details = UserCreate.call(self.sender_details)
        sender = User.find_by_id(sender_authentication_details.user_id)
        sender_authentication_details.generate_token()
        sender_wallet = WalletCreate.call(sender_authentication_details.token, self.wallet_details)

        receiver_authentication_details = UserCreate.call(self.receiver_details)
        receiver = User.find_by_id(receiver_authentication_details.user_id)
        receiver_authentication_details.generate_token()
        receiver_wallet = WalletCreate.call(receiver_authentication_details.token, self.wallet_details)
        assert sender_wallet.balance_cents == 0
        assert receiver_wallet.balance_cents == 0

        TransferCreate.call(sender, sender_wallet, self.transfer_details)

        assert Transaction.query.count() == 2
        assert sender_wallet.balance_cents == -self.transfer_amount
        assert receiver_wallet.balance_cents == self.transfer_amount

        sender_transactions =[ (transaction.amount_cents, transaction.type) for transaction in Transaction.find_all_by_wallet(sender_wallet) ]

        assert sender_transactions == [
            (self.transfer_amount, TransactionType.DEBIT.name)
        ]

        receiver_transactions =[ (transaction.amount_cents, transaction.type) for transaction in Transaction.find_all_by_wallet(receiver_wallet) ]

        assert receiver_transactions == [
            (self.transfer_amount, TransactionType.CREDIT.name),
        ]

        assert Transfer.query.count() == 1
        transfer = Transfer.query.first()

        assert transfer.sender_user_id == sender.id
        assert transfer.receiver_user_id == receiver.id
        assert transfer.amount_cents == self.transfer_amount
        assert transfer.currency == self.currency.name

    @pytest.mark.parametrize('invalid_details', [
        { 'amount_cents': '' },
        { 'amount_cents': 'WHAT' },
        { 'amount_cents': '100000' },
        { 'amount_cents': -100000 }
    ])
    def test_raises_errors_when_trasanction_detais_invalid_not_modifying_wallets(self, database, invalid_details):
        sender_authentication_details = UserCreate.call(self.sender_details)
        sender = User.find_by_id(sender_authentication_details.user_id)
        sender_authentication_details.generate_token()
        sender_wallet = WalletCreate.call(sender_authentication_details.token, self.wallet_details)

        receiver_authentication_details = UserCreate.call(self.receiver_details)
        receiver = User.find_by_id(receiver_authentication_details.user_id)
        receiver_authentication_details.generate_token()
        receiver_wallet = WalletCreate.call(receiver_authentication_details.token, self.wallet_details)
        assert sender_wallet.balance_cents == 0
        assert receiver_wallet.balance_cents == 0

        with pytest.raises(InvalidTransaction):
            TransferCreate.call(sender, sender_wallet, { **self.transfer_details, **invalid_details } )

        assert Transaction.query.count() == 0
        assert sender_wallet.balance_cents == 0
        assert receiver_wallet.balance_cents == 0

        assert Transaction.find_all_by_wallet(sender_wallet) == []
        assert Transaction.find_all_by_wallet(receiver_wallet) == []
        assert Transfer.query.count() == 0

    @pytest.mark.parametrize('invalid_details', [
        { 'amount_cents': None },
        { 'currency': None },
        { 'receiver_email': None }
    ])
    def test_raises_errors_when_mandatory_fields_missing_not_modifying_wallets(self, database, invalid_details):
        sender_authentication_details = UserCreate.call(self.sender_details)
        sender = User.find_by_id(sender_authentication_details.user_id)
        sender_authentication_details.generate_token()
        sender_wallet = WalletCreate.call(sender_authentication_details.token, self.wallet_details)

        receiver_authentication_details = UserCreate.call(self.receiver_details)
        receiver = User.find_by_id(receiver_authentication_details.user_id)
        receiver_authentication_details.generate_token()
        receiver_wallet = WalletCreate.call(receiver_authentication_details.token, self.wallet_details)
        assert sender_wallet.balance_cents == 0
        assert receiver_wallet.balance_cents == 0

        with pytest.raises(InvalidTransfer):
            TransferCreate.call(sender, sender_wallet, { **self.transfer_details, **invalid_details } )

        assert Transaction.query.count() == 0
        assert sender_wallet.balance_cents == 0
        assert receiver_wallet.balance_cents == 0

        assert Transaction.find_all_by_wallet(sender_wallet) == []
        assert Transaction.find_all_by_wallet(receiver_wallet) == []
        assert Transfer.query.count() == 0

    def test_raises_errors_when_receiver_does_not_exists_not_modifying_wallets(self, database):
        sender_authentication_details = UserCreate.call(self.sender_details)
        sender = User.find_by_id(sender_authentication_details.user_id)
        sender_authentication_details.generate_token()
        sender_wallet = WalletCreate.call(sender_authentication_details.token, self.wallet_details)

        assert sender_wallet.balance_cents == 0

        with pytest.raises(InvalidUser):
            TransferCreate.call(sender, sender_wallet, self.transfer_details )

        assert Transaction.query.count() == 0
        assert sender_wallet.balance_cents == 0

        assert Transaction.find_all_by_wallet(sender_wallet) == []
        assert Transfer.query.count() == 0

    def test_raises_errors_when_receiver_does_have_wallet_not_modifying_wallets(self, database):
        sender_authentication_details = UserCreate.call(self.sender_details)
        sender = User.find_by_id(sender_authentication_details.user_id)
        sender_authentication_details.generate_token()
        sender_wallet = WalletCreate.call(sender_authentication_details.token, self.wallet_details)

        receiver_authentication_details = UserCreate.call(self.receiver_details)
        receiver = User.find_by_id(receiver_authentication_details.user_id)

        assert sender_wallet.balance_cents == 0

        with pytest.raises(InvalidWallet):
            TransferCreate.call(sender, sender_wallet, self.transfer_details )

        assert Transaction.query.count() == 0
        assert sender_wallet.balance_cents == 0

        assert Transaction.find_all_by_wallet(sender_wallet) == []
        assert Transfer.query.count() == 0
