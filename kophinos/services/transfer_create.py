from kophinos.exceptions import InvalidTransfer, InvalidUser, InvalidWallet
from kophinos.models.currency import Currency
from kophinos.models.transfer import Transfer
from kophinos.models.transaction import TransactionType
from kophinos.models.user import User
from kophinos.models.wallet import Wallet
from kophinos.services.transaction_create import TransactionCreate

class TransferCreate:
    MANDATORY_FIELDS = [
        'receiver_email',
        'currency',
        'amount_cents'
    ]

    def __init__(self, sender, wallet: Wallet, details: dict):
        self.sender = sender
        self.sender_wallet = wallet
        self.receiver = self._get_receiver(details['receiver_email'])
        self.currency = Currency.get(details['currency'])
        self.amount_cents = details['amount_cents']

    def _get_receiver(self, email: str):
        user = User.find_by_email(email)

        if user is None:
            raise InvalidUser

        return user

    def get_receiver_wallet(self):
        wallet = Wallet.find_by_user_and_currency(self.receiver, self.currency)

        if wallet is None:
            raise InvalidWallet

        return wallet

    def generate_transfer(self, receiver_wallet):
        TransactionCreate.call(
            self.sender_wallet,
            { 'amount_cents': self.amount_cents, 'type': TransactionType.DEBIT.name }
        )

        TransactionCreate.call(
            receiver_wallet,
            { 'amount_cents': self.amount_cents, 'type': TransactionType.CREDIT.name }
        )

        Transfer.create(self.sender, self.receiver, self.amount_cents, self.currency)

        return self.sender_wallet

    @classmethod
    def call(kls, sender, wallet: str, details: dict):
        service = kls(sender, wallet, kls._slice(details))
        receiver_wallet = service.get_receiver_wallet()

        return service.generate_transfer(receiver_wallet)

    @classmethod
    def _slice(kls, details: dict) -> dict:
        sliced_details = {}

        for k in kls.MANDATORY_FIELDS:
            if details.get(k) is not None:
                sliced_details[k] = details[k]
            else:
                raise InvalidTransfer

        return sliced_details

