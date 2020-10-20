import pytest

from kophinos.exceptions import InvalidUser, InvalidUserAuthenticationDetails
from kophinos import hashing
from kophinos.services.user_create import UserCreate
from kophinos.models.user import User
from kophinos.models.user_authentication_detail import UserAuthenticationDetail

@pytest.mark.usefixtures('database')
class TestUserCreate:
    details = {
        'first_name': 'test',
        'last_name': 'test',
        'email': 'test.test@reallycool.test',
        'password': 'somepswd'
    }

    def test_when_user_does_not_exists_and_all_details_correct_creates_user(self, database):
        assert User.find_by_email(self.details['email']) is None
        assert UserAuthenticationDetail.find_by_email_and_password(self.details['email'], self.details['password']) is None

        user_authentication_details = UserCreate.call(self.details)

        assert user_authentication_details is not None
        assert UserAuthenticationDetail.find_by_email_and_password(self.details['email'], self.details['password']) == user_authentication_details
        assert User.find_by_email(self.details['email']) == User.find_by_id(user_authentication_details.user_id)

    def test_when_user_does_not_exists_and_all_details_correct_with_extra_attrs_creates_user(self, database):
        assert User.find_by_email(self.details['email']) is None
        assert UserAuthenticationDetail.find_by_email_and_password(self.details['email'], self.details['password']) is None

        user_authentication_details = UserCreate.call(
            { **self.details, 'someextrafield': 'extrainfo' }
        )

        assert user_authentication_details is not None
        assert UserAuthenticationDetail.find_by_email_and_password(self.details['email'], self.details['password']) == user_authentication_details
        assert User.find_by_email(self.details['email']) == User.find_by_id(user_authentication_details.user_id)

    def test_when_user_exists_and_all_details_correct_return_existing_user(self, database):
        user_authentication_details = UserCreate.call(self.details)
        user = User.find_by_email(self.details['email'])

        assert user is not None
        assert user.id == user_authentication_details.user_id

        before_count_user = User.query.count()
        before_count_user_auth_details = UserAuthenticationDetail.query.count()

        new_user_authentication_details = UserCreate.call(self.details)

        assert User.query.count() == before_count_user
        assert UserAuthenticationDetail.query.count() == before_count_user_auth_details
        assert new_user_authentication_details == user_authentication_details

    @pytest.mark.parametrize('invalid_detail', [
        {'first_name': None},
        { 'last_name': None },
        { 'email': None },
        { 'password': None }
    ])
    def test_does_not_create_user_when_invalid_user_details(self, database, invalid_detail):
        before_count_user = User.query.count()
        before_count_user_auth_details = UserAuthenticationDetail.query.count()

        with pytest.raises(InvalidUser):
            user_authentication_details = UserCreate.call(
                { **self.details, **invalid_detail }
            )

        assert User.query.count() == before_count_user
        assert UserAuthenticationDetail.query.count() == before_count_user_auth_details
