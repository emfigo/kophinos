from datetime import datetime
import flask_login
import uuid
from sqlalchemy import Column, String, ForeignKey
import sqlalchemy.dialects.postgresql as postgresql
from sqlalchemy.exc import IntegrityError

from kophinos import db, login_manager, hashing
from kophinos.exceptions import InvalidUserAuthenticationDetails
from kophinos.tokenizer import Tokenizer

class UserAuthenticationDetail(db.Model, flask_login.UserMixin):
    __tablename__ = 'user_authentication_details'
    id = Column(postgresql.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4)
    user_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(500), nullable=False)
    token = Column(String(250), unique=True)
    created_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    @classmethod
    def create(kls, user, email: str, password: str):

        user_authentication_detail = UserAuthenticationDetail(
            email = email,
            password = hashing.hash(password),
            user_id = user.id
        )

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
            password = hashing.hash(password)
        ).first()

    @classmethod
    def find_by_id(kls, id: uuid.UUID):
        return kls.query.filter_by(
            id = id
        ).first()

    @classmethod
    def find_by_token(kls, token: str):
        user_authentication_details = None

        if token is not None and token != '':
            user_authentication_details = kls.query.filter_by(
                token = token
            ).first()

        return user_authentication_details

    @login_manager.user_loader
    def user_loader(token):
        """
        This is used for flask login
        """
        user_authentication_detail = UserAuthenticationDetail.find_by_token(token)

        return user_authentication_detail

    @login_manager.request_loader
    def request_loader(request):
        """
        This is used for flask login
        """
        token = None
        headers = request.headers

        if headers.get('Authorization'):
            token = headers['Authorization'].split()[-1]

        user_authentication_detail = UserAuthenticationDetail.find_by_token(token)

        if user_authentication_detail is not None:
            user_authentication_detail.is_authenticated = user_authentication_detail is not None

        return user_authentication_detail

    def get_id(self):
        """
        This is used for flask login
        """
        return self.token

    def generate_token(self):
        self.token = Tokenizer.random_token()
        self.updated_at = datetime.utcnow()

        db.session.add(self)
        db.session.commit()

    def clear_token(self):
        self.token = None
        self.updated_at = datetime.utcnow()

        db.session.add(self)
        db.session.commit()

    def as_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'updated_at': int(self.updated_at.timestamp()),
            'created_at': int(self.created_at.timestamp())
        }
