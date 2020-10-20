from http import HTTPStatus
import pytest

from kophinos.models.user import User
from kophinos.services.user_create import UserCreate

@pytest.mark.usefixtures('testapp', 'database')
class TestBlueprintPaymentMethods:
    user_details = {
        'first_name': 'test',
        'last_name': 'Test',
        'email': 'test.test@reallycool.test',
        'password': 'Som3r3allyD1ff1cultPa$$word!'
    }

    def test_creates_sale_when_all_details_are_valid(self, testapp, database):
        client = testapp.test_client()

        response = client.post('/users', json=self.user_details)

        user = User.find_by_email(self.user_details['email'])

        assert response.status_code == HTTPStatus.CREATED
        assert response.json == str(user.id)

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
