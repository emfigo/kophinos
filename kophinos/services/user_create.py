from kophinos.models.user import User
from kophinos.models.user_authentication_detail import UserAuthenticationDetail

class UserCreate:
    def __init__(self, first_name: str, last_name: str, email: str, pswd: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.pswd = pswd

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
    def call(kls, first_name: str, last_name: str, email: str, pswd: str):
        service = UserCreate(first_name, last_name, email, pswd)

        user = service.create_user()

        return service.create_user_authentication_detail(user)
