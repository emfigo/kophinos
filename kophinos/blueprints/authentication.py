from flask import Blueprint, request, jsonify
import flask_login
from http import HTTPStatus

from kophinos.models.user_authentication_detail import UserAuthenticationDetail

authentication = Blueprint('authentication', __name__)


@authentication.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    pswd = request.json.get('password')

    user_authentication_details = UserAuthenticationDetail.find_by_email_and_password(
        email,
        pswd
    )

    if user_authentication_details:
        user_authentication_details.generate_token()
        flask_login.login_user(user_authentication_details)
    else:
        return jsonify('The user details are incorrect. Please try new ones.'), HTTPStatus.UNAUTHORIZED

    return jsonify(user_authentication_details.token), HTTPStatus.CREATED

@authentication.route('/logout')
def logout():
    token = None
    headers = request.headers

    if headers.get('Authorization'):
        token = headers['Authorization'].split()[-1]

    user_authentication_detail = UserAuthenticationDetail.find_by_token(token)

    if user_authentication_detail is not None:
        user_authentication_detail.clear_token()
    else:
        return jsonify('Invalid user'), HTTPStatus.BAD_REQUEST

    flask_login.logout_user()

    return jsonify('Logged out'), HTTPStatus.OK
