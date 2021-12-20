import os
import hashlib
from PrivateClasses.Database import Database


class UserManagement:
    def __init__(self):
        self.database = Database()

    @staticmethod
    def hash_password(clear_password):
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', clear_password.encode('utf-8'), salt, 100000)
        hash = salt + key
        return hash

    @staticmethod
    def check(payload, clear_password):
        salt_from_storage = payload['password_hash'][:32]  # 32 is the length of the salt
        key_from_storage = payload['password_hash'][32:]

        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            clear_password.encode('utf-8'),  # Convert the password to bytes
            salt_from_storage,
            100000
        )

        if new_key == key_from_storage:
            return True
        return False

    def add(self, session_user=None, username=None, admin=None, clear_password=None):
        # Check parameters
        if not all([x for x in [session_user, username, admin, clear_password] if x is None]):
            return {'status': False, 'message': 'Missing parameter'}

        # Check minimal password length
        if len(clear_password) < 7:
            return {'status': False, 'message': 'Password too short'}

        # Add user
        with self.database:
            response = self.database.user_add(session_user=session_user,
                                              username=username,
                                              password_hash=self.hash_password(clear_password),
                                              admin=admin)
        return response

    def delete(self, session_user=None, username=None):
        # Check parameters
        if not all([x for x in [session_user, username] if x is None]):
            return {'status': False, 'message': 'Missing parameter'}

        # Delete user
        with self.database:
            response = self.database.user_del(session_user=session_user, username=username)
        return response

    def password(self, session_user=None, clear_password=None):
        if not all([x for x in [session_user, clear_password] if x is None]):
            return {'status': False, 'message': 'Missing parameter'}

        with self.database:
            response = self.database.user_set_password(session_user=session_user,
                                                       password_hash=self.hash_password(clear_password))
        return response

    def admin_rights(self, session_user=None, username=None, admin=None):
        with self.database:
            response = self.database.user_set_admin(session_user=session_user, username=username, admin=admin)
        return response

    def set_token(self, session_user=None, token=None):
        with self.database:
            response = self.database.user_set_token(session_user=session_user, token=token)
        return response

    def list_user(self, username=None):
        with self.database:
            response = self.database.user_query(username=username)
        return response

    def list_users(self):
        with self.database:
            response = self.database.users_query()
        return response
