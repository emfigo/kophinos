from kophinos.exceptions import InvalidTransaction
from kophinos.models.transaction import Transaction, TransactionType
from kophinos.models.wallet import Wallet

class TransactionCreate:
    MANDATORY_FIELDS = [
        'amount_cents',
        'type'
    ]

    def __init__(self, wallet: Wallet, details: dict):
        self.wallet = wallet
        self.amount_cents = details['amount_cents']
        self.type = TransactionType.get(details['type'])

    def create_transaction(self):
        transaction = Transaction.create(self.wallet, self.amount_cents, self.type)

        self.wallet.add_operation(self.amount_cents, self.type)

        return transaction

    @classmethod
    def call(kls, wallet: str, details: dict):
        service = kls(wallet, kls._slice(details))

        return service.create_transaction()

    @classmethod
    def _slice(kls, details: dict) -> dict:
        sliced_details = {}

        for k in kls.MANDATORY_FIELDS:
            if details.get(k) is not None:
                sliced_details[k] = details[k]
            else:
                raise InvalidTransaction

        return sliced_details

