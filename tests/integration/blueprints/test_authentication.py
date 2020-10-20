from http import HTTPStatus
import pytest

from kophinos.models.user import User
from kophinos.services.user_create import UserCreate

@pytest.mark.usefixtures('testapp', 'database')
class TestBlueprintAuthentication:
    email = 'test.test@reallycool.test'
    pwd = 'Som3r3allyD1ff1cultPa$$word!'

    user_details = {
        'first_name': 'test',
        'last_name': 'Test',
        'email': email,
        'password': pwd
    }

    user_login_details = {
        'email': email,
        'password': pwd
    }

    def test_login_when_all_details_are_valid(self, testapp, database):
        client = testapp.test_client()
        user_authentication_details = UserCreate.call(self.user_details)

        response = client.post('/login', json=self.user_login_details)


        assert response.status_code == HTTPStatus.CREATED
        assert response.json == str(user_authentication_details.token)

    def test_login_when_details_are_incorrect(self, testapp, database):
        client = testapp.test_client()
        user_authentication_details = UserCreate.call(self.user_details)

        response = client.post('/login', json={
            'email': self.email,
            'password': 'somethingwring'
        })

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json == 'The user details are incorrect. Please try new ones.'

    def test_logout_when_all_details_are_valid(self, testapp, database):
        client = testapp.test_client()
        user_authentication_details = UserCreate.call(self.user_details)
        user_authentication_details.generate_token()

        headers = {
            'Authorization': f'Basic {user_authentication_details.token}'
        }

        response = client.get('/logout', headers=headers)


        assert response.status_code == HTTPStatus.OK
        assert response.json == 'Logged out'

    def test_logout_when_details_are_incorrect(self, testapp, database):
        client = testapp.test_client()
        user_authentication_details = UserCreate.call(self.user_details)
        user_authentication_details.generate_token()

        headers = {
            'Authorization': 'Basic Nonexistingtoken'
        }

        response = client.get('/logout', headers=headers)


        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json == 'Invalid user'
