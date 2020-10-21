from datetime import datetime
import uuid
from sqlalchemy import Column, String, ForeignKey, BigInteger
import sqlalchemy.dialects.postgresql as postgresql
from sqlalchemy.exc import IntegrityError

from kophinos import db
from kophinos.exceptions import InvalidUser, InvalidCurrency
from kophinos.models.currency import Currency

class Wallet(db.Model):
    __tablename__ = 'wallets'
    id = Column(postgresql.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4)
    user_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    balance_cents = Column(BigInteger, nullable=False, default=0)
    currency = Column(String(15), nullable=False)
    created_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    @classmethod
    def create(kls, user, currency: Currency):
        wallet = Wallet(
            user_id = user.id,
            currency = currency.name
        )

        try:
            db.session.add(wallet)
            db.session.commit()
        except IntegrityError as err:
            error_info = err.orig.args[0]

            if 'currency' in error_info:
                raise InvalidCurrency
            elif 'user_id' in error_info:
                raise InvalidUser
            else:
                raise err

        finally:
            db.session.rollback()

        return wallet
