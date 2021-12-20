import Configuration
import socket
import time
import tinytuya
import threading
from collections import deque
from PrivateClasses.FuzzyWuzzy import FuzzyWuzzy
from tuya_iot import TuyaOpenAPI


class TuYA:
    def __init__(self):
        self.debug = False
        self.database = Configuration.global_parameters['database']
        self.threads = {}
        self.target = dict()
        self.mood_profile = None
        self.tuya_devices = self.get_devices()

        self.tuya_credentials = self.get_tuya_credentials()
        self.password = self.tuya_credentials['password']
        self.username = self.tuya_credentials['username']
        self.country_code = self.tuya_credentials['country_code']
        self.access_id = self.tuya_credentials['access_id']
        self.access_key = self.tuya_credentials['access_key']

        self.schema = 'tuyaSmart'
        self.end_point = 'https://openapi.tuyaeu.com'
        self.openapi = None
        self.uid = None
        threading.Thread(target=self.connect_to_openapi).start()
        self.delay = 0
        self.color_rotator_thread = threading.Thread(target=self.color_rotator)
        self.color_rotator_thread.start()

    def connect_to_openapi(self):
        initialized = False
        while not initialized:
            try:
                self.tuya_credentials = self.get_tuya_credentials()
                self.password = self.tuya_credentials['password']
                self.username = self.tuya_credentials['username']
                self.country_code = self.tuya_credentials['country_code']
                self.access_id = self.tuya_credentials['access_id']
                self.access_key = self.tuya_credentials['access_key']

                self.schema = 'tuyaSmart'
                self.end_point = 'https://openapi.tuyaeu.com'

                self.openapi = TuyaOpenAPI(self.end_point, self.access_id, self.access_key)
                self.openapi.connect(self.username, self.password, self.country_code, self.schema)
                self.uid = self.openapi.token_info.uid
                initialized = True
                print('Successfully connected to openAPI', flush=True)
            except AttributeError:
                print('Caught error connecting to openAPI', flush=True)
                time.sleep(1)

    def get_tuya_credentials(self):
        result = self.database.get_tuya_credentials()
        if result is not None:
            return result
        else:
            result = {
                'password': '',
                'username': '',
                'country_code': 31,
                'access_id': '',
                'access_key': ''
            }
            return result

    def scan_devices(self):
        if self.uid is None:
            return
        online_data = self.openapi.get('/v1.0/users/{uid}/devices'.format(uid=self.uid))
        local_data = tinytuya.deviceScan()

        # Merge results
        for i in range(len(online_data['result'])):
            online_data['result'][i]['icon'] = 'https://images.tuyaeu.com/{icon}'.format(icon=online_data['result'][i]['icon'])

            # Check if device supports colour
            online_data['result'][i]['colour'] = False
            for state in online_data['result'][i]['status']:
                try:
                    if 'colour' in state['code'] or 'colour' in state['value']:
                        online_data['result'][i]['colour'] = True
                except:
                    pass

            for ip_address in local_data:
                if local_data[ip_address]['gwId'] == online_data['result'][i]['id']:
                    online_data['result'][i]['local_ip'] = local_data[ip_address]['ip']
                    online_data['result'][i]['active'] = local_data[ip_address]['active']
                    online_data['result'][i]['ablilty'] = local_data[ip_address]['ablilty']
                    online_data['result'][i]['encrypt'] = local_data[ip_address]['encrypt']
                    online_data['result'][i]['productKey'] = local_data[ip_address]['productKey']
                    online_data['result'][i]['version'] = local_data[ip_address]['version']

        # save devices to database
        self.database.set_tuya_devices(online_data['result'])

        # Update in memory device list
        return self.get_devices()

    def get_devices(self):
        devices = self.database.get_tuya_devices(object_id=True)
        for device in devices:
            # device new device object...
            device_object = {
                'device': device,
                'queue': deque(maxlen=1),
                'thread': None
            }

            # Cleanup before storting...
            if device['id'] in self.threads and self.threads[device['id']]['thread'] is not None:
                self.threads[device['id']]['thread'].do_run = False
                self.threads[device['id']] = None

            # Start and register new device
            thread = threading.Thread(target=self.spawn_thread, args=[device_object])
            thread.start()
            device_object['thread'] = thread
            self.threads[str(device['_id'])] = device_object
        return devices

    def spawn_thread(self, device_object):
        current_thread = threading.current_thread()
        while getattr(current_thread, "do_run", True):
            try:
                device_queue = device_object['queue']
                device = device_object['device']
                d = tinytuya.BulbDevice(device['id'], device['local_ip'], local_key=device['local_key'])
                d.set_version(float(device['version']))
                d.set_socketPersistent(True)
                d.set_socketNODELAY(True)
                d.set_socketRetryLimit(10)
                d.set_socketTimeout(0.3)
                d.turn_on()
                has_changed = False
                last_change = time.time()
                data = None
                if 'last_setting' in device:
                    device_queue.append(device['last_setting'])

                while getattr(current_thread, "do_run", True):
                    if len(device_queue) > 0:
                        data = device_queue.pop()
                        has_changed = True
                        last_change = time.time()
                        if data['set_colour'] is True:
                            if data['colour'] == '#000000':
                                d.turn_off()
                            else:
                                d.turn_on()

                            hex_color = data['colour'].lstrip('#')
                            color = tuple(int(hex_color[i: i+2], 16) for i in (0, 2, 4))
                            d.set_mode('colour')
                            d.set_colour(color[0], color[1], color[2])
                        else:
                            if data['brightness'] == 0:
                                d.turn_off()
                            else:
                                d.turn_on()

                            d.set_mode('white')
                            result = d.set_white_percentage(brightness=data['brightness'], colourtemp=data['colourtemp'])

                    time.sleep(0.01)
                    if has_changed is True and time.time() - last_change > 5:
                        device['last_setting'] = data
                        self.database.set_tuya_devices([device])
                        has_changed = False
            except Exception as error:
                print('caught error in spawn_thread: {error}'.format(error=error), flush=True)
                time.sleep(1)

    @staticmethod
    def is_bulb_online(server: str, port: int, timeout=1):
        """ping server"""
        try:
            socket.setdefaulttimeout(timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((server, port))
        except Exception as error:
            return False
        else:
            s.close()
            return True

    def get_bulb_color(self, device, result=None, index=0):
        if result is None:
            result = {}

        if 'local_ip' in device and self.is_bulb_online(device['local_ip'], 6668):
            d = tinytuya.BulbDevice(device['id'], device['local_ip'], local_key=device['local_key'])
            d.set_version(float(device['version']))
            status = d.status()
            state = d.state()

            # Convert colour code
            hex_colour = '#000000'
            if state['mode'] == 'colour':
                (r, g, b) = d._hexvalue_to_rgb(state['colour'], d.bulb_type)
                hex_colour = "#{0:02x}{1:02x}{2:02x}".format(r, g, b)
        else:
            hex_colour = '#000000'
            state = {'brightness': 0, 'colourtemp': 0, 'mode': 'white'}
            status = {'dps': {'20': False}}

        result[index] = {'status': status, 'state': state, 'colour': hex_colour}
        return result[index]

    def set_color_profile(self, mood):
        mood['selected'] = True
        self.database.set_tuya_mood_profile(mood)

    def set_mood(self, mood):
        # We might get the mood via google speech recognition, let us try to find the closest match...
        mood_profiles = self.database.get_tuya_mood_profiles()
        best_matched_mood = FuzzyWuzzy(mood, [x['name'] for x in mood_profiles]).compare()

        if best_matched_mood is not None:
            self.mood_profile = self.database.get_tuya_mood_profile(best_matched_mood)
            if self.mood_profile is not None:
                for key in self.threads:
                    if key in self.mood_profile['profile']:
                        self.threads[key]['queue'].append(self.mood_profile['profile'][key])

            return {
                'status': True,
                'result': 'Mood changed to {best_matched_mood}'.format(best_matched_mood=best_matched_mood)
            }

        return {'status': False, 'result': 'Undefined mood'}

    def get_tuya_mood_profiles(self):
        result = self.database.get_tuya_mood_profiles()
        return result

    def get_set_default_mood_profile(self, name=None):
        result = self.database.get_set_default_mood_profile(name)
        return result

    def delete_tuya_mood_profile(self, name):
        result = self.database.delete_tuya_mood_profile(name)
        return result

    def get_chromecast_device(self):
        result = self.database.get_chromecast()
        return result

    def set_colour_rotation_speed(self, data):
        self.delay = data['colour_rotation_speed']
        self.database.set_colour_rotation_speed(data)

    @staticmethod
    def rotate(li, x):
        return li[-x % len(li):] + li[:-x % len(li)]

    def set_rotation_lists(self):
        result = self.database.get_set_light_groups()
        lists = list()
        for group in result['light_groups']:
            group_colours = list()
            group_threads = list()
            for child in group['children']:
                device = self.database.get_tuya_device_by_name(child)
                if device['colour'] is True:
                    group_colours.append(self.mood_profile['profile'][str(device['_id'])])
                    group_threads.append(str(device['_id']))
            lists.append({'group_colours': group_colours, 'group_threads': group_threads})
        return lists

    def color_rotator(self):
        self.delay = 0
        current_mood = ''
        colour_lists = list()
        current_thread = threading.current_thread()
        now = time.time()
        while getattr(current_thread, "do_run", True):
            try:
                if self.mood_profile is None:
                    time.sleep(0.1)
                else:
                    # Check if rotation speed has changed in mood profile
                    if round(time.time(), 1) % 0.5 == 0:
                        self.mood_profile = self.database.get_tuya_mood_profile(self.mood_profile['name'])
                        self.delay = self.mood_profile['colour_rotation_speed']

                    if current_mood != self.mood_profile['name']:
                        current_mood = self.mood_profile['name']
                        colour_lists = self.set_rotation_lists()
                        now = time.time() + self.delay

                    elif self.delay != 0 and time.time() - now > self.delay:
                        now = time.time()
                        for i in range(0, len(colour_lists), 1):
                            colour_lists[i]['group_colours'] = self.rotate(colour_lists[i]['group_colours'], 1)
                            for j in range(0, len(colour_lists[i]['group_colours']), 1):
                                colours = colour_lists[i]['group_colours'][j]
                                key = colour_lists[i]['group_threads'][j]
                                self.threads[key]['queue'].append(colours)
                    else:
                        time.sleep(0.1)
            except Exception as error:
                print(error)