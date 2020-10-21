from flask import Blueprint, request, jsonify
import flask_login
from http import HTTPStatus

from kophinos.exceptions import InvalidCurrency, InvalidTransaction
from kophinos.models.user import User
from kophinos.models.currency import Currency
from kophinos.models.transaction import Transaction
from kophinos.models.wallet import Wallet
from kophinos.services.transaction_create import TransactionCreate
from kophinos.services.wallet_create import WalletCreate

wallets = Blueprint('wallets', __name__)

@wallets.route('/wallets/<currency>')
@flask_login.login_required
def get_wallet(currency):
    user_authentication_details = flask_login.current_user
    user = User.find_by_id(user_authentication_details.user_id)
    try:
        currency = Currency.get(currency)
    except InvalidCurrency:
        return jsonify('Invalid currency. Please select specify another one.'), HTTPStatus.BAD_REQUEST

    wallet = Wallet.find_by_user_and_currency(user, currency)

    if wallet is None:
        return jsonify('Invalid account. Account does not exist for user.'), HTTPStatus.BAD_REQUEST

    return jsonify(wallet.as_dict()), HTTPStatus.OK

@wallets.route('/wallets/<currency>/transactions')
@flask_login.login_required
def get_wallet_transactions(currency):
    user_authentication_details = flask_login.current_user
    user = User.find_by_id(user_authentication_details.user_id)
    try:
        currency = Currency.get(currency)
    except InvalidCurrency:
        return jsonify('Invalid currency. Please select specify another one.'), HTTPStatus.BAD_REQUEST

    wallet = Wallet.find_by_user_and_currency(user, currency)

    if wallet is None:
        return jsonify('Invalid account. Account does not exist for user.'), HTTPStatus.BAD_REQUEST

    transactions = [ transaction.as_dict() for transaction in Transaction.find_all_by_wallet(wallet) ]

    return jsonify(transactions), HTTPStatus.OK

@wallets.route('/wallets', methods=['POST'])
@flask_login.login_required
def create_wallet():
    user_authentication_details = flask_login.current_user
    details = request.json

    try:
        currency = Currency.get(details.get('currency'))
    except InvalidCurrency:
        return jsonify('Invalid currency. Please select specify another one.'), HTTPStatus.BAD_REQUEST

    wallet = WalletCreate.call(user_authentication_details.token, details)

    return jsonify(wallet.as_dict()), HTTPStatus.CREATED

@wallets.route('/wallets/<currency>/transactions', methods=['POST'])
@flask_login.login_required
def create_wallet_transactions(currency):
    user_authentication_details = flask_login.current_user
    user = User.find_by_id(user_authentication_details.user_id)
    try:
        currency = Currency.get(currency)
    except InvalidCurrency:
        return jsonify('Invalid currency. Please select specify another one.'), HTTPStatus.BAD_REQUEST

    wallet = Wallet.find_by_user_and_currency(user, currency)

    if wallet is None:
        return jsonify('Invalid account. Account does not exist for user.'), HTTPStatus.BAD_REQUEST

    try:
        transaction = TransactionCreate.call(wallet, request.json)
    except InvalidTransaction:
        return jsonify('Invalid transaction. Please change transaction details.'), HTTPStatus.BAD_REQUEST

    return jsonify(transaction.as_dict()), HTTPStatus.CREATED
