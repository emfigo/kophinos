from datetime import datetime
import uuid
from sqlalchemy import Column, String, ForeignKey
import sqlalchemy.dialects.postgresql as postgresql
from sqlalchemy.exc import IntegrityError

from kophinos import db
from kophinos.exceptions import InvalidUser

class User(db.Model):
    __tablename__ = 'users'
    id = Column(postgresql.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4)
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    created_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    @classmethod
    def create(kls, first_name: str, last_name: str, email: str):

        user = User( first_name=first_name, last_name=last_name, email=email)

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as err:
            error_info = err.orig.args[0]

            raise InvalidUser(error_info)
        finally:
            db.session.rollback()

        return user

    @classmethod
    def find_by_email(kls, email: str):
        return kls.query.filter_by(
            email = email
        ).first()

    @classmethod
    def find_by_id(kls, id: uuid.UUID):
        return kls.query.filter_by(
            id = id
        ).first()

    def as_dict(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'updated_at': int(self.created_at.timestamp()),
            'created_at': int(self.created_at.timestamp())
        }

