from flask import Blueprint, request, jsonify
import flask_login
from http import HTTPStatus

from kophinos.exceptions import InvalidUser
from kophinos.services.user_create import UserCreate
from kophinos.models.user import User
from kophinos.models.user_authentication_detail import UserAuthenticationDetail
from kophinos.models.wallet import Wallet

users = Blueprint('users', __name__)


@users.route('/users', methods=['POST'])
def create():
    try:
        user_authentication_details = UserCreate.call(request.json)
    except InvalidUser:
        return jsonify('The user details are incorrect. Please try new ones.'), HTTPStatus.BAD_REQUEST

    return jsonify(user_authentication_details.as_dict()), HTTPStatus.CREATED

@users.route('/users/wallets')
@flask_login.login_required
def wallets():
    user_authentication_details = flask_login.current_user
    user = User.find_by_id(user_authentication_details.user_id)

    wallets = [ wallet.as_dict() for wallet in Wallet.find_all_by_user(user) ]

    return jsonify(wallets), HTTPStatus.OK

