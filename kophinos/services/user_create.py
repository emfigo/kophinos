from kophinos.exceptions import InvalidUser
from kophinos.models.user import User
from kophinos.models.user_authentication_detail import UserAuthenticationDetail

class UserCreate:
    MANDATORY_FIELDS = [
        'first_name',
        'last_name',
        'email',
        'password'
    ]

    def __init__(self, first_name: str, last_name: str, email: str, password: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.pswd = password

    def create_user(self):
        user = User.find_by_email(self.email)

        if user is None:
            user = User.create(self.first_name, self.last_name, self.email)

        return user

    def create_user_authentication_detail(self, user):
        user_authentication_detail = UserAuthenticationDetail.find_by_email_and_password(self.email, self.pswd)

        if user_authentication_detail is None:
            user_authentication_detail = UserAuthenticationDetail.create(
               user, self.email, self.pswd
            )

        return user_authentication_detail

    @classmethod
    def call(kls, details):
        service = UserCreate(**kls._slice(details))

        user = service.create_user()

        return service.create_user_authentication_detail(user)

    @classmethod
    def _slice(kls, details: dict) -> dict:
        sliced_details = {}

        for k in kls.MANDATORY_FIELDS:
            if details.get(k) is not None:
                sliced_details[k] = details[k]
            else:
                raise InvalidUser

        return sliced_details

