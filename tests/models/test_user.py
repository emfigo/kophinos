import pytest
import uuid

from kophinos.models.user import User

@pytest.mark.usefixtures('database')
class TestUser:
    first_name = 'Test'
    last_name = 'Test'
    email = 'test.test@reallycool.test'

    def test_creates_user_with_all_expected_attributes(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        assert User.query.filter_by(
            email = self.email
        ).first().id == user.id

        assert user.id is not None

        assert User.query.filter_by(
            email = self.email
        ).first().created_at == user.created_at
        assert user.created_at is not None

        assert User.query.filter_by(
            email = self.email
        ).first().updated_at == user.updated_at
        assert user.updated_at is not None

        assert user.first_name == self.first_name
        assert user.last_name == self.last_name
        assert user.email == self.email

    def test_converts_user_to_dict(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        expected_dict = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'updated_at': int(user.created_at.timestamp()),
            'created_at': int(user.created_at.timestamp())
        }

        assert user.as_dict() == expected_dict

    def test_finds_by_email_returns_the_expected_user(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        assert User.query.count() == 1
        assert User.find_by_email('nonexistingemail@something.test') is None
        assert User.find_by_email(self.email) == user

    def test_finds_by_id_returns_the_expected_user(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        assert User.query.count() == 1
        assert User.find_by_id(uuid.uuid4()) is None
        assert User.find_by_id(user.id) == user
