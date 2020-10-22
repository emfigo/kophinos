from http import HTTPStatus
import pytest

from kophinos.models.currency import Currency
from kophinos.models.transfer import Transfer
from kophinos.models.wallet import Wallet
from kophinos.models.transaction import Transaction
from kophinos.services.user_create import UserCreate

@pytest.mark.usefixtures('testapp', 'database')
class TestBlueprintWallets:
    user_details = {
        'first_name': 'test',
        'last_name': 'Test',
        'email': 'test.test@reallycool.test',
        'password': 'Som3r3allyD1ff1cultPa$$word!'
    }

    receiver_details = {
        'first_name': 'test2',
        'last_name': 'Test',
        'email': 'test2.test@reallycool.test',
        'password': 'Som3r3allyD1ff1cultPa$$word!'
    }

    wallet_details = {
        'currency': Currency.SGD.name
    }

    transaction_details = {
        'amount_cents': 100000,
        'type': 'CREDIT'
    }

    transfer_details = {
        "receiver_email": "test2.test@reallycool.test",
        "amount_cents": 100000,
        "currency": Currency.SGD.name
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

    def test_creates_expected_wallet_transaction_when_authenticated_and_valid_details(self, testapp, database):
        client = testapp.test_client()

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        client.post('/wallets', headers=headers, json=self.wallet_details)

        response = client.post(f"/wallets/{self.wallet_details['currency']}/transactions", headers=headers, json=self.transaction_details)

        assert Transaction.query.count() == 1

        wallet = Wallet.query.first()
        transaction = Transaction.query.first()
        transaction_dict = transaction.as_dict()
        transaction_dict['id'] = str(transaction_dict['id'])

        assert response.status_code == HTTPStatus.CREATED
        assert response.json == transaction_dict

    def test_returns_error_message_when_authenticated_and_non_existing_wallet_transactions(self, testapp, database):
        client = testapp.test_client()

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        response = client.post(f"/wallets/{self.wallet_details['currency']}/transactions", headers=headers, json=self.transaction_details)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json == 'Invalid account. Account does not exist for user.'

    @pytest.mark.parametrize('invalid_detail', [
        {'amount_cents': None },
        {'amount_cents': '1000000' },
        {'amount_cents': 'hello' },
        {'type': None },
        {'type': 'NONEXISTING' }
    ])
    def test_returns_error_message_when_authenticated_and_invalid_transaction_details(self, testapp, database, invalid_detail):
        client = testapp.test_client()

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        client.post('/wallets', headers=headers, json=self.wallet_details)

        response = client.post(f"/wallets/{self.wallet_details['currency']}/transactions", headers=headers, json={ **self.transaction_details, **invalid_detail })

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json == 'Invalid transaction. Please change transaction details.'

    def test_returns_error_message_transactions_when_not_authenticated(self, testapp, database):
        client = testapp.test_client()

        response = client.post(f"/wallets/{self.wallet_details['currency']}/transactions", json=self.transaction_details)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json == 'unauthorized'

    def test_returns_expected_wallet_transaction_when_authenticated_and_valid_details(self, testapp, database):
        client = testapp.test_client()

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        client.post('/wallets', headers=headers, json=self.wallet_details)

        response = client.get(f"/wallets/{self.wallet_details['currency']}/transactions", headers=headers)
        assert response.status_code == HTTPStatus.OK
        assert response.json == []

        client.post(f"/wallets/{self.wallet_details['currency']}/transactions", headers=headers, json=self.transaction_details)

        response = client.get(f"/wallets/{self.wallet_details['currency']}/transactions", headers=headers)
        assert Transaction.query.count() == 1

        wallet = Wallet.query.first()
        transaction = Transaction.query.first()
        transaction_dict = transaction.as_dict()
        transaction_dict['id'] = str(transaction_dict['id'])

        assert response.status_code == HTTPStatus.OK
        assert response.json == [transaction_dict]

    def test_get_returns_error_message_when_authenticated_and_non_existing_wallet_transactions(self, testapp, database):
        client = testapp.test_client()

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        response = client.get(f"/wallets/{self.wallet_details['currency']}/transactions", headers=headers)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json == 'Invalid account. Account does not exist for user.'

    def test_returns_error_message_get_transactions_when_not_authenticated(self, testapp, database):
        client = testapp.test_client()

        response = client.get(f"/wallets/{self.wallet_details['currency']}/transactions")

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json == 'unauthorized'

    def test_creates_expected_wallet_transfer_when_authenticated_and_valid_details(self, testapp, database):
        client = testapp.test_client()

        client.post('/users', json=self.receiver_details)
        response = client.post('/login', json=self.receiver_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        client.post('/wallets', headers=headers, json=self.wallet_details)

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        response = client.post('/wallets', headers=headers, json=self.wallet_details)

        wallet = Wallet.query.filter_by(id = response.json['id']).first()

        response = client.post(f"/wallets/{self.wallet_details['currency']}/transfers", headers=headers, json=self.transfer_details)

        assert Transfer.query.count() == 1

        wallet = Wallet.query.filter_by(id = wallet.id).first()
        wallet_dict = wallet.as_dict()
        wallet_dict['id'] = str(wallet_dict['id'])

        assert response.status_code == HTTPStatus.CREATED
        assert response.json == wallet_dict

    def test_returns_error_message_when_authenticated_and_non_existing_wallet_transfer(self, testapp, database):
        client = testapp.test_client()

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        response = client.post(f"/wallets/{self.wallet_details['currency']}/transfers", headers=headers, json=self.transfer_details)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json == 'Invalid account. Account does not exist for user.'

    @pytest.mark.parametrize('invalid_detail', [
        {'amount_cents': '1000000' },
        {'amount_cents': -1000000 },
        {'amount_cents': 'hello' }
    ])
    def test_returns_error_message_when_authenticated_and_invalid_transfer_details(self, testapp, database, invalid_detail):
        client = testapp.test_client()

        client.post('/users', json=self.receiver_details)
        response = client.post('/login', json=self.receiver_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        client.post('/wallets', headers=headers, json=self.wallet_details)

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        client.post('/wallets', headers=headers, json=self.wallet_details)

        response = client.post(f"/wallets/{self.wallet_details['currency']}/transfers", headers=headers, json={ **self.transfer_details, **invalid_detail} )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json == 'Invalid transaction. Please change transaction details.'

    @pytest.mark.parametrize('invalid_detail', [
        {'amount_cents': None },
        {'receiver_email': None },
        {'currency': None }
    ])
    def test_returns_error_message_when_authenticated_and_missing_mandatory_details(self, testapp, database, invalid_detail):
        client = testapp.test_client()

        client.post('/users', json=self.receiver_details)
        response = client.post('/login', json=self.receiver_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        client.post('/wallets', headers=headers, json=self.wallet_details)

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        client.post('/wallets', headers=headers, json=self.wallet_details)

        response = client.post(f"/wallets/{self.wallet_details['currency']}/transfers", headers=headers, json={ **self.transfer_details, **invalid_detail} )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json == 'Invalid transfer. Please change transfer details.'

    @pytest.mark.parametrize('invalid_detail', [
        {'receiver_email': 'nonexisting_email@email.test' }
    ])
    def test_returns_error_message_when_authenticated_and_invalid_receiver(self, testapp, database, invalid_detail):
        client = testapp.test_client()

        client.post('/users', json=self.receiver_details)
        response = client.post('/login', json=self.receiver_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        client.post('/wallets', headers=headers, json=self.wallet_details)

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        client.post('/wallets', headers=headers, json=self.wallet_details)

        response = client.post(f"/wallets/{self.wallet_details['currency']}/transfers", headers=headers, json={ **self.transfer_details, **invalid_detail} )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json == 'Invalid receiver. Please specify a valid receiver email.'

    def test_returns_error_message_when_authenticated_and_invalid_receiver_wallet(self, testapp, database):
        client = testapp.test_client()

        client.post('/users', json=self.receiver_details)
        response = client.post('/login', json=self.receiver_details)

        client.post('/users', json=self.user_details)
        response = client.post('/login', json=self.user_details)

        headers = {
            'Authorization': f"Basic {response.json}"
        }

        client.post('/wallets', headers=headers, json=self.wallet_details)

        response = client.post(f"/wallets/{self.wallet_details['currency']}/transfers", headers=headers, json=self.transfer_details )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json == "Invalid receiver wallet. Receiver can't accept transfer with specified currency."

    def test_returns_error_message_transfer_when_not_authenticated(self, testapp, database):
        client = testapp.test_client()

        response = client.post(f"/wallets/{self.wallet_details['currency']}/transfers", json=self.transfer_details)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json == 'unauthorized'

