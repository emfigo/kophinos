from flask import Blueprint, request, jsonify
import flask_login
from http import HTTPStatus

from kophinos.blueprints import helpers
from kophinos.exceptions import InvalidTransaction
from kophinos.models.user import User
from kophinos.models.transaction import Transaction
from kophinos.services.transaction_create import TransactionCreate
from kophinos.services.wallet_create import WalletCreate

wallets = Blueprint('wallets', __name__)

@wallets.route('/wallets/<currency>')
@flask_login.login_required
def get_wallet(currency):
    user_authentication_details = flask_login.current_user
    user = User.find_by_id(user_authentication_details.user_id)
    response = helpers.get_wallet(user, currency)
    response_code = HTTPStatus.OK

    if type(response) is str:
        response_code = HTTPStatus.BAD_REQUEST
    else:
        response = response.as_dict()

    return jsonify(response), response_code

@wallets.route('/wallets/<currency>/transactions')
@flask_login.login_required
def get_wallet_transactions(currency):
    user_authentication_details = flask_login.current_user
    user = User.find_by_id(user_authentication_details.user_id)
    wallet = helpers.get_wallet(user, currency)
    response_code = HTTPStatus.OK

    if type(wallet) is str:
        response_code = HTTPStatus.BAD_REQUEST
        response = wallet
    else:
        response = [ transaction.as_dict() for transaction in Transaction.find_all_by_wallet(wallet) ]

    return jsonify(response), response_code

@wallets.route('/wallets', methods=['POST'])
@flask_login.login_required
def create_wallet():
    user_authentication_details = flask_login.current_user
    details = request.json
    response = helpers.get_currency(details.get('currency'))
    response_code = HTTPStatus.CREATED

    if type(response) is str:
        response_code = HTTPStatus.BAD_REQUEST
    else:
        response = WalletCreate.call(user_authentication_details.token, details).as_dict()

    return jsonify(response), response_code

@wallets.route('/wallets/<currency>/transactions', methods=['POST'])
@flask_login.login_required
def create_wallet_transactions(currency):
    user_authentication_details = flask_login.current_user
    user = User.find_by_id(user_authentication_details.user_id)
    wallet = helpers.get_wallet(user, currency)
    response_code = HTTPStatus.CREATED

    if type(wallet) is str:
        response = wallet
        response_code = HTTPStatus.BAD_REQUEST
    else:
        try:
            response = TransactionCreate.call(wallet, request.json).as_dict()
        except InvalidTransaction:
            response = 'Invalid transaction. Please change transaction details.'
            response_code = HTTPStatus.BAD_REQUEST

    return jsonify(response), response_code
