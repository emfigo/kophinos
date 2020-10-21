from datetime import datetime
from enum import Enum, unique
import uuid
from sqlalchemy import Column, String, ForeignKey, BigInteger
import sqlalchemy.dialects.postgresql as postgresql
from sqlalchemy.exc import IntegrityError

from kophinos import db
from kophinos.exceptions import InvalidWallet

@unique
class TransactionType(Enum):
    CREDIT = 0
    DEBIT = 1


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = Column(postgresql.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4)
    wallet_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('wallets.id'), nullable=False)
    amount_cents = Column(BigInteger, nullable=False, default=0)
    type = Column(String(10), nullable=False)
    created_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    @classmethod
    def create(kls, wallet, amount_cents: int, type: TransactionType):
        transaction = Transaction(
            wallet_id = wallet.id,
            amount_cents = amount_cents,
            type = type.name
        )

        try:
            db.session.add(transaction)
            db.session.commit()
        except IntegrityError as err:
            raise InvalidWallet
        finally:
            db.session.rollback()

        return transaction

