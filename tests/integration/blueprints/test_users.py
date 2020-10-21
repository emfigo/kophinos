from http import HTTPStatus
import pytest

from kophinos.models.user_authentication_detail import UserAuthenticationDetail
from kophinos.services.user_create import UserCreate

@pytest.mark.usefixtures('testapp', 'database')
class TestBlueprintUsers:
    user_details = {
        'first_name': 'test',
        'last_name': 'Test',
        'email': 'test.test@reallycool.test',
        'password': 'Som3r3allyD1ff1cultPa$$word!'
    }

    def test_creates_user_when_all_details_are_valid(self, testapp, database):
        client = testapp.test_client()

        response = client.post('/users', json=self.user_details)

        user_authentication_details = UserAuthenticationDetail.find_by_email_and_password(
            self.user_details['email'],
            self.user_details['password']
        )

        assert response.status_code == HTTPStatus.CREATED
        assert response.json == {
            'id': str(user_authentication_details.id),
            'email': self.user_details['email'],
            'updated_at': int(user_authentication_details.updated_at.timestamp()),
            'created_at': int(user_authentication_details.created_at.timestamp())
        }

    @pytest.mark.parametrize('invalid_detail', [
        {'first_name': None},
        { 'last_name': None },
        { 'email': None },
        { 'password': None }
    ])
    def test_returns_an_error_when_missing_mandatory_field(self, testapp, database, invalid_detail):
        client = testapp.test_client()

        response = client.post('/users', json={**self.user_details, **invalid_detail})

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json == 'The user details are incorrect. Please try new ones.'
