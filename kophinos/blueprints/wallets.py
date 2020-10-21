from flask import Blueprint, request, jsonify
import flask_login
from http import HTTPStatus

from kophinos.exceptions import InvalidCurrency
from kophinos.models.user import User
from kophinos.models.currency import Currency
from kophinos.models.wallet import Wallet
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
