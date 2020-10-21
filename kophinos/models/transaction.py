from datetime import datetime
from enum import Enum, unique
import uuid
from sqlalchemy import Column, String, ForeignKey, BigInteger
import sqlalchemy.dialects.postgresql as postgresql
from sqlalchemy.exc import IntegrityError

from kophinos import db
from kophinos.exceptions import InvalidWallet, InvalidTransaction

@unique
class TransactionType(Enum):
    CREDIT = 0
    DEBIT = 1

    @classmethod
    def get(kls, name: str):
        try:
            return getattr(kls, name.upper())
        except:
            raise InvalidTransaction

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = Column(postgresql.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4)
    wallet_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('wallets.id'), nullable=False)
    amount_cents = Column(BigInteger, nullable=False, default=0)
    type = Column(String(10), nullable=False)
    created_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    @classmethod
    def create(kls, wallet, amount_cents: int, transaction_type: TransactionType):
        if type(amount_cents) is not int:
            raise InvalidTransaction

        transaction = Transaction(
            wallet_id = wallet.id,
            amount_cents = amount_cents,
            type = transaction_type.name
        )

        try:
            db.session.add(transaction)
            db.session.commit()
        except IntegrityError as err:
            raise InvalidWallet
        finally:
            db.session.rollback()

        return transaction

    @classmethod
    def find_all_by_wallet(kls, wallet):
        return kls.query.filter_by(
            wallet_id = wallet.id,
        ).all()

    def as_dict(self):
        return {
            'id': self.id,
            'amount_cents': self.amount_cents,
            'type': self.type,
            'created_at': int(self.created_at.timestamp())
        }
