from freezegun import freeze_time
import pytest
import uuid

from kophinos import hashing
from kophinos.exceptions import InvalidUserAuthenticationDetails
from kophinos.models.user import User
from kophinos.models.user_authentication_detail import UserAuthenticationDetail
from kophinos.tokenizer import Tokenizer

@pytest.mark.usefixtures('database')
class TestUserAuthenticationDetail:
    first_name = 'test'
    last_name = 'test'
    email = 'test.test@reallycool.test'
    password = 'someversionpswd'

    def test_creates_user_authentication_details_with_all_expected_attributes(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        user_authentication_detail = UserAuthenticationDetail.create(
            user = user,
            email = self.email,
            password = self.password
        )

        assert UserAuthenticationDetail.query.filter_by(
            email = self.email
        ).first().id == user_authentication_detail.id

        assert user_authentication_detail.id is not None

        assert UserAuthenticationDetail.query.filter_by(
            email = self.email
        ).first().created_at == user_authentication_detail.created_at
        assert user_authentication_detail.created_at is not None

        assert UserAuthenticationDetail.query.filter_by(
            email = self.email
        ).first().updated_at == user_authentication_detail.updated_at
        assert user_authentication_detail.updated_at is not None

        assert user_authentication_detail.email == self.email
        assert user_authentication_detail.password != self.password
        assert user_authentication_detail.password == hashing.hash(self.password)
        assert user_authentication_detail.user_id == user.id

    def test_does_not_create_user_authentication_details_with_non_existing_user(self, database):
        user = User(
            id = uuid.uuid4(),
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        prev_count = UserAuthenticationDetail.query.count()

        with pytest.raises(InvalidUserAuthenticationDetails):
            user_authentication_detail = UserAuthenticationDetail.create(
                user = user,
                email = self.email,
                password = self.password
            )

        assert UserAuthenticationDetail.query.count() == prev_count

    def test_does_not_create_user_authentication_details_with_invalid_password(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        prev_count = UserAuthenticationDetail.query.count()

        with pytest.raises(InvalidUserAuthenticationDetails):
            user_authentication_detail = UserAuthenticationDetail.create(
                user = user,
                email = self.email,
                password = None
            )

        assert UserAuthenticationDetail.query.count() == prev_count

    def test_does_not_create_user_authentication_details_with_invalid_email(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        prev_count = UserAuthenticationDetail.query.count()

        with pytest.raises(InvalidUserAuthenticationDetails):
            user_authentication_detail = UserAuthenticationDetail.create(
                user = user,
                email = None,
                password = self.password
            )

        assert UserAuthenticationDetail.query.count() == prev_count

    def test_does_not_create_user_authentication_details_with_duplicated_email_and_password(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        user_authentication_detail = UserAuthenticationDetail.create(
            user = user,
            email = self.email,
            password = self.password
        )

        prev_count = UserAuthenticationDetail.query.count()

        with pytest.raises(InvalidUserAuthenticationDetails):
            user_authentication_detail = UserAuthenticationDetail.create(
                user = user,
                email = self.email,
                password = self.password
            )

        assert UserAuthenticationDetail.query.count() == prev_count

    def test_finds_by_email_and_password_returns_the_expected_user_authentication_detail(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        user_authentication_detail = UserAuthenticationDetail.create(
            user = user,
            email = self.email,
            password = self.password
        )

        assert UserAuthenticationDetail.query.count() == 1
        assert UserAuthenticationDetail.find_by_email_and_password(self.email, 'nonexistingpswd') is None
        assert UserAuthenticationDetail.find_by_email_and_password('nonexistingemail@email.com', self.password) is None
        assert UserAuthenticationDetail.find_by_email_and_password(self.email, self.password) == user_authentication_detail

    def test_finds_by_id_returns_the_expected_user_authentication_detail(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        user_authentication_detail = UserAuthenticationDetail.create(
            user = user,
            email = self.email,
            password = self.password
        )

        assert UserAuthenticationDetail.query.count() == 1
        assert UserAuthenticationDetail.find_by_id(uuid.uuid4()) is None
        assert UserAuthenticationDetail.find_by_id(user_authentication_detail.id) == user_authentication_detail

    def test_generate_token_for_existing_user(self, database):
        with freeze_time("2000-10-19"):
            user = User.create(
                first_name = self.first_name,
                last_name = self.last_name,
                email = self.email
            )

            user_authentication_detail = UserAuthenticationDetail.create(
                user = user,
                email = self.email,
                password = self.password
            )

        assert user_authentication_detail.token is None
        current_updated_at = user_authentication_detail.updated_at

        user_authentication_detail.generate_token()

        assert user_authentication_detail.token is not None
        assert user_authentication_detail.updated_at is not None
        assert user_authentication_detail.updated_at > current_updated_at

    def test_clear_token_for_existing_user(self, database):
        with freeze_time("2000-10-19"):
            user = User.create(
                first_name = self.first_name,
                last_name = self.last_name,
                email = self.email
            )

            user_authentication_detail = UserAuthenticationDetail.create(
                user = user,
                email = self.email,
                password = self.password
            )

            user_authentication_detail.generate_token()

            assert user_authentication_detail.token is not None
            current_updated_at = user_authentication_detail.updated_at

        user_authentication_detail.clear_token()

        assert user_authentication_detail.token is None
        assert user_authentication_detail.updated_at is not None
        assert user_authentication_detail.updated_at > current_updated_at

    def test_finds_by_token_returns_the_expected_user_authentication_detail(self, database):
        user = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email
        )

        user_authentication_detail = UserAuthenticationDetail.create(
            user = user,
            email = self.email,
            password = self.password
        )

        user2 = User.create(
            first_name = self.first_name,
            last_name = self.last_name,
            email = 'test2@test.test'
        )

        UserAuthenticationDetail.create(
            user = user2,
            email = 'test2@test.test',
            password = self.password
        )

        user_authentication_detail.generate_token()

        assert UserAuthenticationDetail.query.count() == 2
        assert UserAuthenticationDetail.find_by_token('') is None
        assert UserAuthenticationDetail.find_by_token(None) is None
        assert UserAuthenticationDetail.find_by_token(user_authentication_detail.token) == user_authentication_detail
