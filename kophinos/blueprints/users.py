from flask import Blueprint, request, jsonify
from http import HTTPStatus

from kophinos.exceptions import InvalidUser
from kophinos.services.user_create import UserCreate

users = Blueprint('users', __name__)


@users.route('/users', methods=['POST'])
def create():
    try:
        user_authentication_details = UserCreate.call(request.json)
    except InvalidUser:
        return jsonify('The user details are incorrect. Please try new ones.'), HTTPStatus.BAD_REQUEST

    return jsonify(user_authentication_details.as_dict()), HTTPStatus.CREATED

