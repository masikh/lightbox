import Configuration
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from PrivateClasses.UserManagement import UserManagement


class Token:
    def __init__(self, username=None):
        self.username = username

    def generate_auth_token(self, expiration=1200):
        s = Serializer(Configuration.global_parameters['app'].config['SECRET_KEY'], expires_in=expiration)
        token = s.dumps({'id': self.username})
        UserManagement().set_token(session_user=self.username, token=token)
        return token

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(Configuration.global_parameters['app'].config['SECRET_KEY'])
        try:
            data = s.loads(token)
            result = UserManagement().list_user(data['id'])
            return result['message']['username']
        except (SignatureExpired, BadSignature, Exception):
            return None  # valid token (but expired), invalid token or generic exception
