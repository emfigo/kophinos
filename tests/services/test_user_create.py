import pytest

from kophinos.exceptions import InvalidUser, InvalidUserAuthenticationDetails
from kophinos import hashing
from kophinos.services.user_create import UserCreate
from kophinos.models.user import User
from kophinos.models.user_authentication_detail import UserAuthenticationDetail

@pytest.mark.usefixtures('database')
class TestUserCreate:
    first_name = 'test'
    last_name = 'test'
    email = 'test.test@reallycool.test'
    password = 'somepswd'

    def test_when_user_does_not_exists_and_all_details_correct_creates_user(self, database):
        assert User.find_by_email(self.email) is None
        assert UserAuthenticationDetail.find_by_email_and_password(self.email, self.password) is None

        user_authentication_details = UserCreate.call(self.first_name, self.last_name, self.email, self.password)

        assert user_authentication_details is not None
        assert UserAuthenticationDetail.find_by_email_and_password(self.email, self.password) == user_authentication_details
        assert User.find_by_email(self.email) == User.find_by_id(user_authentication_details.user_id)

    def test_when_user_exists_and_all_details_correct_return_existing_user(self, database):
        user_authentication_details = UserCreate.call(self.first_name, self.last_name, self.email, self.password)
        user = User.find_by_email(self.email)

        assert user is not None
        assert user.id == user_authentication_details.user_id

        before_count_user = User.query.count()
        before_count_user_auth_details = UserAuthenticationDetail.query.count()

        new_user_authentication_details = UserCreate.call(self.first_name, self.last_name, self.email, self.password)

        assert User.query.count() == before_count_user
        assert UserAuthenticationDetail.query.count() == before_count_user_auth_details
        assert new_user_authentication_details == user_authentication_details

    @pytest.mark.parametrize('invalid_detail', [
        {'first_name': None},
        { 'last_name': None },
        { 'email': None }
    ])
    def test_does_not_create_user_when_invalid_user_details(self, database, invalid_detail):
        before_count_user = User.query.count()
        before_count_user_auth_details = UserAuthenticationDetail.query.count()

        with pytest.raises(InvalidUser):
            user_authentication_details = UserCreate.call(
                **{
                    **{
                        'first_name': self.first_name,
                        'last_name': self.last_name,
                        'email': self.email,
                        'pswd': self.password
                    },
                    **invalid_detail
                }
            )

        assert User.query.count() == before_count_user
        assert UserAuthenticationDetail.query.count() == before_count_user_auth_details

    @pytest.mark.parametrize('invalid_detail', [
        { 'pswd': None }
    ])
    def test_does_not_create_user_when_invalid_user_authentication_detail(self, database, invalid_detail):
        before_count_user_auth_details = UserAuthenticationDetail.query.count()

        with pytest.raises(InvalidUserAuthenticationDetails):
            user_authentication_details = UserCreate.call(
                **{
                    **{
                        'first_name': self.first_name,
                        'last_name': self.last_name,
                        'email': self.email,
                        'pswd': self.password
                    },
                    **invalid_detail
                }
            )

        assert UserAuthenticationDetail.query.count() == before_count_user_auth_details
