from datetime import datetime
import uuid
from sqlalchemy import Column, String, ForeignKey, BigInteger
import sqlalchemy.dialects.postgresql as postgresql
from sqlalchemy.exc import IntegrityError

from kophinos import db
from kophinos.exceptions import InvalidUser
from kophinos.models.currency import Currency

class Transfer(db.Model):
    __tablename__ = 'transfers'
    id = Column(postgresql.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4)
    sender_user_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    receiver_user_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    amount_cents = Column(BigInteger, nullable=False, default=0)
    currency = Column(String(15), nullable=False)
    created_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    @classmethod
    def create(kls, sender, receiver, amount_cents: int, currency: Currency):
        transfer = Transfer(
            sender_user_id = sender.id,
            receiver_user_id = receiver.id,
            amount_cents = amount_cents,
            currency = currency.name
        )

        try:
            db.session.add(transfer)
            db.session.commit()
        except IntegrityError as err:
            raise InvalidUser
        finally:
            db.session.rollback()

        return transfer


