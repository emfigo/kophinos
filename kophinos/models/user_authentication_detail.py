from datetime import datetime
import uuid
from sqlalchemy import Column, String, ForeignKey
import sqlalchemy.dialects.postgresql as postgresql
from sqlalchemy.exc import IntegrityError

from kophinos import db
from kophinos.exceptions import InvalidUserAuthenticationDetails

class UserAuthenticationDetail(db.Model):
    __tablename__ = 'user_authentication_details'
    id = Column(postgresql.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4)
    user_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(500), nullable=False, unique=True)
    created_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    @classmethod
    def create(kls, user, email: str, password: str):

        user_authentication_detail = UserAuthenticationDetail( email=email, password=password, user_id=user.id)

        try:
            db.session.add(user_authentication_detail)
            db.session.commit()
        except IntegrityError as err:
            error_info = err.orig.args[0]

            raise InvalidUserAuthenticationDetails(error_info)
        finally:
            db.session.rollback()


        return user_authentication_detail

    @classmethod
    def find_by_email_and_password(kls, email: str, password: str):
        return kls.query.filter_by(
            email = email,
            password = password
        ).first()

    @classmethod
    def find_by_id(kls, id: uuid.UUID):
        return kls.query.filter_by(
            id = id
        ).first()
