from Configuration import environment
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError


class Database:
    def __init__(self):
        self.settings = environment['database']
        self.client = None
        self.database = None

    def __enter__(self):
        self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    """ Connect to db and create collections if they don't exist and set access rights
    """
    def connect(self):
        try:
            self.client = MongoClient(self.settings['hostname'],
                                      username=self.settings['username'],
                                      password=self.settings['password'],
                                      authSource='admin',
                                      authMechanism='SCRAM-SHA-1')

            # Check if db has been initialized before
            db_list = self.client.list_database_names()
            self.database = self.client[self.settings['db_name']]
            if self.settings['db_name'] not in db_list:
                from PrivateClasses.UserManagement import UserManagement
                default_credentials = {'username': 'admin', 'password_hash': UserManagement().hash_password('admin'), 'admin': True}
                self.database['users'].insert_one(default_credentials)
        except OperationFailure as error:
            print('Caught error in Database.connect(): {error}'.format(error=error), flush=True)
            self.disconnect()

    """ Disconnect from database
    """
    def disconnect(self):
        try:
            self.client.close()
        except ServerSelectionTimeoutError:
            pass
        except OperationFailure:
            pass
        except TypeError:
            pass
        except AttributeError:
            pass
        self.database = None
        self.client = None

    """ Users management
    """

    def user_add(self, session_user=None, username=None, password_hash=None, admin=None):
        # Missing parameter? Bailout.
        if not all([x for x in [session_user, username, password_hash, admin] if x is None]):
            return {'status': False, 'message': 'Missing parameter'}

        # Check if user is admin
        if self.database.users.find_one({'username': session_user, 'admin': True}) is None:
            return {'status': False, 'message': 'Insufficient access rights'}

        # Does this user exist?
        user = self.database.users.find_one({'username': username})
        if user is None:
            self.database.users.insert_one({'username': username, 'password_hash': password_hash, 'admin': admin})
            return {'status': True, 'message': 'User {username} created'.format(username=username)}
        return {'status': False, 'message': 'User already exist'}

    def user_del(self, session_user=None, username=None):
        # Missing parameter? Bailout.
        if not all([x for x in [session_user, username] if x is None]):
            return {'status': False, 'message': 'Missing parameter'}

        # Check if user is admin or actual user
        if self.database.users.find_one({'username': session_user, 'admin': True}) is None:
            return {'status': False, 'message': 'Insufficient access rights'}

        # Does this user exist?
        user = self.database.users.find_one({'username': username})
        if user is None:
            return {'status': False, 'message': 'No such user'}

        # Is this the last admin user?
        elif user['admin'] is True and self.database.users.find({'admin': True}).count() == 1:
            return {'status': False, 'message': 'Refused to delete last admin user'}

        # Remove the user
        else:
            self.database.users.delete_one({'username': username})
            return {'status': True, 'message': 'User {username} deleted'.format(username=username)}

    def user_set_password(self, session_user=None, password_hash=None):
        # Missing parameter? Bailout.
        if not all([x for x in [session_user, password_hash] if x is None]):
            return {'status': False, 'message': 'Missing parameter'}

        # Update the user
        self.database.users.update_one({'username': session_user}, {'$set': {'password_hash': password_hash}})
        return {'status': True, 'message': 'Password for {username} changed'.format(username=session_user)}

    def user_set_admin(self, session_user=None, username=None, admin=None):
        # Missing parameter? Bailout.
        if not all([x for x in [session_user, username, admin] if x is None]):
            return {'status': False, 'message': 'Missing parameter'}

        # Only allow admin users to make changes
        if self.database.users.find_one({'username': session_user, 'admin': True}) is None:
            return {'status': False, 'message': 'Insufficient access rights'}

        # If we're the last admin, bailout, we don't like to fall out of the tree!
        if self.database.users.find({'admin': True}).count() == 1 and admin is False:
            return {'status': False, 'message': 'Refused to delete last admin user'}

        # Update the user
        self.database.users.update_one({'username': username}, {'$set': {'admin': admin}})
        return {'status': False,
                'message': 'Access for {username} set to: {admin}'.format(username=username,
                                                                          admin='admin' if admin is True else 'user')}

    def user_set_token(self, session_user=None, token=None):
        if not all([x for x in [session_user, token] if x is None]):
            return {'status': False, 'message': 'Missing parameter'}

        user = self.database.users.find_one({'username': session_user})
        # Does this user exist?
        if user is None:
            return {'status': False, 'message': 'No such user'}
        else:
            self.database.users.update_one({'username': session_user}, {'$set': {'token': token}})
            return {'status': True, 'message': 'Token updated'}

    def user_query(self, username=None):
        # Missing parameter? Bailout.
        if not all([x for x in [username] if x is None]):
            return {'status': False, 'message': 'Missing parameter'}

        # Query this user
        user = self.database.users.find_one({'username': username}, {'_id': False})
        if user is None:
            return {'status': False, 'message': 'No such user'}
        return {'status': True, 'message': user}

    def users_query(self):
        return {'status': True,
                'message': list(self.database.users.find({},
                                                         {'_id': False,
                                                          'token': False,
                                                          'password_hash': False}))}

    """ get/set tuya credentials
    """

    def set_tuya_credentials(self, credentials):
        result = self.database.tuya_credentials.find_one({})
        if result is None:
            self.database.tuya_credentials.insert_one(credentials)
        else:
            self.database.tuya_credentials.update_one(result, {'$set': credentials}, upsert=True)

    def get_tuya_credentials(self):
        result = self.database.tuya_credentials.find_one({}, {'_id': False})
        return result

    def get_chromecast(self):
        result = self.database.tuya_credentials.find_one({}, {'chromecast': True})
        if result is not None:
            return result['chromecast']
        return None

    """ get/set tuya devices
    """

    def set_tuya_devices(self, devices):
        for device in devices:
            result = self.database.tuya_devices.find_one({'id': device['id']})
            if result is None:
                device['last_setting'] = {
                    "colour": "#000000",
                    "brightness": 50,
                    "colourtemp": 50,
                    "set_colour": False
                }
                self.database.tuya_devices.insert_one(device)
            else:
                if 'last_setting' in result:
                    device['last_setting'] = result['last_setting']
                self.database.tuya_devices.update_one(result, {'$set': device}, upsert=True)

    def set_tuya_device_last_setting(self, last_setting, device_id):
        try:
            self.database.tuya_devices.update_one({'id': device_id},
                                                  {
                                                      '$set': {
                                                          'last_setting': {
                                                              'colour': last_setting['colour'],
                                                              'brightness': last_setting['brightness'],
                                                              'colourtemp': last_setting['colourtemp'],
                                                              'set_colour': last_setting['set_colour'],
                                                              'is_on': last_setting['is_on']
                                                          }
                                                      }
                                                  })
        except Exception as error:
            pass

    def get_tuya_devices(self, object_id=False):
        if object_id is False:
            result = list(self.database.tuya_devices.find({}).sort('name'))
            for i in range(0, len(result), 1):
                result[i]['_id'] = str(result[i]['_id'])
        else:
            result = list(self.database.tuya_devices.find({}).sort('name'))
        return result

    def get_tuya_device_by_name(self, name):
        return self.database.tuya_devices.find_one({'name': name})

    """ get/set tuya color profiles (moods)
    """

    def set_colour_rotation_speed(self, data):
        profile = self.get_tuya_mood_profile(data['mood'])
        profile['colour_rotation_speed'] = data['colour_rotation_speed']
        self.set_tuya_mood_profile(profile)

    def get_tuya_mood_profiles(self):
        result = list(self.database.tuya_mood_profiles.find({}).sort('name'))
        return result

    def get_tuya_mood_profile(self, name):
        result = self.database.tuya_mood_profiles.find_one({'name': name})
        return result

    def set_tuya_mood_profile(self, profile):
        if profile['name'] != '':
            profile.pop('_id', None)
            result = self.database.tuya_mood_profiles.find_one({'name': profile['name']})
            if result is None:
                self.database.tuya_mood_profiles.insert_one(profile)
            else:
                self.database.tuya_mood_profiles.update_one(result, {'$set': profile}, upsert=True)

    def delete_tuya_mood_profile(self, name):
        self.database.tuya_mood_profiles.delete_one({'name': name})
        result = self.database.tuya_mood_profile_default.find_one({})
        if result is not None:
            self.database.tuya_mood_profile_default.delete_one({'_id': result['_id']})
            return 'profile deleted'
        return 'no such profile'

    def get_set_default_mood_profile(self, name=None):
        if name is not None:
            result = self.database.tuya_mood_profile_default.find_one({})
            if result is None:
                self.database.tuya_mood_profile_default.insert_one({'default': name})
            else:
                self.database.tuya_mood_profile_default.update_one(result, {'$set': {'default': name}}, upsert=True)
        else:
            result = self.database.tuya_mood_profile_default.find_one({})
            if result is not None:
                name = str(result['default'])

        return name

    """ get/set tuya Light groups (moods)
    """

    def get_set_light_groups(self, light_groups=None):
        devices = list(self.database.tuya_devices.find({}))
        available_devices_names = [x['name'] for x in devices]
        if light_groups is not None:
            result = self.database.light_groups.find_one({})
            if result is None:
                self.database.light_groups.insert_one(light_groups)
            else:
                self.database.light_groups.update_one(result, {'$set': light_groups}, upsert=True)
        else:
            light_groups = self.database.light_groups.find_one({}, {'_id': False})
            if light_groups is None:
                light_groups = {'light_groups': []}

        for group in light_groups['light_groups']:
            for light in group['children']:
                if light in available_devices_names:
                    available_devices_names.remove(light)

        return {'unassigned_lights': available_devices_names, 'light_groups': light_groups['light_groups']}
