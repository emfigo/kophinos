from http import HTTPStatus
import pytest

from kophinos.models.currency import Currency
from kophinos.models.wallet import Wallet
from kophinos.services.user_create import UserCreate

@pytest.mark.usefixtures('testapp', 'database')
class TestBlueprintWallets:
    user_details = {
        'first_name': 'test',
        'last_name': 'Test',
        'email': 'test.test@reallycool.test',
        'password': 'Som3r3allyD1ff1cultPa$$word!'
    }

    wallet_details = {
        'currency': Currency.SGD.name
    }

    def test_creates_wallet_when_all_details_are_valid(self, testapp, database):
        client = testapp.test_client()

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        response = client.post('/wallets', headers=headers, json=self.wallet_details)

        assert Wallet.query.count() == 1
        wallet = Wallet.query.first()

        wallet_dict = wallet.as_dict()
        wallet_dict['id'] = str(wallet_dict['id'])

        assert response.status_code == HTTPStatus.CREATED
        assert response.json == wallet_dict

    @pytest.mark.parametrize('invalid_detail', [
        {'currency': None},
        {'currency': ''},
        {'currency': 'NONEXISTING'}
    ])
    def test_returns_an_error_when_missing_mandatory_field(self, testapp, database, invalid_detail):
        client = testapp.test_client()

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        response = client.post('/wallets', headers=headers, json={ **self.wallet_details, **invalid_detail } )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json == 'Invalid currency. Please select specify another one.'

    def test_returns_unauthorized_when_not_auhtenticated(self, testapp, database):
        client = testapp.test_client()

        response = client.post('/wallets', json=self.wallet_details)

        assert Wallet.query.count() == 0
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json == 'unauthorized'

    def test_returns_expected_wallet_when_authenticated_and_valid_details(self, testapp, database):
        client = testapp.test_client()

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        client.post('/wallets', headers=headers, json=self.wallet_details)

        wallet = Wallet.query.first()

        wallet_dict = wallet.as_dict()
        wallet_dict['id'] = str(wallet_dict['id'])

        response = client.get(f"/wallets/{self.wallet_details['currency']}", headers=headers)

        assert response.status_code == HTTPStatus.OK
        assert response.json == wallet_dict

    def test_returns_error_message_when_authenticated_and_non_existing_wallet(self, testapp, database):
        client = testapp.test_client()

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        response = client.get(f"/wallets/{self.wallet_details['currency']}", headers=headers)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json == 'Invalid account. Account does not exist for user.'

    @pytest.mark.parametrize('invalid_detail', [
        {'currency': None},
        {'currency': 'NONEXISTING'}
    ])
    def test_returns_error_message_when_authenticated_and_invalid_details(self, testapp, database, invalid_detail):
        client = testapp.test_client()

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        response = client.get(f"/wallets/{invalid_detail['currency']}", headers=headers)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json == 'Invalid currency. Please select specify another one.'

    def test_returns_error_message_when_not_authenticated(self, testapp, database):
        client = testapp.test_client()

        response = client.get(f"/wallets/{self.wallet_details['currency']}")

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json == 'unauthorized'

